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

from util.time import isoformat


class TestUtils(unittest.TestCase):
    def test_time_generation(self):
        expected = "2020-10-08T01:23:54"

        actual = isoformat((2020, 10, 8, 1, 23, 54, 0, 0))

        self.assertEqual(
            expected,
            actual,
            "DateTime was not generated properly.\nExpected {}, got {}".format(
                expected, actual
            ),
        )

    def test_date_generation(self):
        expected = "2020-10-08"

        actual = isoformat((2020, 10, 8, 1, 23, 54, 0, 0))[:10]

        self.assertEqual(
            expected,
            actual,
            "Date was not generated properly.\nExpected {}, got {}".format(
                expected, actual
            ),
        )
