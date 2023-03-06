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

import logging
import unittest

log = logging.Logger("test_logging")


class TestLogging(unittest.TestCase):
    # These test cases were added for regression testing after the failure of
    # pipeline #41274 (04ebcd47c261abad34005ac93d9c0c8a5c1f4540)

    def test_log(self):
        exception_caught = False
        exception_msg = ""
        try:
            # Just testing info is enough to test debug,
            # warning, error, and critical
            log.info("Message %s %s", "Additional args", "Another arg")
        except Exception as test_exc:
            exception_caught = True
            exception_msg = test_exc

        self.assertFalse(
            exception_caught,
            'Exception caught when there should be no exceptions raised.\nGot: "{}"'.format(
                exception_msg
            ),
        )
