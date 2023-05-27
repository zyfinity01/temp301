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


Low level code for SDI-12
"""

import logging
import time
from micropython import const
from machine import Pin
from machine import UART

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
import asyn

SLEEP = const(0)
WAKE = const(1)
RX_DIR = const(1)
TX_DIR = const(0)
RX_TIMEOUT = const(500)  # milliseconds
UART_ENCODING = "utf-8"

# Define Rev::4.0 connections from ESP32 GPIO to the SDI-12 module,
# shown on the ESP32_board schematic, as constants
#
SDI_DIR = const(21)  # IO21 (physical pin 33)
SDI_RX = const(39)  # IO39 (physical pin 5)
SDI_TX = const(22)  # IO22 (physical pin 36)
SDI_EN = const(2)  # IO2 (physical pin 24)
SDI_FOUT = const(25)  # IO25 (physical pin 10)

ADDR_QUERY_CMD = "?!"  # Can be sent with run_unaddressed_command() to query addresses of connected sensors

log = logging.getLogger("sdi12")
# Enable the following to set a log level specific to this module:
# log.setLevel(logging.DEBUG)


def init_sdi() -> dict:
    """
    Creates an SDI-12 structure which contains the pins needed to communicate
    with the sensors.

    The returned dict contains the keys:
    - uart: the UART driver
    - dir_: the direction control pin
    - force_out: the pin to force the output high
    - en: the sensor wake pin
    - lock: an asynchronous lock to prevent concurrent access to the SDI line

    Returns:
        dict: The SDI-12 structure.
    """

    sdi = {
        "uart": UART(
            2,
            baudrate=1200,
            bits=7,
            parity=0,
            stop=1,
            timeout_char=62,
            tx=SDI_TX,
            rx=SDI_RX,
        ),
        "dir_": Pin(SDI_DIR, mode=Pin.OUT),
        "force_out": Pin(SDI_FOUT, mode=Pin.OUT),
        "en": Pin(SDI_EN, mode=Pin.OUT),
        "lock": asyn.Lock(),
    }
    # make sure the sensors are asleep by default
    sdi["en"].value(SLEEP)

    return sdi


def turn_on_sensors(sdi: dict) -> int:
    """Powers/wakes the sensors.

    Use the return argument to ensure that the sensor being accessed has fully booted up.

    Args:
        sdi (dict): The SDI-12 structure.

    Returns:
        int: the time that the sensor was woken
    """
    if sdi["en"].value() == WAKE:
        log.warning("Sensor already on")
        return 0

    log.info("Booting all sensors")
    sdi["en"].value(WAKE)
    return time.time()


def turn_off_sensors(sdi: dict):
    """Turn off all sensors.

    Args:
        sdi (dict): The SDI-12 structure.
    """
    # check if sensors are already off
    if sdi["en"].value() == SLEEP:
        log.warning("Sensor already off")
        return

    log.info("Turning off all sensors")
    sdi["en"].value(SLEEP)


async def read_sensor(
    sensor: dict, sdi: dict, time_booted: int, crc=False, name: str = None
) -> dict:
    """
    Retrieve, parse and return SDI-12 reading as dict

    Args:
        sensor (dict): The information for the SDI-12 sensor being started.
        time_booted (int): The time the sensor started up.
        sdi (dict): The SDI-12 structure.
        crc (bool, optional): Set to True to enable error checking. Not yet implemented. Defaults to False.
        name (str, optional): The name of the sensor. Defaults to the sensor address if not specified.

    Returns:
        dict: The fully parsed sensor data. This contains ont the data that the user is interested in (based on the contents of the sensor dict).

    Raises:
        ValueError: If the returned address is incorrect.
        ValueError: If the response from the measure command was invalid.
        TypeError: If the sensor returns no reading. This normally indicates some other unexpected issue.
        RuntimeError: If the sensor doesn't reply (or is unable to reply).
    """
    try:
        response = await measure(sensor, sdi, time_booted, crc, name)
    except RuntimeError as e:
        log.error("RuntimeError: {0}".format(e))
        raise RuntimeError("Unable to take measurement reading")

    # get the middle 3 digits (time taken to take measurement)
    try:
        measure_time = int(response[1:4])
        num_values = int(response[4])
    # this shouldn't happen, but do it just to be sure
    except ValueError:
        # log the error and then return None
        raise ValueError(
            "Sensor returned invalid reading. Connection to sensor may be faulty."
        )
    except TypeError:
        # This error should never actually happen. If it does, operation will continue as normal (by raising exception), but we log a critical error.
        log.critical(
            "Measurement reading returned no reading to the read_sensor function. This should never happen."
        )
        raise TypeError("Sensor returned no reading. Address may be incorrect.")

    # don't allow other SDI-12 sensors to run during this wait time
    async with sdi["lock"]:
        await asyncio.sleep(measure_time)

    # strip the sensor data
    sensor_index = _readings_to_indices(sensor)

    # get the minimum of either the number of values or max reading index
    max_index = min(num_values, max(sensor_index))

    # get all responses, up to max_index
    all_responses = await deep_data_reading(sensor, sdi, max_index, time_booted)

    # filter out unneeded responses
    filtered_responses = _filter_responses(all_responses, sensor_index)
    # apply span and zero offset adjustments
    scaled_responses = _apply_adjustments(filtered_responses, sensor)
    return scaled_responses


async def run_command(command: str, sdi: dict, wake_time: int = 0) -> str:
    """Run any command. Should be used with the webapp monitor.

    Any command can be run, even invalid ones. The only requirement is that they must begin with an address and end with an exclamation mark.

    The sensors must be powered before sending a command, which needs to be done outside of this function, ideally while the webapp is active. There is no check to ensure enough time has passed, so this is up to the user.

    Args:
        command (str): The command to be send by the user.
        sdi (dict): The SDI-12 structure.
        wake_time (int): The time the sensor started up.

    Returns:
        str: The raw response from the sensor.

    Raises:
        ValueError: If the command was not valid.
        RuntimeError: If the sensor is not powered.
    """
    # Check sensor is on. Do not handle exception here as this should be done when the webapp is started (or at a similar time)
    _check_sensor_state(sdi)
    # Check command is formatted correctly and return string to print to terminal if not
    if not (command[0].isalpha() or command[0].isdigit() or command.startswith("?")):
        raise ValueError("Command address must be 0-9, A-Z, or a-z")
    if not command.endswith("!"):
        raise ValueError("Command must end with !")

    # Select a short wait time. It is up to the user to make sure they don't do this to early.
    sensor = {"bootup_time": 5}

    return await _send_cmd(command, sensor, sdi, wake_time)


def run_unaddressed_command(command: str, sdi: dict) -> str:
    """
    Run any command, and does not require an address unlike run_command(). Can be used to query addresses of all sensors, which nessecitates no address being sent. Will also turn on all the sensors.

    Args:
        command (str): the command to be sent/
        sdi (dict): The SDI-12 structure.
    Returns:
        str: The raw response from the sensor.
    """
    # Wakes all sensors
    _wake_sensors(sdi)
    # Sets direction to transmitting
    sdi["dir_"](TX_DIR)
    uart = sdi["uart"]
    # Clears the buffer
    uart.read()
    # Sends the command
    uart.write(command)
    # Waits for the command to send
    time.sleep_us(8333 * len(command))
    # Reads the response
    r = uart.read()
    return r1


def _wake_sensors(sdi: dict):
    """Send a break/mark sequence to wake all connected sensors so they are ready to receive data. This should be used before sending a command.

    Args:
        sdi (dict): The SDI-12 structure.
    """
    # send break
    sdi["force_out"](0)
    sdi["dir_"](TX_DIR)
    time.sleep_us(25000)
    # send mark
    sdi["force_out"](1)
    time.sleep_us(8333)


def _check_sensor_state(sdi: dict):
    """Check if sensors are ready to send. If this function returns False, the program MUST not attempt to send any data.

    Args:
        sdi (dict): The SDI-12 structure.

    Raises:
        RuntimeError: If the sensor is not awake.
    """
    if sdi["en"].value() == SLEEP:
        raise RuntimeError("Sensor is currently asleep and shouldn't be accessed.")


async def _check_ready_time(sensor: dict, wake_time: int):
    """Check if the sensor has booted.

    If the sensor hasn't booted, asynchronously wait for it to start.

    Args:
        sensor (dict): The information for the SDI-12 sensor being started.
        wake_time (int): The time the sensor started up.
    """
    time_until_ready = wake_time + sensor["bootup_time"] - time.time()
    # if equal to 0, sleep anyway to give a bit of leeway
    if time_until_ready >= 0:
        log.info(
            "Waiting {0} seconds for sensor to be ready".format(time_until_ready + 1)
        )
        # add 1 so if time_until_ready == 0, it doesn't perform a "round-robin"
        await asyncio.sleep(time_until_ready + 1)


async def _send_cmd(cmd: str, sensor: dict, sdi: dict, wake_time: int) -> str:
    """Send a command to all the sensors. Return the response or None if something fails.

    Args:
        cmd (str): The command string. This must begin with the address and end with an exclamation mark. The command is assumed to be valid, so it should be validated beforehand.
        sensor (dict): The sensor information.
        sdi (dict): The SDI-12 structure.
        wake_time (int): The time that the sensors were booted up.

    Returns:
        str: The raw response from the command formatted as a string. If the command is invalid or the sensor wasn't on, this will raise an exception.

    Raises:
        RuntimeError: If the sensor is not turned on.
        RuntimeError: If no response is received from the sensor or if it is invalid.
    """

    _check_sensor_state(sdi)

    # check if sensor is ready to be read, otherwise wait
    await _check_ready_time(sensor, wake_time)

    async with sdi["lock"]:
        uart = sdi["uart"]
        response = None
        attempts = 0
        while not response and attempts < 3:
            # Wake up all sensors
            _wake_sensors(sdi)
            # Send command
            uart.write(cmd)
            # Sleep for enough time to fully send command (each byte takes ~8.3 ms)
            time.sleep_us(8333 * len(cmd))
            # Switch to receive mode
            sdi["dir_"](RX_DIR)
            # Clear the receive buffer
            log.debug("Clearing buffer: {}".format(uart.read()))

            # Sensor should wait some period of time, which increases for each attempt
            timeout_end = time.ticks_ms() + RX_TIMEOUT * (attempts + 1)
            while not uart.any():
                # Check timeout
                if time.ticks_diff(timeout_end, time.ticks_ms()) < 0:
                    break
                # Run other tasks every 50ms while waiting
                await asyncio.sleep_ms(50)

            # If successful response, take reading
            read_string = uart.read()

            try:
                if read_string == b"\x00":
                    raise RuntimeError("No bytes received by sensor")
                # Attempt to convert the response to a string
                response = str(read_string, UART_ENCODING)
            except UnicodeError:
                # Log an error if the string couldn't be formatted
                log.error("Could not format sensor string: {}".format(read_string))
            except TypeError:
                # Log an error if there was no response from the sensor
                log.error("No response returned by sensor")
            except RuntimeError as e:
                log.error("RuntimeError: {0}".format(e))
            else:
                # If no exceptions, return the data
                log.info("Read data from SDI12: {}".format(read_string))
                return response
            # This branch will only be reached in the event of an exception. Decrease the remaining attempts and retry
            attempts += 1
            # Take a nap before trying again
            await asyncio.sleep_ms(50)

        # If no more attempts remain, raise a RuntimeError
        raise RuntimeError(
            "Sensor did not return response, or the response couldn't be formatted correctly."
        )


def _parse_sensor_data(response: str, crc: bool = False) -> list:
    """Split the recorded data returned by the sensor.

    This involves removing the address, splitting at (and keeping) plus or minus signs, and removing carriage return and linefeed characters.

    Args:
        response (str): The response from the sensor that needs to be formatted. Should follow the regex `[0-9A-Za-z]([+-](\d+(\.\d+)?))+`
        crc (bool, optional): Set to True to enable error checking. Not yet implemented. Defaults to False.

    Returns:
        list: A list containing the split data.
    """
    start_indices = [i for i, x in enumerate(response) if x == "+" or x == "-"]
    # -2 to remove <CR><LF> (\r\n)
    start_indices.append(len(response) - 2)
    response_list = [
        float(response[start_indices[i] : start_indices[i + 1]])
        for i in range(len(start_indices) - 1)
    ]
    return response_list


def _check_addr(response: str, addr: str):
    """Check that the response was from the intended address.

    Args:
        response (str): The response received from the sensor.
        addr (str): The address that the response *should have* come from.

    Raises:
        ValueError: If the address in the response is invalid.
    """
    # Convert to strings just in case
    if str(response[0]) != str(addr):
        log.debug(
            "Received response from sensor {0}. Expected sensor {1}".format(
                response[0], addr
            )
        )
        return False

    return True


def _readings_to_indices(sensor: dict) -> tuple:
    """Extracts just the indices of the readings for easier parsing.

    Args:
        readings (dict): The sensor information.

    Returns:
        tuple: Stripped sensor information containing just the reading name and its index.
    """
    readings = sensor["readings"]
    return tuple([reading["index"] for reading in readings])


def _filter_responses(responses: list, measure_id_index: tuple) -> tuple:
    """Filter the responses that the user requested and map them to the name of the sensor.

    Args:
        responses (list): The parsed responses from the sensor
        measure_id_index (tuple): The stripped sensor information. This must be run through _readings_to_indices first.

    Returns:
        tuple: The responses that the user requested with the reading name as the key.
    """
    return tuple(
        [responses[index - 1] for index in measure_id_index if index <= len(responses)]
    )


def _apply_adjustments(responses: tuple, sensor: dict) -> tuple:
    """Apply multiplier (span) and offset (zero) adjustments to the received data.

    The multiplier is applied first, followed by the offset.

    Args:
        responses (tuple): The responses from the sensor with the name of the reading as the key. They must be filtered beforehand using _filter_responses.
        sensor (dict): The sensor information.

    Returns:
        tuple: The readings with any adjustments applied. The readings are mapped with the reading name as the key.
    """
    readings = sensor["readings"]
    return tuple(
        [
            response * readings[index]["multiplier"] + readings[index]["offset"]
            for index, response in enumerate(responses)
        ]
    )


async def measure(sensor: dict, sdi: dict, wake_time: int, crc: bool, name: str) -> str:
    """Send a measure command (aM!). Optionally, send an error checking measurement command instead (aMC!).

    Args:
        sensor (dict): The sensor information.
        sdi (dict): The SDI-12 structure.
        wake_time (int): The time the sensor was woken.
        crc (bool): Set to True to enable error checking. Not yet implemented.
        name (str): The name of the sensor.

    Returns:
        str: The raw response from the sensor. This will be of the form atttn, where a is the address, ttt is the time to take the measurement, and n is the number of responses.

    Raises:
        ValueError: If the returned address is incorrect.
        RuntimeError: If the sensor doesn't reply (or is unable to reply).
    """
    addr = sensor["address"]

    log.info("Reading sensor: {0}".format(name if name else addr))

    response = await _send_cmd(
        "{0}M{1}!".format(addr, "C" if crc else ""), sensor, sdi, wake_time
    )

    # verify that the response was from the correct address
    attemp = 0
    while not _check_addr(response, addr) and attemp < 3:
        attemp = attemp + 1
        response = await _send_cmd(
            "{0}M{1}!".format(addr, "C" if crc else ""), sensor, sdi, wake_time
        )

    return response


async def deep_data_reading(
    sensor: dict, sdi: dict, max_index: int, wake_time: int
) -> list:
    """Read all the data from a sensor.

    This will send as many aDn! commands as required until there is no more data to read, or when max_index is reached.

    Args:
        sensor (dict): The sensor information.
        sdi (dict): The SDI-12 structure.
        max_index (int): The index of the last reading the user wants.
        wake_time (int): The time that the sensor was woken.

    Returns:
        list: All the data from the sensor, up to max_index or the last reading, whichever comes first.

    Raises:
        ValueError: If the returned address is incorrect.
        RuntimeError: If the sensor doesn't reply (or is unable to reply).
    """
    # read response
    reading_index = 0
    data_index = 0
    addr = sensor["address"]
    full_responses = []

    # Set up command with address, but leave index out (hence, {{0}})
    read_cmd = "{0}D{{0}}!".format(addr)

    while reading_index < max_index:
        response = await _send_cmd(read_cmd.format(data_index), sensor, sdi, wake_time)

        attemp = 0
        while not _check_addr(response, addr) and attemp < 3:
            attemp = attemp + 1
            response = await _send_cmd(
                read_cmd.format(data_index), sensor, sdi, wake_time
            )

        response_list = _parse_sensor_data(response)
        # If no response received log an error. This really shouldn't happen.
        if not response_list:
            log.critical(
                "No response received at index {0}. The program should never enter this branch.".format(
                    reading_index
                )
            )
            raise RuntimeError("No response received from sensor")
        # Add all responses to a list
        full_responses.extend(response_list)
        # Increment the index of the response read
        reading_index += len(response_list)
        # Increment the index of the D command
        data_index += 1
        await asyncio.sleep(0)

    return full_responses
