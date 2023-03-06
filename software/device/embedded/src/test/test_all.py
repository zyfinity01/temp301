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
import gc


def test_all():
    # Run all unittest suites (must be manually added for now)
    tests = [
        "test/test_counter",
        "test/test_sdi12",
        "test/test_modem",
        "test/test_rtc",
        "test/test_validations",
        "test/test_scheduler",
        "test/test_webserver",
        "test/test_sdcard",
        "test/test_pipeline",
        "test/test_logging",
        # "test/test_tinyweb", # temporarily disabled due to asyncio queue overflow errors in CI
    ]

    for test in tests:
        unittest.main(test, noexit=True)
        gc.collect()


if __name__ == "__main__":
    test_all()
