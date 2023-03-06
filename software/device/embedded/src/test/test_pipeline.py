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

from services import sdi12
import unittest


class PipelineTests(unittest.TestCase):
    def test_convert_readings(self):
        readings = [
            {
                "reading": "temperature",
                "index": 0,
                "multiplier": 1,
                "offset": 0,
                "unit": "c",
            },
            {
                "reading": "flow",
                "index": 1,
                "multiplier": 1,
                "offset": 0,
                "unit": "mm/s",
            },
        ]

        sensor = {"readings": readings}
        sensor_results = (10, 20)

        result_dict = sdi12.convert_readings(sensor_results, sensor)

        expected = {"temperature": 10, "flow": 20}

        self.assertEqual(expected, result_dict)

    def test_convert_readings_2(self):
        readings = [
            {
                "reading": "temperature",
                "index": 0,
                "multiplier": 1,
                "offset": 0,
                "unit": "c",
            },
            {
                "reading": "flow",
                "index": 1,
                "multiplier": 1,
                "offset": 0,
                "unit": "mm/s",
            },
        ]

        sensor = {"readings": readings}
        sensor_results = (10, 20, 30)

        with self.assertRaises(ValueError):
            result_dict = sdi12.convert_readings(sensor_results, sensor)

    def test_convert_readings_empty(self):
        readings = tuple([])
        sensor = {}

        self.assertEqual({}, sdi12.convert_readings(readings, sensor))

    def test_convert_readings_invalid_sensor(self):
        with self.assertRaises(ValueError):
            sdi12.convert_readings((1, 2, 3), {})
