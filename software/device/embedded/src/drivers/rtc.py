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


This module define functions that help setting the real time clock
"""
import time
import ds1307
from machine import I2C, RTC


class rtc:
    def __init__(self) -> None:
        self.ex_rtc = ds1307.DS1307(I2C(0))
        self.local_rtc = RTC()

    def get_ex_rtc_time(self):
        """get time from external rtc"""
        rtc_time = self.ex_rtc.datetime()
        maped_time = time.mktime(
            (
                rtc_time[0],
                rtc_time[1],
                rtc_time[2],
                rtc_time[4],
                rtc_time[5],
                rtc_time[6],
                0,
                0,
            )
        )
        return time.localtime(maped_time)

    def sync_rtc_time(self):
        """Syncronize the ESP32's real time clock with external clock"""
        ex_rtc_time = self.ex_rtc.datetime()
        self.local_rtc.datetime(
            (
                ex_rtc_time[0],
                ex_rtc_time[1],
                ex_rtc_time[2],
                0,
                ex_rtc_time[4],
                ex_rtc_time[5],
                ex_rtc_time[6],
                0,
            )
        )

    def set_ex_rtc_time(self, new_time):
        """Set the external clock with given time
        input format(year, month, day, hour, minute, second)
        """
        self.ex_rtc.datetime(
            (
                new_time[0],
                new_time[1],
                new_time[2],
                0,
                new_time[3],
                new_time[4],
                new_time[5],
                0,
            )
        )

    def reset_rtc_time(self):
        """Reset rtc to year 2000"""
        self.ex_rtc.datetime((2000, 0, 0, 0, 0, 0, 0, 0))

    def set_local_time(self, new_time):
        """Set local rtc with provided time"""
        self.local_rtc.datetime(
            (
                new_time[0],
                new_time[1],
                new_time[2],
                0,
                new_time[3],
                new_time[4],
                new_time[5],
                0,
            )
        )

    def get_local_time(self):
        """Return local time"""
        return time.localtime()
