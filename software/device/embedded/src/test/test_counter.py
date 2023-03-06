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


Tests for tipping bucket rain gauge counter
"""

import unittest
import time
from random import randint
from drivers import counter as counter_driver


# pylint: disable=unused-variable,protected-access
class TestCounter(unittest.TestCase):
    """Test class for the tipping bucket rain gauge counter."""

    def __init__(self):
        """Instantiate and initialise a counter"""
        super().__init__()
        self.rain_counter = counter_driver.Counter()
        self.rain_counter.initialise()

    def test_reset(self):
        """
        Test counter reset

        Place a random number of counts in the output register prior to
        executing the reset. Subsequent tests rely on counter.reset()
        functioning correctly, so this test should run first.
        """
        randcount = randint(1, 60)
        self.rain_counter.reset()
        for i in range(1, randcount + 1):
            self.rain_counter.__pulse_cpc()
            time.sleep_us(10)
        reading = self.rain_counter.read()
        if reading != randcount:
            print(
                "ERROR: output register reads {0} after {1} pulses".format(
                    reading, randcount
                )
            )
            raise RuntimeError
        self.rain_counter.reset()
        reading = self.rain_counter.read()
        self.assertEqual(reading, 0, "Counter is not zero directly after reset")

    def test_counting_fast(self):
        """
        Test all possible count accumulations read correctly

        Rev::4.0 design limitations require the maximum count to be limited
        to 60. The PCF8574A throws exceptions when the output register
        contains 62 or 63 (#543). The TB6/0.2 mm has a maximum count rate of a
        little under 1 Hz, so must read and reset the counter once every 60
        seconds.
        """
        for i in range(1, 60 + 1):
            print(" {0}".format(i) if (i == 1) else ", {0}".format(i), sep="", end="")
            self.rain_counter.reset()
            for j in range(1, i + 1):
                self.rain_counter.__pulse_cpc()
                time.sleep_us(10)
            reading = self.rain_counter.read()
            self.assertEqual(
                reading,
                i,
                "Output register reads {0} after {1} pulses".format(reading, i),
            )
        print(".")  # Terminate the list with a full stop and newline.

    # def test_counting_slow(self):
    #     """
    #     Test consecutive pulses
    #
    #     Rev::4.0 design limitations require the maximum count to be limited
    #     to 60. The PCF8574A throws exceptions when the output register
    #     contains 62 or 63 (#543).
    #
    #     The TB6/0.2mm manual specifies a maximum rainfall intensity of 700
    #     mm/hour, which gives a fastest average tip rate of 3500 tips/hour or
    #     0.97 tips/seconds (1.02 seconds/tip). Use this frequency, 1 Hz,
    #     for the slow test.
    #     """
    #     half_period = 500  # Milliseconds between pulses, halved.
    #     self.rain_counter.reset()
    #     for i in range(1, 60 + 1):
    #         print(" {0}".format(i) if (i == 1) else ", {0}".format(i), sep="", end="")
    #         self.rain_counter.__pulse_cpc()
    #         time.sleep_ms(half_period)
    #         reading = self.rain_counter.read()
    #         self.assertEqual(
    #             reading,
    #             i,
    #             "Output register reads {0} after {1} pulses".format(reading, i),
    #         )
    #         time.sleep_ms(half_period)
    #     print(".")  # Terminate the list with a full stop and newline.

    # def test_error_recovery(self):
    #   """
    #   See #543 for details of this test and the reason it is not included.
    #   """

    # def test_stability(self):
    #     """Test the count holds at zero when there are no events"""
    #     self.rain_counter.reset()
    #     print(
    #         "Counter reset, testing the output register remains zero for 5 minutes..."
    #     )
    #     for i in range(1, 5 + 1):
    #         time.sleep(60)
    #         reading = self.rain_counter.read()
    #         self.assertEqual(
    #             reading,
    #             0,
    #             "Output register reads {0} without external event".format(reading),
    #         )
    #         print("OK after {0} minutes".format(i))


if __name__ == "__main__":
    unittest.main()
