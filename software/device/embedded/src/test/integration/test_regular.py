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

Process:

Load config -> Read counter -> Check scheduler -> Read sensors-> Log data -> Transmit data
"""
import unittest
import random
import main
from services import config as config_services
from drivers import counter as counter_driver


class TestRegular(unittest.TestCase):
    """Test class for integration test"""

    def __init__(self):
        """Init test"""
        super().__init__()
        # Allocate emergency ISR buffer - https://docs.micropython.org/en/latest/reference/isr_rules.htm
        self.rain_counter = counter_driver.Counter()
        self.rain_counter.reset()

    def test_regular_mode(self):
        # Load config file
        device_config = config_services.read_config_file(
            config_filename="test/integration/device-config.test.json", sd=False
        )
        device_data = config_services.read_data_file(
            data_filename="test/integration/device-data.test.json", sd=False
        )
        self.gen_rain_data()
        main.regular_mode(device_config, device_data)

    def gen_rain_data(self):
        # Generate random rain fall data from 0mm to 12mm
        tips = random.randint(0, 12)
        for i in range(tips):
            self.rain_counter.pulse()


if __name__ == "__main__":
    unittest.main()
