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

import os
import time
import random
import util.helpers as helpers
import logging
import unittest
import drivers.sdcard as sdcard

from util.time import isoformat


class TestSD(unittest.TestCase):
    def setUp(self):
        print("Setting up...")
        sdcard.setup()

    def tearDown(self):
        # Delete files created, but catch OSError if they don't already exist
        print("Tearing down...")
        try:
            helpers.deep_rmdir("sd/daily")
        except OSError:
            pass
        try:
            os.remove(sdcard.get_log_file())
        except OSError:
            pass
        try:
            os.remove(sdcard.get_main_telemetry_file())
        except OSError:
            pass

        sdcard.teardown()

    def test_exists_after_setup(self):
        """Check that the SD card is connected properly."""
        success = sdcard.SD_DIR[1:] in os.listdir()

        self.assertTrue(
            success,
            "SD card directory was not mounted properly.\nCurrent working directory contains {}".format(
                os.listdir()
            ),
        )

    def test_free_space_success(self):
        """There's no way to ensure that the free space on the SD card is correct, so we will just check that this doesn't return -1 or crash during calling to ensure that the function isn't failing."""

        fail = False
        try:
            if sdcard.get_free_space() == -1:
                fail = True
        except OSError:
            fail = True

        self.assertFalse(fail, "get_free_space returned an incorrect response.")

    def test_saving_telemetry(self):
        """Ensure that header is generated and telemetry is saved."""
        data = {"Sensor 1": 1, "DateTime": 123456}
        sdcard.save_telemetry(data)

        response = None
        with open(sdcard.get_main_telemetry_file(), "r") as f:
            response = f.read()

        time_ = isoformat(123456)
        data.pop("DateTime")
        # We use _gen_data_string because we assume the function works as expected
        expected = sdcard.HEADER_STR + "\n" + "Sensor 1,{},1".format(time_) + "\n"

        self.assertEqual(
            response,
            expected,
            "Telemetry file does not contain correct data.\nExpected: {}, got: {}".format(
                repr(expected), repr(response)
            ),
        )

    def test_saving_telemetry_twice(self):
        """Ensure that saving two lines of data will only result in the header being placed once."""
        data1 = {"Sensor 1": 1, "DateTime": 123456}
        data2 = {"Sensor 2": 2, "DateTime": 123456}
        sdcard.save_telemetry(data1)
        sdcard.save_telemetry(data2)

        response = None
        with open(sdcard.get_main_telemetry_file(), "r") as f:
            response = f.read()

        time_ = isoformat(123456)
        data1.pop("DateTime")
        data2.pop("DateTime")
        # We use _gen_data_string because we assume the function works as expected
        expected = (
            sdcard.HEADER_STR
            + "\n"
            + "Sensor 1,{},1".format(time_)
            + "\n"
            + "Sensor 2,{},2".format(time_)
            + "\n"
        )

        self.assertEqual(
            response,
            expected,
            "Telemetry file does not contain correct data.\nExpected: {}, got: {}".format(
                repr(expected), repr(response)
            ),
        )

    def test_saving_multiple_lines(self):
        """Ensure that saving two lines of data will only result in the header being placed once and that multiple datapoints can be added with one dict."""
        data = {"Sensor 1": 1, "Sensor 2": 2, "DateTime": 123456}
        sdcard.save_telemetry(data)

        with open(sdcard.get_main_telemetry_file(), "r") as f:
            lines = [line for line in f]

        time_ = isoformat(123456)

        expected_1 = "Sensor 1,{},1\n".format(time_)
        expected_2 = "Sensor 2,{},2\n".format(time_)
        expected_header = sdcard.HEADER_STR + "\n"
        if lines[0] != expected_header:
            self.fail(
                "Header was incorrect.\nExpected {}, got {}".format(
                    repr(expected_header + "\n"), repr(lines[0])
                )
            )
        # There is no guarantee what order they will be saved, so just use `in`
        if expected_1 not in lines:
            self.fail(
                "Not all data was saved to the file.\nExpected to find {} in {}".format(
                    repr(expected_1), lines
                )
            )
        if expected_2 not in lines:
            self.fail(
                "Not all data was saved to the file.\nExpected to find {} in {}".format(
                    repr(expected_2), lines
                )
            )

    def test_logging(self):
        """Test that logging to the SD card is successful."""
        log = logging.getLogger("test_sdcard")

        # Generate random string with message in case the log file isn't properly deleted
        test_message = "This is a test message {}".format(random.random())
        log.info(test_message)
        # Close the log file so it saves
        sdcard.close_log()

        response = None
        with open(sdcard.get_log_file(), "r") as f:
            response = f.read()

        self.assertTrue(test_message in response, "Message not found in log file")

    def test_double_setup(self):
        """Check that the SD card can be set up multiple times without issue."""
        # Will set up once with the setUp() unittest method, so only need to try once more.
        try:
            sdcard.setup()
        except OSError as e:
            self.fail(
                "Running setup twice caused an OSError to be raised:\n{}".format(e)
            )

        self.assertTrue(
            sdcard._SD_ENABLED, "SD enable flag is not set when it should be."
        )


class TestSDLogic(unittest.TestCase):
    def test_data_generation(self):
        """Test that the data string generated is correct."""
        actual = sdcard._gen_data_string("sensor name", "value", "some timestamp")

        expected = "sensor name,some timestamp,value"

        self.assertEqual(
            actual,
            expected,
            "String returned by _gen_data_string is incorrect.\nExpected: {}, got: {}".format(
                repr(expected), repr(actual)
            ),
        )

    def test_file_appending(self):
        """Check that it can append to a file correctly."""
        file = "test_file"
        # Delete file before doing anything
        if file in os.listdir():
            os.remove(file)

        data_string = "hello world"
        sdcard._append_to_csv(file, [data_string])
        expected = data_string + "\n"

        data = None
        with open(file, "r") as f:
            data = f.read()

        self.assertEqual(
            data,
            expected,
            "File does not contain the correct data. Expected: {}, got: {}".format(
                repr(expected), repr(data)
            ),
        )

    def test_generating_path_short(self):
        expected = sdcard.get_logging_dir() + "/test"
        actual = sdcard.gen_path("test")

        self.assertEqual(
            expected,
            actual,
            "Filename was not generated properly.\nExpected {}, got {}".format(
                expected, actual
            ),
        )

    def test_generating_path_long(self):
        expected = sdcard.get_logging_dir() + "/test/a/few/more"
        actual = sdcard.gen_path("test", "a/few", "more")

        self.assertEqual(
            expected,
            actual,
            "Filename was not generated properly.\nExpected {}, got {}".format(
                expected, actual
            ),
        )
