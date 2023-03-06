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


def isoformat(timetuple, sep="T"):
    """
    Return a string representing the date and time in ISO 8601 format.

    For the CPython module definition, see
    <https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat>
    and <https://github.com/python/cpython/blob/main/Lib/datetime.py>

    Args:
        time (time): a MicroPython time 8-tuple <https://docs.micropython.org/en/latest/library/time.html>
    """
    if type(timetuple) == int:
        timetuple = time.localtime(timetuple)
    # Check for tuple length greater than or equal to six
    if len(timetuple) >= 6:
        time_str = "{0:04d}-{1:02d}-{2:02d}{sep:1s}{3:02d}:{4:02d}:{5:02d}".format(
            *timetuple[:6], sep=sep
        )
    else:
        time_str = "isoformat(): unable to format a time tuple with {0} elements, require 6 elements (YYYY-MM-DD HH:MM:SS)".format(
            len(timetuple)
        )
    return time_str
