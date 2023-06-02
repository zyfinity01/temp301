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


Test real time clock module

- Get time from local RTC
- Get time from external RTC
- Get time form network
- Set external RTC with network time
- Set local RTC with network time
"""

import unittest
from drivers import modem as modem_driver
from drivers import rtc as rtc_driver
import utime


class TestRTC(unittest.TestCase):
    """Test class for real time clock"""

    def __init__(self):
        """init external rtc and modem"""
        super().__init__()
        self.ex_rtc = rtc_driver.rtc()
        self.modem = modem_driver.Modem()
        self.modem.initialise()

    def test_local_rtc_time(self):
        """Test get time from local rtc."""
        result = self.ex_rtc.get_local_time()
        print("Time from local rtc: ", result)

    def test_external_rtc_time(self):
        """Test get time from external rtc."""
        result = self.ex_rtc.get_ex_rtc_time()
        print("Time from external rtc: ", result)

    def test_network_time(self):
        """Test get network time from modem."""
        result = self.modem.get_network_time()
        print("Time from network rtc: ", result)

    def compare_local_to_network_before_sync(self):
        """compare local time to network time"""
        local = self.ex_rtc.get_local_time()
        modem = self.modem.get_network_time()
        difference = local - modem
        if abs(difference) > 1:
            print("Difference is outside of acceptable error margin")
            print("Local time minus modem time is", difference)

    def test_sync_local_rtc_w_network(self):
        """sync the local rtc with network time."""
        network_time = self.modem.get_network_time()
        self.ex_rtc.set_local_time(network_time)
        result = self.ex_rtc.get_local_time()
        print("Time from local rtc now is : ", result)

    def compare_local_to_network_after_sync(self):
        """compare local time to network time"""
        local = self.ex_rtc.get_local_time()
        modem = self.modem.get_network_time()
        difference = local - modem
        if abs(difference) > 1:
            print("Difference is outside of acceptable error margin")
            print("Local time minus modem time is", difference)

    def test_sync_external_rtc_w_network(self):
        """sync the external rtc with network time ."""
        network_time = self.modem.get_network_time()
        self.ex_rtc.set_ex_rtc_time(network_time)
        result = self.ex_rtc.get_ex_rtc_time()
        print("Time from external rtc is : ", result)

    def test_sync_local_rtc_w_ex_rtc(self):
        """sync the local rtc with external rtc."""
        self.ex_rtc.sync_rtc_time()
        result = self.ex_rtc.get_local_time()
        print("Time from local rtc now is : ", result)

    def test_timezone(self):
        """test the timezone of rtc clock"""
        seconds = utime.timezone()
        hours = seconds / 3600
        print("Timezone is utc+", hours)


if __name__ == "__main__":
    unittest.main()
