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


Executed on startup directly after boot.py
"""
import sys

# Change the module search order by modifying `sys.path`. The entry
# `""` specifies frozen bytecode. By moving this entry to the end
# of `sys.path`, frozen files will only be found if there is no
# match found in the filesystem.
# In the future this manipulation can be avoided by baking the
# `lib/` directory into the firmware.
if len(sys.path) > 0 and sys.path[0] == "":
    sys.path.append(sys.path.pop(0))

import logging

# threading module is used to enable concurent execution of the time synchronizing process, by creating a seperate thread for the sync task. Thus, code can keep running other tasks without sync to complete. Hence, the device will stay responsive
import threading

# importing rtc(Real time clock) from drivers for needed functions in time module
from drivers import rtc as rtc_driver

# Set global log level
# logging._level = logging.INFO
logging._level = logging.DEBUG

# Set Production status: affects display of development and console-only messages
# PRODUCTION = True
PRODUCTION = False

log = logging.getLogger("main")
# Enable the following to set a log level specific to this module:
# log.setLevel(logging.DEBUG)

log.info("Data Recorder booting...")

# TRACE-level debugging only:
# log.debug("Importing sdcard driver and mounting the card")
from drivers import sdcard as sdcard_driver

sdcard_driver.setup()

# uPy imports
# TRACE-level debugging only:
# log.debug("Importing uPy modules")
import machine
import esp32
from machine import Pin, deepsleep
from micropython import const, alloc_emergency_exception_buf

# lib imports
# TRACE-level debugging only:
# log.debug("Importing libraries")
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
import asyn
from aswitch import Pushbutton

import utime as time
import json

# code imports
# TRACE-level debugging only:
# log.debug("Importing drivers/services")
# from drivers import sdcard as sdcard_driver  # imported first-thing
from drivers import counter as counter_driver

from services import config as config_services
from services import sdi12 as sdi12_services
from services import scheduler as scheduler_services
from services import wlan as wlan_services

from util.time import isoformat
from util.buildinfo import log_build_info
from util import helpers

# TRACE-level debugging only:
# log.debug("Completed module and library imports")

# RGB LED pin connections
LED_RED_PIN = const(32)  # ESP32 GPIO 32 (physical pin 8)
LED_GREEN_PIN = const(33)  # ESP32 GPIO 33 (physical pin 9)
LED_BLUE_PIN = None  # Not connected in Rev::4.0; see #508.

# Time constants in seconds
DEEP_SLEEP_WAIT_PERIOD = 3
FIVE_MINUTES = 300
SIXTY_MINUTES = 3600

# Time constants in milliseconds
DEEP_SLEEP_PERIOD = 60000
SERVER_STOP_WAIT_PERIOD = 5000

# Recovery constants
RECOVERY_TRANSMISSION_COUNT = 3
MAX_RETRANSMIT_CACHE_SIZE = 1000 * 1000


# Allocate emergency ISR buffer - https://docs.micropython.org/en/latest/reference/isr_rules.html
alloc_emergency_exception_buf(100)

button_pin = Pin(14, Pin.IN, Pin.PULL_DOWN)
esp32.wake_on_ext0(pin=button_pin, level=esp32.WAKEUP_ALL_LOW)


async def start_server(server):
    """
    Coroutine to start the webserver
    Args:
        server: webserver object
    """
    server.run()


async def all_shutdown():
    await asyncio.sleep(1)


def deep_sleep(sensors: dict):
    """
    Go into deep sleep

    Args:
        sensors (dict): sensor objects to calculate sleep time for
    """
    sleep_time = scheduler_services.calculate_sleep_time(int(time.time()), sensors)
    log.info(
        "Entering deep sleep for {0} s ({1:.2g} minutes)".format(
            sleep_time, (sleep_time / 60)
        )
    )
    deepsleep((1000 * sleep_time) + 500)


async def stop_server(server, sensors):
    """
    Stop the server and go back into deep sleep after a short delay.

    This method is a callback for the sleep button

    Args:
        server: webserver object to be shut down gracefully
        sensors (dict): sensor objects to pass to deep_sleep()
    """
    set_client()
    # !!! It is uncertain why the following 5-second delay was inserted,
    # !!! initially in commit 25465623 to !111 via #193. It _may_ be necessary
    # !!! for the Tinyweb server to shut down cleanly. Defer removal until its
    # !!! function is understood.
    log.info(
        "Stopping the web server and entering deep sleep in {0} s".format(
            SERVER_STOP_WAIT_PERIOD / 1000
        )
    )
    await asyncio.sleep_ms(SERVER_STOP_WAIT_PERIOD)
    server.stop()
    deep_sleep(sensors)


def sync_time(modem):
    """Function to calibrate local time using modem or external RTC"""
    rtc = rtc_driver.rtc()

    def sync_rtc():  # new function that encapsulates existing time function and is designed to run on a seperate thread
        while True:
            try:
                current_timezone = (
                    time.timezone // 3600
                )  # Get the current timezone in hours
                if current_timezone == 12:
                    if modem.has_network:
                        network_time = modem.get_network_time()
                        time_start = time.ticks_ms()
                        network_mktime = time.mktime(network_time)
                        internal_RTC_offset = (
                            time.mktime(rtc.get_local_time()) - network_mktime
                        )
                        external_RTC_offset = (
                            time.mktime(rtc.get_ex_rtc_time()) - network_mktime
                        )
                        print("Internal RTC offset {:+d} s".format(internal_RTC_offset))
                        if abs(internal_RTC_offset) > 1:
                            rtc.set_local_time(network_time)
                            print("Synchronized internal RTC with network time")
                        print("External RTC offset {:+d} s".format(external_RTC_offset))
                        if abs(external_RTC_offset) > 1:
                            rtc.set_ex_rtc_time(network_time)
                            print("Synchronized external RTC with network time")
                    else:
                        print("Synchronizing time with external RTC module")
                        internal_RTC_offset = time.mktime(
                            rtc.get_local_time()
                        ) - time.mktime(rtc.get_ex_rtc_time())
                        print(
                            "Internal RTC offset from external RTC module {:+d} s".format(
                                internal_RTC_offset
                            )
                        )
                        if abs(internal_RTC_offset) > 0:
                            rtc.sync_rtc_time()
                else:
                    print("Device timezone is not set to UTC+12")
            except OSError:
                print("Failed to set time (OSError)")

            # Sleep for 1 hour before running the synchronization again
            time.sleep(3600)

    # Create a thread to run the synchronization process
    sync_thread = threading.Thread(target=sync_rtc)
    sync_thread.daemon = True  # Allow the program to exit even if the thread is running
    sync_thread.start()


def set_client():
    """Save new MQTT client profile"""
    log.info("Saving new MQTT client profile")
    from services import config
    from drivers import modem as modem_driver

    modem = modem_driver.Modem()
    modem.initialise()
    device_config = config.read_config_file()
    client_id = device_config["mqtt_settings"]["username"]
    server = device_config["mqtt_settings"]["host"]
    modem.mqtt_reset()
    modem.mqtt_set_client(client_id, server)
    modem.http_connect(modem_driver.MATTERMOST_SERVER)  # Modem connects to mattermost
    modem.power_off()


import asyncio


def regular_mode(device_config=None, device_data=None):
    """
    Enter Regular Mode.

    Regular mode is the usual, low-power mode of the device. It wakes up, gets an SDI-12 reading,
    Transmits the reading if it can and then goes back into deep sleep.

    Args:
        device_config (dict): device configuration dictionary
    """
    current_time = time.time()
    log.info("Entering Regular Mode")

    # Turn on red LED while in Regular Mode
    Pin(LED_RED_PIN, Pin.OUT, value=0)

    # Fetch device configuration if not provided
    device_config = device_config or config_services.read_config_file()
    # Fetch device data if not provided
    device_data = device_data or config_services.read_data_file()

    # Create a Counter object
    rain_counter = counter_driver.Counter()
    rainfall = rain_counter.get_rainfall()

    # Check schedule (if raining change interval to 5 minutes else 60 minutes)
    interval_minutes = 5 if rainfall > 0 else 60
    interval_seconds = interval_minutes * 60

    # Append rainfall and current time to device data
    device_data["rainfall"].append(rainfall)
    device_data["date_time"].append(current_time)

    # Determine if transmission should occur based on schedule
    should_transmit = scheduler_services.should_transmit(
        current_time,
        device_data["last_transmitted"],
        device_config["send_interval"] * interval_seconds,
    )

    if should_transmit:
        # Run the pipeline asynchronously to transmit data
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(pipeline(device_config, device_data, current_time))
        except (RuntimeError, TypeError, ValueError) as e:
            if not device_config["test_mode"]:
                # Log the error and handle exceptions
                log.critical("An error occurred in the pipeline: {0}".format(e))
                if not PRODUCTION:
                    try:
                        # Provide an opportunity to cancel deep sleep
                        print(
                            "\nDeep sleeping in {0} seconds.".format(
                                DEEP_SLEEP_WAIT_PERIOD
                            )
                        )
                        print(
                            "Press Ctrl-C to exit to the MicroPython interactive shell instead.\n"
                        )
                        time.sleep(DEEP_SLEEP_WAIT_PERIOD)
                    except KeyboardInterrupt:
                        # Prompt user with options upon interruption
                        print("Enter `regular_mode()` to take a sensor reading.")
                        print("Enter `configure_mode()` to start the webserver.")
                        print(
                            "Enter `deepsleep(ms)` to deep sleep for `ms` milliseconds.\n"
                        )
                        sys.exit()
                log.info(
                    "Entering deep sleep for {0} ms ({1:.2g} minutes)".format(
                        DEEP_SLEEP_PERIOD, (DEEP_SLEEP_PERIOD / 1000) / 60
                    )
                )
                deepsleep(DEEP_SLEEP_PERIOD)
    else:
        # Turn off red LED
        Pin(LED_RED_PIN, Pin.IN, None)
        if not PRODUCTION:
            try:
                # Provide an opportunity to cancel deep sleep
                print("\nDeep sleeping in {0} seconds.".format(DEEP_SLEEP_WAIT_PERIOD))
                print(
                    "Press Ctrl-C to exit to the MicroPython interactive shell instead.\n"
                )
                time.sleep(DEEP_SLEEP_WAIT_PERIOD)
            except KeyboardInterrupt:
                # Prompt user with options upon interruption
                print("Enter `regular_mode()` to take a sensor reading.")
                print("Enter `configure_mode()` to start the webserver.")
                print("Enter `deepsleep(ms)` to deep sleep for `ms` milliseconds.\n")
                sys.exit()

        # Calculate sleep time based on schedule and available sensors
        sleep_time = scheduler_services.calculate_sleep_time(
            int(time.time()), config_services.get_sensors(device_config)
        )
        log.info(
            "Entering deep sleep for {0} s ({1:.2g} minutes)".format(
                sleep_time, (sleep_time / 60)
            )
        )
        deepsleep((1000 * sleep_time) + 500)


async def pipeline(device_config: dict, device_data: dict, current_time: int):
    """
    Run the regular-mode pipeline of steps from reading data to sending it.

    Args:
        device_config (dict): device configuration dictionary
    """
    from drivers import sdi12 as sdi12_driver
    from drivers import modem as modem_driver

    # Code moved from regular_mode() #650 to here to enable testing
    # Set last send time
    device_data["last_transmitted"] = current_time
    config_services.write_data_file(device_data)
    # Enable the following debug statement only when troubleshooting
    log.debug("Set last_transmitted {:d}".format(current_time))

    modem = modem_driver.Modem()
    modem.initialise()
    sync_time(modem)
    # Initialise SDI-12 UART
    sdi = sdi12_driver.init_sdi(1)
    # Enable the following debug statement only when troubleshooting
    # SDI-12 driver problems:
    # log.debug("SDI-12 Driver: {0}".format(sdi))

    # From here, we use asyn.Gather so that we can boot the modem, take a reading
    # from the sensors and then continue once everything has finished.

    # list of tasks to execute asynchronously
    tasks = []

    # turn on the sensors
    sensors = config_services.get_sensors(device_config)

    # filter sensors to ones that are "enabled"
    sensors_filtered = {name: data for name, data in sensors.items() if data["enabled"]}
    wake_time = time.time()

    log.debug("Wake time (seconds since epoch): {0}".format(wake_time))

    # read sensorspro
    # TODO filter out sensors that aren't scheduled to be read
    names, gatherables = sdi12_services.gather_sensors(sdi, sensors_filtered, wake_time)
    tasks.extend(gatherables)

    # # Add sensors to tasks
    log.info("Running tasks...")
    sensor_reading_time = time.time()
    task_results = await asyn.Gather(tasks)

    sensor_results = [
        {"name": name, "readings": readings}
        for name, readings in zip(names, task_results)
    ]
    log.debug("Sensor results: {0}".format(sensor_results))

    # map readings tuple to dict
    sensor_mapped_results = [
        {
            "name": result["name"],
            "readings": sdi12_services.convert_readings(
                result["readings"],
                config_services.get_sensor(device_config, result["name"]),
            ),
        }
        for result in sensor_results
    ]

    log.debug(sensor_mapped_results)

    # Merge results from all sensors
    sensor_merged_results = {}
    for d in [sensor["readings"] for sensor in sensor_mapped_results]:
        for k, v in d.items():
            if k in sensor_merged_results:
                log.warning("{0} already in dict and will be overwritten".format(k))
            sensor_merged_results[k] = v
    log.info("Merged readings from all sensors: {0}".format(sensor_merged_results))

    # Add time information
    sensor_merged_results["DateTime"] = sensor_reading_time

    # Log to SD Card
    sdcard_driver.save_telemetry(sensor_merged_results)

    # Convert Datetime to ISO8601 compliant string
    sensor_merged_results["DateTime"] = isoformat(sensor_merged_results["DateTime"])

    rainfall_data = 0
    for i in device_data["rainfall"]:
        rainfall_data += i

    # Add rainfall data
    sensor_merged_results["rainfall"] = rainfall_data

    json_result = json.dumps(sensor_merged_results)

    # Start transmit
    # don't transmit failed transmissions if the initial transmission fails
    if transmit(
        device_data,
        device_config,
        modem,
        json_result,
    ):
        # attempt to transmit some failed transmissions
        for itt in range(RECOVERY_TRANSMISSION_COUNT):
            # if the file is too big
            if (
                helpers.get_file_size(
                    sdcard_driver.REQUEUE_FILE + sdcard_driver.FILETYPE
                )
                > MAX_RETRANSMIT_CACHE_SIZE
            ):
                log.warning(
                    "Transmission cache full! Transmissions will have to be read manually!\n\t"
                )
                break

            # get failed transmission if any are remaining
            failed_transmission = sdcard_driver.read_failed_transmission()
            if failed_transmission is None:
                break

            log.debug(
                "Attempting to retransmit transmission:\n\t{}".format(
                    failed_transmission
                )
            )

            # attempt to send the transmission
            if transmit(device_data, device_config, modem, failed_transmission):
                log.debug("Retransmission succeeded!")
                # if the transmission succeeded, it can be removed from the cache
                sdcard_driver.delete_latest_failed_transmission()
    else:
        log.warning("Transmitting failed, saving transmission to sd card")
        # If the transmission fails, send the result to the sd card cache
        sdcard_driver.write_failed_transmission(json_result)

    # Turn off modem
    # For frequent transmissions, e.g. once per minute, the power-on/power-off
    # cycle is taking too long and causing delays - also sometimes it's
    # triggering long delays when, for example, an IP address is not
    # immediately acquired. Place behind a heuristic which leaves the modem on
    # if the sleep time is sufficiently short.
    sleep_time = min(
        DEEP_SLEEP_PERIOD,
        scheduler_services.calculate_sleep_time(int(time.time()), sensors),
    )
    if sleep_time > 60:
        modem.power_off()
    else:
        log.debug("Leaving modem on as sleep time is only {0} s".format(sleep_time))

    # Turn off red LED
    Pin(LED_RED_PIN, Pin.IN, None)

    if not PRODUCTION:
        # Sleep for a few seconds to give an opportunity to cancel deep sleep.
        try:
            # Console-only message, do not write to the log.
            print("\nDeep sleeping in {0} seconds.".format(DEEP_SLEEP_WAIT_PERIOD))
            print(
                "Press Ctrl-C to exit to the MicroPython interactive shell instead.\n"
            )
            time.sleep(DEEP_SLEEP_WAIT_PERIOD)
        except KeyboardInterrupt:
            print("Enter `regular_mode()` to take a sensor reading.")
            print("Enter `configure_mode()` to start the webserver.")
            print("Enter `deepsleep(ms)` to deep sleep for `ms` milliseconds.\n")
            sys.exit()

    if not device_config["test_mode"]:
        # Sleep for enough time to make the next reading
        sleep_time = scheduler_services.calculate_sleep_time(int(time.time()), sensors)
        log.info(
            "Entering deep sleep for {0} s ({1:.2g} minutes)".format(
                sleep_time, (sleep_time / 60)
            )
        )
        deepsleep((sleep_time * 1000) + 500)


def transmit(device_data: dict, device_config: dict, modem, json_result: str):
    """
    Attempts to transmit a given json-encoded data collection to the server.

    Args:
        device_config (dict): device configuration dictionary
        json_result (str): data to be transmitted to the server
        device_data (dict): device data dictionary
        modem: modem to be used to transmit data

    Returns:
        bool: whether the transmission was successful
    """
    if modem.has_serial:
        returnValue = True
        log.info("Start transmitting data...")

        modem.get_signal_power()
        modem.acquire_network()  # Proceed even if an IP address has not been acquired
        # Update the Cellular network RSSI
        # !!! Must be executed _only_ when a transmit is taking place,
        # !!! otherwise the modem will not be instantiated.
        # !!! Which is why it's been move to pipeline()
        device_data["coverage_level"] = (
            "Not known or not detectable"
            if modem.signal_power is None or modem.signal_power == 99
            else int(100 * modem.signal_power / 31)  # 31 is the maximum signal_power
        )
        config_services.write_data_file(device_data)
        if modem.mqtt_connect():
            topic = "{0}/{1}".format(
                device_config["mqtt_settings"]["parent_topic"].rstrip("/"),
                device_config["device_name"],
            )
            modem.mqtt_publish(topic, str(json_result))
            time.sleep(1)
            modem.mqtt_disconnect()
            # Reset rainfall data buffer
            device_data["rainfall"] = []
            device_data["date_time"] = []
            config_services.write_data_file(device_data)
        else:
            log.error("Failed to connect to the MQTT broker")
            returnValue = False

        # If mattermost connected
        if modem.set_http_connection(modem_driver.MATTERMOST_SERVER):

            modem.http_publish_mattermost(str(json_result))
            time.sleep(1)
            # modem.mqtt_disconnect()   not sure if need to disconnect http connection

            # Reset rainfall data buffer
            device_data["rainfall"] = []
            device_data["date_time"] = []
            config_services.write_data_file(device_data)
        else:
            log.error("Failed to connect to Mattermost")
            # Add this line when comfortable it works, or else might screw up everything
            # returnValue = False

        log.info("Modem has no network or no response. No transmission")

    else:
        return False

    return returnValue


from services.webserver import WebServer
from services import config
from drivers import sdi12gi


def configure_mode():
    """
    Enter Configure Mode.

    Spins up a tinyweb server for visualization and configuration of the device.

    """
    log.info("Entering Configure Mode")

    # Read device configuration and data
    device_config = config.read_config_file()
    sensors = config.get_sensors(device_config)
    device_data = config.read_data_file()

    # Start AP mode
    wlan_services.start_ap_mode(ssid="GWRC-{0}".format(device_config["device_id"]))

    # Initialize SDI-12
    sdi = sdi12.init_sdi(0)

    # Disable maintenance mode
    device_config["maintenance_mode"] = False

    log.info("Starting Web Server")
    web_server = WebServer(device_config, device_data, sdi)

    # Initialize button
    button = Pushbutton(button_pin)
    button.long_func(stop_server, args=(web_server, sensors))

    try:
        # Start server and asyncio loop
        loop = asyncio.get_event_loop()
        loop.create_task(start_server(web_server))
        loop.run_forever()
    except KeyboardInterrupt:
        # Stop server and enter deep sleep
        log.info(
            "Stopping Web Server and entering deep sleep in {0} s".format(
                SERVER_STOP_WAIT_PERIOD / 1000
            )
        )
        time.sleep_ms(SERVER_STOP_WAIT_PERIOD)
        web_server.stop()
        print("")
        print("Enter `regular_mode()` to take a sensor reading.")
        print("Enter `configure_mode()` to start the webserver.")
        print("Enter `deepsleep(ms)` to deep sleep for `ms` milliseconds.\n")
        return  # don't deep sleep

    # Unreachable code block
    # stop_server() executes deep_sleep(sensors) as its final statement,
    # halting code execution prior to reaching this point
    #
    # TODO: if the device was supposed to read during configure mode, do regular mode instead of deep sleeping
    # If can't get the event loop to cooperate, just make it sleep for 0 seconds to do a reboot
    deep_sleep(sensors)


if __name__ == "__main__":
    # Assign machine.wake_reason() to a variable to avoid polling it more than
    # once. Note that the defined constants
    # <https://docs.micropython.org/en/latest/library/machine.html#machine-constants>
    # have significant overlap in their numeric values:
    #
    # IRQ Wake Values
    # machine.IDLE = Undefined
    # machine.SLEEP = 2
    # machine.DEEPSLEEP = 4
    #
    # Reset Causes
    # machine.PWRON_RESET = 1
    # machine.HARD_RESET = 2
    # machine.WDT_RESET = 3
    # machine.DEEPSLEEP_RESET = 4
    # machine.SOFT_RESET = 5
    #
    # Wake-up Reasons
    # machine.WLAN_WAKE = Undefined
    # machine.PIN_WAKE = 2
    # machine.RTC_WAKE = Undefined
    wake_reason = machine.wake_reason()
    reset_cause = machine.reset_cause()
    log.debug("machine.wake_reason(): {0}".format(wake_reason))
    log.debug("machine.reset_cause(): {0}".format(reset_cause))
    if wake_reason == machine.DEEPSLEEP:
        # Woken from RTC, so enter "Regular Mode"
        regular_mode()

    elif wake_reason == machine.PIN_WAKE:
        # Woken from pushbutton, so enter "Configure Mode"
        configure_mode()

    else:
        # Must be first power-up. Initialise rain gauge counter and
        # synchronise the on-board RTC with the network time.
        log_build_info()

        log.info("Initialising rain gauge counter")
        rain_counter = counter_driver.Counter()
        rain_counter.initialise()

        log.info("Connecting to the modem")
        from drivers import modem as modem_driver

        modem = modem_driver.Modem()
        modem.initialise()

        sync_time(modem)

        if not PRODUCTION:
            try:
                # Console-only message, do not write to the log
                print(
                    "\nAutomatically entering Regular Mode in {0} seconds.".format(
                        2 * DEEP_SLEEP_WAIT_PERIOD
                    )
                )
                print(
                    "Press Ctrl-C now to exit to the MicroPython interactive shell instead.\n"
                )
                time.sleep(2 * DEEP_SLEEP_WAIT_PERIOD)
            except KeyboardInterrupt:
                print("Enter `regular_mode()` to take a sensor reading.")
                print("Enter `configure_mode()` to start the webserver.")
                print("Enter `deepsleep(ms)` to deep sleep for `ms` milliseconds.\n")
                sys.exit()

        regular_mode()
