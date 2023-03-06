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
"""

try:
    import json as ujson
except ImportError:
    import ujson
import logging
from drivers.sdcard import gen_path

CONFIG_FILE = "/services/config.json"
TEST_CONFIG_FILE = "/services/test-config.json"
DYNAMIC_DATA_FILE = "/services/data.json"
log = logging.getLogger("config")
# Enable the following to set a log level specific to this module:
# log.setLevel(logging.DEBUG)


def read_config_file(config_filename: str = CONFIG_FILE):
    """
    return configuration file data as dict.

    This method contains side effects
    """
    try:
        with open(config_filename, "r", encoding="utf-8") as f_in:
            return ujson.load(f_in)
    except OSError:
        log.critical("Config file does not exist: {0}".format(config_filename))


def read_test_config_file():
    """
    Return unit-test specific configuration file data as dict.
    """
    return read_config_file(TEST_CONFIG_FILE)


def write_config_file(config_data, config_filename: str = CONFIG_FILE):
    """
    Write the latest config to the JSON file.

    TODO: add checking for existing file

    This method contains side effects
    """
    with open(config_filename, "w", encoding="utf-8") as f_out:
        ujson.dump(config_data, f_out)
    return True


def read_data_file(data_filename: str = DYNAMIC_DATA_FILE, sd=True):
    if sd:
        data_filename = gen_path(data_filename)
    try:
        with open(data_filename, "r", encoding="utf-8") as f_in:
            return ujson.load(f_in)
    except OSError:
        log.critical("Data file does not exist: {0}".format(data_filename))


def write_data_file(data, data_filename: str = DYNAMIC_DATA_FILE, sd=True):
    if sd:
        data_filename = gen_path(data_filename)
    with open(data_filename, "w", encoding="utf-8") as f_out:
        ujson.dump(data, f_out)
    return True


def update_sensor(config: dict, sensor_name: str, **kwargs):
    """

    Update a single sensor

    Args:
        config (dict): configuration dictionary
        sensor_name (str): name of sensor to update
        **kwargs: dict of values to update in sensor

    Returns:

    """
    # TODO make more memory efficient than copying entire dict (possible?)
    new_config = config.copy()

    for k, v in kwargs.items():
        new_config["sdi12_sensors"][sensor_name][k] = v

    # TODO would this work?
    # new_config['sdi12_sensors'][sensor_name].update(kwargs.items())

    return new_config


def get_sensor_names(config) -> list:
    """
    Return list of sensor names in the config dictionary
    """

    return list(config["sdi12_sensors"].keys())


def get_sensors(config: dict) -> dict:
    """

    Args:
        config:

    Returns:

    """
    return config["sdi12_sensors"]


def get_sensor(config: dict, sensor_name: str):
    return get_sensors(config)[sensor_name]


def create_sensor(config: dict, name: str) -> dict:
    """
    Create a new sensor with default values

    Args:
        config: existing config
        name: new sensor name
    Returns:
        new config with new sensor
    """
    new_config = config.copy()
    new_config["sdi12_sensors"][name] = {
        "enabled": True,
        "address": 1,
        "bootup_time": 0,
        "record_interval": 10,
        "first_record_at": 0,
        "readings": [],
    }

    return new_config
