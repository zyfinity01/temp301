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


Simulation software to create mock SDI-12/rainfall data and send it to the azure cloud IoT Hub backend.
See iotc-test.py for testing communication to Azure IoT Central
"""

import configargparse
import time
import random
import paho.mqtt.client as mqtt
import ssl
import json


def on_connect(client, userdata, flags, rc):
    print("Device connected with result code: " + str(rc))


def on_disconnect(client, userdata, rc):
    print("Device disconnected with result code: " + str(rc))


def on_publish(client, userdata, mid):
    print("Device sent message")


def generate_reading():
    """
    Generate a random reading in csv form of:
    device_id,device_type,voltage,reading
    :returns string
    """
    voltage = 12 + random.uniform(-1, 1)

    reading = (
        random.gauss(10, 1)
        if options.device_type == "sdi-12"
        else int(random.gauss(5, 2))
    )

    if options.format == "csv":
        return "{0},{1},{2:.2f},{3:.2f}".format(
            options.device_id, options.device_type, voltage, reading
        )

    elif options.format == "json":
        message = {
            "id": options.device_id,
            "type": options.device_type,
            "voltage": "{0:.2f}".format(voltage),
            "reading": "{0:.2f}".format(reading),
        }
        return json.dumps(message)
    raise ValueError("invalid format type")


def main():
    client = mqtt.Client(
        client_id=options.device_id, clean_session=True, protocol=mqtt.MQTTv311
    )
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    client.username_pw_set(
        username="{0}.azure-devices.net/{1}/?api-version=2018-06-30".format(
            options.hub_name, options.device_id
        ),
        # TODO: replace this with x.509 certs as an auth method rather than using sas tokens
        password=options.sas_token,
    )
    client.tls_set(
        ca_certs="digiCert-root.crt",
        certfile=None,
        keyfile=None,
        tls_version=ssl.PROTOCOL_TLSv1_2,
        ciphers=None,
    )
    client.tls_insecure_set(False)

    connected = client.connect(
        host="{0}.azure-devices.net".format(options.hub_name), port=options.port
    )

    topic = "devices/{0}/messages/events/".format(options.device_id)
    print(
        "Generating/sending events for {0} every {1} seconds".format(
            options.device_id, options.wait_time
        )
    )
    client.loop_start()
    while True:
        try:
            reading = generate_reading()
            print("Generated sensor reading: " + reading)

            published = client.publish(topic, reading, qos=1)
            time.sleep(options.wait_time)
        except KeyboardInterrupt:
            client.loop_stop()
            print("Exiting.")
            break


if __name__ == "__main__":
    parser = configargparse.ArgParser(default_config_files=["device.conf"])
    parser.add_argument("-c", "--config", is_config_file=True, help="config file path")
    parser.add_argument(
        "--wait-time",
        default=3,
        type=int,
        help="seconds to wait after sending message",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose mode")
    parser.add_argument(
        "--device-type",
        choices=["rainfall", "sdi-12"],
        default="sdi-12",
        help="type of device",
    )
    parser.add_argument(
        "-n", "--device-id", required=True, help="device id in azure IoT Hub"
    )
    parser.add_argument(
        "-p", "--port", default=8883, type=int, help="Cloud endpoint port"
    )
    parser.add_argument(
        "-r",
        "--region",
        required=True,
        help="Device region identifier (eg: upper-hutt)",
    )
    parser.add_argument(
        "--hub-name",
        required=True,
        help="IoT Hub Identifier (without .azure-device.net)",
    )
    parser.add_argument(
        "-s", "--sas-token", required=True, help="Azure IoT SAS Token (temporary)"
    )
    parser.add_argument(
        "-f", "--format", default="json", choices=["json", "csv"], help="Message format"
    )

    options = parser.parse_args()
    print(parser.format_values())
    main()
