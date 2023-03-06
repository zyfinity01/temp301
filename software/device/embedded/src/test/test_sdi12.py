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


Test code for sdi12
"""

import time

# import random
import unittest
import pcf8574
from drivers import sdi12 as sdi12_driver
from machine import I2C

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio


class TestSDI(unittest.TestCase):
    """Test class for SDI12 sensor"""

    def __init__(self):
        """Init test"""
        super().__init__()
        self.sdi = sdi12_driver.init_sdi()

    @staticmethod
    def gen_sensor_data(
        enabled=True,
        address="1",
        bootup_time=20,
        record_interval=10,
        first_record_at=0,
    ):
        """generate sensor data"""
        return {
            "enabled": enabled,
            "address": address,
            "bootup_time": bootup_time,
            "record_interval": record_interval,
            "first_record_at": first_record_at,
            "readings": None,
        }

    def test_wake_sleep(self):
        """Test if the sensor sets the pin to wake and sleep correctly."""
        states = []
        expected = [1, 0]

        sdi12_driver.turn_on_sensors(self.sdi)
        # on value
        states.append(self.sdi["en"].value())
        sdi12_driver.turn_off_sensors(self.sdi)
        # off value
        states.append(self.sdi["en"].value())

        self.assertEqual(
            states,
            expected,
            "State of enable pin did not change.\nExpected {0}, got {1}".format(
                expected, states
            ),
        )

    @staticmethod
    def async_test_helper(async_generator):
        """async test helpper"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(async_generator)

    def test_requesting_measurement(self):
        """Requires a water level sensor."""

        sensor = self.gen_sensor_data(**{"address": "1", "bootup_time": 5})

        wake_time = sdi12_driver.turn_on_sensors(self.sdi)

        response = self.async_test_helper(
            sdi12_driver.measure(sensor, self.sdi, wake_time, False, "water level 1")
        )

        # Turn off sensors after running
        sdi12_driver.turn_off_sensors(self.sdi)

        expected = "10023\r\n"

        self.assertEqual(
            response,
            expected,
            "Did not receive correct response from sensor.\nExpected {0}, got {1}".format(
                expected, response
            ),
        )

    def test_data_reading(self):
        """Test reading data from sdi12 sensor 1"""
        sensor = self.gen_sensor_data(**{"address": "1", "bootup_time": 5})

        wake_time = sdi12_driver.turn_on_sensors(self.sdi)

        # run with max index equal to 3 as the sensor being used returns 3 values
        self.async_test_helper(
            sdi12_driver.measure(sensor, self.sdi, wake_time, False, "water level 1")
        )
        # sleep for a bit more time than needed, because why not?
        time.sleep(4)
        # read data
        response = self.async_test_helper(
            sdi12_driver.deep_data_reading(sensor, self.sdi, 3, wake_time)
        )

        # Turn off sensors after running
        sdi12_driver.turn_off_sensors(self.sdi)

        if response is None:
            self.fail("No response received from sensor.")
        # Have wide bounds so we aren't testing sensor,
        # we are just testing that the response isn't mangled
        self.assertTrue(
            -60 < response[0] < 10,
            "Reading #1 is not within the expected range of -60 to 10, got {0}".format(
                response[0]
            ),
        )  # pressure
        self.assertTrue(
            -10 < response[1] < 40,
            "Reading #2 is not within the expected range of -10 to 40, got {0}".format(
                response[1]
            ),
        )  # temperature
        self.assertTrue(
            8 < response[2] < 18,
            "Reading #3 is not within the expected range of 8 to 18, got {0}".format(
                response[2]
            ),
        )  # voltage
