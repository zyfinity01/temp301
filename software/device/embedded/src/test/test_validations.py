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

import unittest
from services.validators import *


class TestValidations(unittest.TestCase):
    """
    Test class for testing input validation
    """

    def test_input_length_valid(self):
        self.assertTrue(validate_length("I am valid", 1, 40))
        self.assertTrue(validate_length("a", 1, 2))
        self.assertTrue(validate_length("aaa", 1, 5))
        self.assertTrue(validate_length("", 0, 5))

    def test_input_length_invalid(self):
        with self.assertRaises(ValueError):
            validate_length("", 1, 5)

        with self.assertRaises(ValueError):
            validate_length("a", 2, 5)

        with self.assertRaises(ValueError):
            validate_length("I am too long", 1, 5)

    def test_validate_length_invalid_arguments(self):
        with self.assertRaises(AssertionError):
            validate_length("string", -1, 10)

        with self.assertRaises(AssertionError):
            validate_length("string", 2, 1)

        with self.assertRaises(AssertionError):
            validate_length("string", 1, 1)

    def test_base64_valid(self):
        self.assertTrue(validate_base64("aGVsbG8="))
        self.assertTrue(validate_base64(""))

    def test_base64_invalid(self):
        with self.assertRaises(ValueError):
            validate_base64("im an invalid base64 string")

        with self.assertRaises(ValueError):
            validate_base64("aGVsbG$$$8=")

        with self.assertRaises(ValueError):
            validate_base64("aGVsbG-8")

    def test_num_valid(self):
        self.assertTrue(validate_num(0, 0))
        self.assertTrue(validate_num(10, 0))
        self.assertTrue(validate_num(10, 0, 20))

    def test_num_invalid(self):
        with self.assertRaises(ValueError):
            validate_num(0, 1)

        with self.assertRaises(ValueError):
            validate_num(10, 0, 5)

        with self.assertRaises(ValueError):
            validate_num(10, 0, 10)

    def test_valid_enum(self):
        self.assertTrue(validate_enum("X509", ["X509", "SAS"]))
        self.assertTrue(validate_enum("SAS", ["X509", "SAS"]))

    def test_invalid_enum(self):
        with self.assertRaises(ValueError):
            validate_enum("I DONT EXIST", ["YES", "NO"])

    def test_valid_type(self):
        self.assertTrue(validate_type("string", str))
        self.assertTrue(validate_type(123, int))
        self.assertTrue(validate_type(123, str, int))

    def test_invalid_type(self):
        with self.assertRaises(ValueError):
            validate_type("string", int)
        with self.assertRaises(ValueError):
            validate_type(123, str)

    def test_valid_regex_addr(self):
        self.assertTrue(validate_regex("a", ADDRESS_REGEX))
        self.assertTrue(validate_regex("a", ADDRESS_REGEX))

    def test_invalid_regex_addr(self):
        with self.assertRaises(ValueError):
            validate_regex("I'm obviously wrong", ADDRESS_REGEX)
        with self.assertRaises(ValueError):
            validate_regex("aa", ADDRESS_REGEX)
        with self.assertRaises(ValueError):
            validate_regex("10", ADDRESS_REGEX)

    def test_device_settings_valid_simple(self):
        settings = {
            "device_name": "name",
            "device_id": "device_id",
            "wifi_password": "password",
            "send_interval": 10,
        }

        validate_device_settings(settings)  # should pass

    def test_device_settings_valid(self):
        settings = {
            "device_name": "name",
            "device_id": "device_id",
            "wifi_password": "password",
            "send_interval": 10,
            "mqtt_settings": {
                "host": "test.mosquitto.org",
                "port": 1883,
                "username": "username",
            },
        }

        validate_device_settings(settings)  # should pass

    def test_device_settings_invalid(self):
        settings = {
            "device_name": "",
        }

        with self.assertRaises(ValueError):
            validate_device_settings(settings)

    def test_device_settings_invalid_2(self):
        settings = {
            "device_name": "valid name",
            "mqtt_settings": {
                "parent_topic": "invalidtopicname",
            },  # doesn't contain a leading or trailing slash
        }

        with self.assertRaises(ValueError):
            validate_device_settings(settings)

    def test_device_settings_invalid_key(self):
        settings = {"unknown": "value"}

        with self.assertRaises(ValueError):
            validate_device_settings(settings)

    def test_device_settings_invalid_key_nested(self):
        settings = {
            "mqtt_settings": {
                "unknown": "value",
            }
        }

        with self.assertRaises(ValueError):
            validate_device_settings(settings)

    def test_sensor_settings_valid_basic(self):
        settings = {
            "enabled": True,
            "address": "a",
            "bootup_time": 10,
            "record_interval": 10,
            "first_record_at": 1000,
        }

        # should validate normal values
        validate_sensor_settings(settings)

    def test_sensor_settings_valid(self):
        # nested list values
        settings = {
            "enabled": True,
            "address": "a",
            "bootup_time": 10,
            "record_interval": 10,
            "first_record_at": 1000,
            "readings": [
                {
                    "reading": "temperature",
                    "index": 0,
                    "unit": "c",
                    "multiplier": 1,
                    "offset": 2.0,
                }
            ],
        }

        # should validate normal values
        validate_sensor_settings(settings)

    def test_sensor_settings_invalid(self):
        # nested list values
        settings = {
            "enabled": True,
            "address": "a",
            "bootup_time": 10,
            "record_interval": 10,
            "first_record_at": 1000,
            "readings": [
                {
                    "reading": "temperature",
                    "index": -1,
                    "unit": "c",
                    "multiplier": 1,
                    "offset": 2.0,
                }
            ],
        }

        # invalid index
        with self.assertRaises(ValueError):
            validate_sensor_settings(settings)

    def test_sensor_settings_invalid_2(self):
        # nested list values
        settings = {
            "enabled": True,
            "address": "a",
            "bootup_time": 10,
            "record_interval": 10,
            "first_record_at": 1000,
            "readings": [
                {
                    "reading": "temperature",
                    "index": 0,
                    "unit": "m/s",
                    "multiplier": "I'm a string but I should be a number",
                    "offset": 2.0,
                }
            ],
        }

        # invalid multiplier
        with self.assertRaises(ValueError):
            validate_sensor_settings(settings)

    def test_sensor_settings_invalid_3(self):
        # nested list values
        settings = {
            "enabled": True,
            "address": "a",
            "bootup_time": 10,
            "record_interval": 10,
            "first_record_at": 1000,
            "readings": ["im a string"],
        }

        # invalid list element
        with self.assertRaises(ValueError):
            validate_sensor_settings(settings)
