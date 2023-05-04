#!/usr/bin/env python3
"""
Copyright (C) 2023  Benjamin Secker, Jolon Behrent, Louis Li, James Quilty

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.


Subscribe to a MQTT topic and publish to another service via an HTTP API.
"""

import os
import sys
import json
import argparse
import logging
import traceback
from datetime import datetime
import requests
import paho.mqtt.client as mqtt

MQTT_BROKER = "test.mosquitto.org"
MQTT_TOPIC = "test/environmentMonitoring/"
MQTT_SUBSCRIBER = f"MQTT subscriber on {os.uname()[1]}"
GWRC_FAVICON = "https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://gw.govt.nz&size=16"


# Callbacks
def cb_connect(client, userdata, flags, return_code):
    """
    paho-mqtt callback function. See the documentation and example code in
    <https://pypi.org/project/paho-mqtt/> and
    <https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php>.
    """
    log = logging.getLogger(__name__)
    log.info("Connected with code %d. Press CTRL+C to exit.", return_code)
    # Subscribe Topic
    topic = f"{userdata.base_topic}{userdata.topic}"
    client.subscribe(topic)

    post_mattermost(
        f"Subscribed to topic `{topic}` "
        f"on MQTT broker [{userdata.broker}]({userdata.broker}).",
    )


def cb_message(client, userdata, msg):
    """
    paho-mqtt callback function. See the documentation and example code in
    <https://pypi.org/project/paho-mqtt/> and
    <https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php>.
    """
    log = logging.getLogger(__name__)
    msg_payload = msg.payload.decode("utf-8")
    try:
        log.debug("Received MQTT message with payload: %s", msg_payload)
        readings = json.loads(msg_payload)
    except Exception as exception:
        log.exception("Message %s generated an exception:", msg_payload)
        post_mattermost(
            f"**Caught Exception:** {str(exception)}.\n"
            f"The MQTT message was: `{msg_payload}`.\n"
            f"```python\n{traceback.format_exc()}\n```",
        )
    else:
        log.info("%s", readings)
        text = (
            f"**{readings['DateTime']}**  "
            f"Temperature: {readings['temperature']} ; "
            f"Pressure: {readings['pressure']} ; "
            f"Bucket Tips: {readings['rainfall']}."
        )
        post_mattermost(text, userdata.topic + " via MQTT", GWRC_FAVICON)
        post_mmy(readings)
        # # Post to Microsoft Power BI
        # requests.post(REST_API_URL, msg.payload)


def post_mattermost(text, username=MQTT_SUBSCRIBER, icon_url=""):
    """
    Post to Mattermost channel ENGR489: Environmental Monitoring Alerts
    """
    mattermost_webhook = (
        "https://mattermost.ecs.vuw.ac.nz/hooks/6hwshmgj1bdu8k5rajakurz9oe"
    )
    payload = {"username": username, "icon_url": icon_url, "text": text}
    return requests.post(mattermost_webhook, json=payload)


def post_mmy(data: dict):
    """
    Post to Monitor My Watershed vuw_test site
    """
    resp = requests.post(
        "http://data.envirodiy.org/api/data-stream/",
        json={
            "sampling_feature": "c9b1d92e-d52b-454a-a294-e2ca7736eb3b",
            "timestamp": f"{data['DateTime']}+12:00",
            "66019fe3-6e8e-4143-bbf8-f7acbc131829": data["temperature"],
            "2c9bdb88-622c-43e2-a844-5c80e041bf36": (0.2 * data["rainfall"]),
        },
        headers={
            "TOKEN": "97f38860-679f-4a0e-9196-6a6f473bbc84",
            "Content-Type": "application/json",
        },
    )
    return resp


def parse_arguments():
    """
    Parse the command-line arguments
    """

    parser = argparse.ArgumentParser(description="Subscribes to an MQTT topic.")

    parser.add_argument(
        "--debug",
        action="store_true",
        help="provide additional detail about script execution.",
    )

    parser.add_argument(
        "--silent",
        action="store_true",
        help="disables console output.",
    )

    parser.add_argument(
        "--log",
        action="store_true",
        help=(
            "write log to a file, automatically created in a "
            "'logs' directory in the same directory as the script."
        ),
    )

    parser.add_argument(
        "--broker",
        type=str,
        default=MQTT_BROKER,
        help="full host and domain name of the MQTT broker.",
    )

    parser.add_argument(
        "--base-topic",
        type=str,
        default=MQTT_TOPIC,
        help="the base topic string to which the final topic level, "
        "typically the data recorder name, is added; must end in '/'.",
    )

    parser.add_argument(
        "topic",
        type=str,
        help="name of the MQTT topic, typically the data recorder name.",
    )

    return parser.parse_args()


def setup_logger(args):
    """
    Sets up logging to file and console with a named logger.

    Returns: a Logger object corresponding to the named logger.
    """

    # Create the logger
    #
    # Need to set the logger level to be commensurate with the handler levels,
    # i.e. <= the minimum handler level otherwise low-level messages will not
    # be passed to the handlers!
    #
    # At the moment, set to minimum level, but will probably want to set the
    # log level to min(console-log-level, file-log-level, ..)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if args.log:

        # Set up the log file parameters
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_name = os.path.splitext(os.path.basename(__file__))[0]
        log_dir = os.path.join(script_dir, "logs")
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        # datestamp: Could use ISO 8601 format (YYYY-mm-ddTHH:MM:SS) but
        # colons are illegal in filenames. Compromise for readability:
        datestamp = datetime.now().strftime("%Y-%m-%d-%H%M")

        # Create the handlers and add to the logger
        logfile = logging.FileHandler(
            filename=os.path.join(log_dir, f"{script_name}-{datestamp}.log"),
            mode="w",
            encoding="utf-8",
            errors=None,
        )
        logfile.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                style="%",
            )
        )
        logfile.setLevel(logging.DEBUG if args.debug else logging.INFO)
        logger.addHandler(logfile)  # add the file as a handler

    if not args.silent:
        # Would like to avoid the use of print statements, so use logging
        # instead to log to multiple destinations. See:
        # <https://docs.python.org/3/howto/logging-cookbook.html#logging-to-multiple-destinations>
        #
        # Define a Handler which writes INFO messages or higher to sys.stdout
        console = logging.StreamHandler(stream=sys.stdout)
        console.setLevel(logging.INFO)
        # set a format which is simpler for console use and tell the handler to use this format
        console.setFormatter(logging.Formatter("%(message)s"))
        # add the handler to the logger
        logger.addHandler(console)

    return logger


# =======================================================================
# ENTRY POINT
# =======================================================================
#
def main():
    """
    Configure the MQTT client then poll the broker at the specified
    period until the process is terminated.
    """

    args = parse_arguments()

    log = setup_logger(args)

    # Create an MQTT client instance and configure the callback
    # functions prior to connecting to the specified broker.
    client = mqtt.Client()
    client.on_connect = cb_connect
    client.on_message = cb_message
    client.user_data_set(args)
    # To log debug messages from paho-mqtt, use the following:
    # client.enable_logger(log)
    client.connect(args.broker, 1883, 60)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        log.info("Halting on user request.")
        post_mattermost(
            "Halting on user request; disconnecting from broker.",
        )
    except Exception as exception:
        log.exception("Caught Exception:")
        post_mattermost(
            f"**Caught Exception:** {str(exception)}.\n" f"Disconnecting from broker.",
        )
    finally:
        log.info("Disconnecting from broker.")
        client.disconnect()


if __name__ == "__main__":
    main()
