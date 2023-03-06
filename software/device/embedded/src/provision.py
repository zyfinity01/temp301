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


This script should be ran after factory production to initially provision the device.

It performs the following functions:
 - Sets up certs for x509 authentication to the cloud backend
 - creates default configure and data json files
 - generates a lookup table
"""
import logging
from drivers import sdcard
from drivers import modem as modem_driver
from drivers import rtc as rtc_driver
import lib.textfx as textfx
from services.config import CONFIG_FILE, DYNAMIC_DATA_FILE, TEST_CONFIG_FILE

log = logging.getLogger("provision")
# Enable the following to set a log level specific to this module:
# log.setLevel(logging.DEBUG)


def modem_setup():
    # auto baud
    modem = modem_driver.Modem()
    modem.autobaud()
    modem.set_network()
    if modem.initialise():
        return True

    return False


def _validate_input(
    message: str,
    class_: type,
    min_value: class_ = None,
    max_value: class_ = None,
    valid_values: list = None,
    allow_exit: bool = False,
    default_value: class_ = None,
):
    """Requests an input from the user and validates it.

    Args:
        message (str): The message to display to the user to request the input.
        class_ (type): The expected class of the response. For example: int, float, str.
        min_value (class_, optional): The minimum input value. Must be of type class_. Defaults to None.
        max_value (class_, optional): The maximum input value. Must be of type class_. Defaults to None.
        valid_values (list, optional): List of valid values. If the value is only accepted if it is included in this list. If min and max bounds are specified, at least one value in this list must be within those bounds. Defaults to None.
        allow_exit (bool, optional): Whether the input can be empty. If set to true, the function will return None if nothing is entered. Defaults to False.
        default_value (class_, optional): The value to return if no input is provided. Only works if allow_exit is True. Defaults to None.

    Raises:
        ValueError: If min_value is greater than max_value.
        ValueError: If all values in valid_values are out of min/max bounds.

    Returns:
        class_: The value entered by the user, or None if nothing entered and allow_exit is True.
    """
    # Validation of parameters
    if min_value is not None and max_value is not None and max_value < min_value:
        raise ValueError("min_value must be less than or equal to max_value.")
    if valid_values:
        if min_value and max_value:
            valid_values = [
                val for val in valid_values if min_value <= val <= max_value
            ]
        elif min_value:
            valid_values = [val for val in valid_values if min_value <= val]
        elif max_value:
            valid_values = [val for val in valid_values if val <= max_value]

        if not valid_values:
            raise ValueError("Min and max range must include at least one valid value")

    # Validation of input
    while True:
        try:
            data = input(message)
            if allow_exit and data == "":
                return default_value
            data = class_(data)
        except ValueError:
            textfx.print_error(
                "Please enter a value of type {}.".format(class_.__name__)
            )
            continue

        if min_value is not None:
            if data < min_value:
                textfx.print_error(
                    "Ensure the value is greater than {}".format(min_value)
                )
                continue
        if max_value is not None:
            if data > max_value:
                textfx.print_error("Ensure the value is less than {}".format(max_value))
                continue
        if valid_values:
            if data not in valid_values:
                textfx.print_error("Value must be one of {}".format(valid_values))
                continue
        # If all goes well, break
        break
    return data


def device_config_setup():
    # Create device config and data file

    device_example_config = "services/config.example.json"
    test_device_example_config = "services/test-example.json"
    device_example_data = "services/data.example.json"

    # write device config
    with open(device_example_config, "r") as f_in, open(CONFIG_FILE, "w") as f_out:
        log.info("Creating device config from {0}".format(device_example_config))
        f_out.write(f_in.read())

    # write test device config
    with open(test_device_example_config, "r", encoding="utf-8") as f_in, open(
        TEST_CONFIG_FILE, "w", encoding="utf-8"
    ) as f_out:
        log.info(
            "Creating test device config from {0}".format(test_device_example_config)
        )
        f_out.write(f_in.read())

    # write device data
    with open(device_example_data, "r", encoding="utf-8") as f_in, open(
        DYNAMIC_DATA_FILE, "w", encoding="utf-8"
    ) as f_out:
        log.info("Creating device data from {0}".format(device_example_data))
        f_out.write(f_in.read())


def set_local_time():
    """sync the local rtc with network time."""
    modem = modem_driver.Modem()
    modem.initialise()
    network_time = modem.get_network_time()
    RTC = rtc_driver.rtc()
    RTC.set_local_time(network_time)
    result = RTC.get_local_time()
    log.info("Time from local RTC is now: {0}".format(result))


def check_sd_card():
    while True:
        try:
            textfx.print_info("Checking SD card...")
            if not sdcard.enabled():
                raise RuntimeError
        except RuntimeError:
            textfx.print_error(
                "No SD card detected. Check that the SD card is inserted properly."
            )
            response = _validate_input(
                "Would you like to retry [y/N]? ",
                str.lower,
                valid_values=["y", "n"],
                allow_exit=True,
                default_value="n",
            )
            # Finish if user doesn't want to retry, otherwise run setup again
            if response == "n":
                return False
            else:
                sdcard.setup()
                # The while loop will force it to retry
        else:
            break
    return True


def provision():
    # Do not put any provisioning before this line
    while True:
        response = _validate_input(
            "Please enter 'modem' or 'config' or 'time' to provision the modem or device config files or set time(enter to finish): ",
            str.lower,
            valid_values=["modem", "config", "time"],
            allow_exit=True,
        )
        if not response:
            break
        elif response == "modem":
            textfx.print_header("Setting up modem...")
            modem_setup()
        elif response == "config":
            textfx.print_header("Generating config")
            device_config_setup()
        elif response == "time":
            textfx.print_header("Setting time")
            set_local_time()
    # Do not put any provisioning beyond this line
    textfx.print_header("Provisioning complete")


if __name__ == "__main__":
    provision()
