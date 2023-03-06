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

import time

import unittest
import services.scheduler as scheduler


class TestSleep(unittest.TestCase):
    sensor = {
        "address": 1,
        "bootup_time": 0,
        "record_interval": 15,
        "first_record_at": 0,
        "multiplier": 1,
        "offset": 0,
        "unit": "mm",
        "enabled": True,
    }

    def test_next_time_zero(self):
        sleep_for = scheduler.get_time_to_next_recording(
            time.mktime((2020, 7, 27, 1, 0, 0, 0, 0)), self.sensor
        )

        self.assertEqual(sleep_for, 0)

    def test_14_mins(self):
        sleep_for = scheduler.get_time_to_next_recording(
            time.mktime((2020, 7, 27, 0, 46, 0, 0, 0)), self.sensor
        )

        self.assertEqual(sleep_for, 14 * 60)

    def test_10_seconds(self):
        sleep_for = scheduler.get_time_to_next_recording(
            time.mktime((2020, 7, 27, 0, 59, 50, 0, 0)), self.sensor
        )

        self.assertEqual(sleep_for, 10)

    def test_not_at_first_record(self):
        # should be 19 minutes away

        sensor = {
            "address": 1,
            "bootup_time": 0,
            "record_interval": 15,
            "first_record_at": time.mktime((2020, 1, 2, 1, 0, 0, 0, 0)),
            "multiplier": 1,
            "offset": 0,
            "unit": "mm",
            "enabled": True,
        }

        sleep_for = scheduler.get_time_to_next_recording(
            time.mktime((2020, 1, 2, 0, 41, 0, 0, 0)), sensor
        )

        self.assertEqual(sleep_for, 19 * 60)

    def test_sleep_time(self):
        sensor = {
            "address": 1,
            "bootup_time": 0,
            "record_interval": 15,
            "first_record_at": time.mktime((2020, 1, 2, 1, 0, 0, 0, 0)),
            "multiplier": 1,
            "offset": 0,
            "unit": "mm",
            "enabled": True,
        }

        current_time = time.mktime((2020, 3, 3, 1, 47, 0, 0, 0))

        self.assertEqual(
            scheduler.calculate_sleep_time(current_time, {"test-sensor": sensor}),
            13 * 60,
        )

    def test_sleep_time_multiple(self):
        sensors = {
            "test-1": {
                "address": 1,
                "bootup_time": 0,
                "record_interval": 15,
                "first_record_at": time.mktime((2020, 1, 2, 1, 0, 0, 0, 0)),
                "multiplier": 1,
                "offset": 0,
                "unit": "mm",
                "enabled": True,
            },
            "test-2": {
                "address": 1,
                "bootup_time": 0,
                "record_interval": 30,
                "first_record_at": time.mktime((2020, 1, 2, 1, 0, 0, 0, 0)),
                "multiplier": 1,
                "offset": 0,
                "unit": "mm",
                "enabled": True,
            },
        }
        current_time = time.mktime((2020, 3, 3, 1, 50, 0, 0, 0))

        self.assertEqual(
            scheduler.calculate_sleep_time(current_time, sensors),
            10 * 60,
        )

    def test_sleep_time_boot(self):
        sensor = {
            "address": 1,
            "bootup_time": 10,
            "record_interval": 15,
            "first_record_at": time.mktime((2020, 1, 2, 1, 0, 0, 0, 0)),
            "multiplier": 1,
            "offset": 0,
            "unit": "mm",
            "enabled": True,
        }

        current_time = time.mktime((2020, 3, 3, 1, 47, 0, 0, 0))

        # 10 second boot time
        self.assertEqual(
            scheduler.calculate_sleep_time(current_time, {"test-sensor": sensor}),
            (13 * 60) - 10,
        )

    def test_sleep_time_boot_multiple(self):
        sensors = {
            "test-1": {
                "address": 1,
                "bootup_time": 20,
                "record_interval": 15,
                "first_record_at": time.mktime((2020, 1, 2, 1, 0, 0, 0, 0)),
                "multiplier": 1,
                "offset": 0,
                "unit": "mm",
                "enabled": True,
            },
            "test-2": {
                "address": 1,
                "bootup_time": 10,
                "record_interval": 30,
                "first_record_at": time.mktime((2020, 1, 2, 1, 0, 0, 0, 0)),
                "multiplier": 1,
                "offset": 0,
                "unit": "mm",
                "enabled": True,
            },
        }
        current_time = time.mktime((2020, 3, 3, 1, 50, 0, 0, 0))

        self.assertEqual(
            scheduler.calculate_sleep_time(current_time, sensors),
            (10 * 60) - 20,
        )

    def test_sleep_time_first_record(self):
        sensor = {
            "address": 1,
            "bootup_time": 10,
            "record_interval": 15,
            "first_record_at": time.mktime((2020, 3, 3, 2, 0, 0, 0, 0)),
            "multiplier": 1,
            "offset": 0,
            "unit": "mm",
            "enabled": True,
        }

        # first_record is ahead of current time
        current_time = time.mktime((2020, 3, 3, 1, 50, 0, 0, 0))

        # 10 second boot time
        self.assertEqual(
            scheduler.calculate_sleep_time(current_time, {"test-sensor": sensor}),
            (10 * 60) - 10,
        )

    def test_sleep_time_first_record_two_sensors(self):
        sensors = {
            "test-1": {
                "address": 1,
                "bootup_time": 20,
                "record_interval": 15,
                "first_record_at": time.mktime((2020, 1, 2, 1, 0, 0, 0, 0)),
                "multiplier": 1,
                "offset": 0,
                "unit": "mm",
                "enabled": True,
            },
            "test-2": {
                "address": 1,
                "bootup_time": 10,
                "record_interval": 30,
                "first_record_at": time.mktime((2020, 1, 2, 1, 30, 0, 0, 0)),
                "multiplier": 1,
                "offset": 0,
                "unit": "mm",
                "enabled": True,
            },
        }

        # same as above, but sensor 2 shouldn't record for a while
        current_time = time.mktime((2020, 1, 2, 0, 50, 0, 0, 0))

        self.assertEqual(
            scheduler.calculate_sleep_time(current_time, sensors),
            (10 * 60) - 20,
        )
