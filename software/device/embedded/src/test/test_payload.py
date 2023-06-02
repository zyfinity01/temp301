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


Test getting data and make payload
"""

import unittest
import pcf8574
import time
import logging
import asyn
from machine import I2C
from drivers import counter as counter_driver
from drivers import sdi12 as sdi12_driver
from services import config as config_services
from services import sdi12 as sdi12_services

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

log = logging.getLogger("test_payload")
# Enable the following to set a log level specific to this module:
log.setLevel(logging.DEBUG)  # Special case (?)


class TestPayload(unittest.TestCase):
    """Test class for making payload"""

    def __init__(self):
        """Init the test"""
        super().__init__()
        ex_io = pcf8574.PCF8574(I2C(0), 0x38)
        self.rain_counter = counter_driver.init_counter(ex_io)
        self.sdi = sdi12_driver.init_sdi(0)
        # load device data to get rainfall data
        self.device_data = config_services.read_data_file()
        self.device_config = config_services.read_config_file(
            config_filename="test/integration/device-config.test.json"
        )

    @staticmethod
    def async_test_helper(async_generator):
        """async test helpper"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(async_generator)

    def test_reading_sdi(self):
        """Test reading data from sdi12 sensor 1"""
        # list of tasks to execute asynchronously
        tasks = []

        # turn on the sensors
        sensors = config_services.get_sensors(self.device_config)

        # filter sensors to ones that are "enabled"
        sensors_filtered = {
            name: data for name, data in sensors.items() if data["enabled"]
        }
        wake_time = sdi12_driver.turn_on_sensors(self.sdi)

        log.debug("Wake time: {0}".format(wake_time))

        # read sensorspro
        # TODO filter out sensors that aren't scheduled to be read
        names, gatherables = sdi12_services.gather_sensors(
            self.sdi, sensors_filtered, wake_time
        )
        tasks.extend(gatherables)

        # # Add sensors to tasks
        log.info("Running tasks...")
        log.debug("Tasks: {0}".format(tasks))
        sensor_reading_time = time.time()
        task_results = await asyn.Gather(tasks)

        log.debug("Sensor result: {}".format(task_results))

        sensor_results = [
            {"name": name, "readings": readings}
            for name, readings in zip(names, task_results)
        ]
        log.debug("Sensor results: {0}".format(sensor_results))

        # map readings tuple to dict
        sensor_mapped_results = [
            {
                "name": result["name"],
                "readings": sdi12_services.convert_readings(
                    result["readings"],
                    config_services.get_sensor(self.device_config, result["name"]),
                ),
            }
            for result in sensor_results
        ]

        log.debug(sensor_mapped_results)

        # Merge results from all sensors
        sensor_merged_results = {}
        for d in [sensor["readings"] for sensor in sensor_mapped_results]:
            for k, v in d.items():
                if k in sensor_merged_results:
                    log.warning("{0} already in dict and will be overwritten".format(k))
                sensor_merged_results[k] = v
        log.info("Merged readings from all sensors: {0}".format(sensor_merged_results))

        # Add time information
        sensor_merged_results["DateTime"] = sensor_reading_time

        log.debug(sensor_mapped_results)


if __name__ == "__main__":
    unittest.main()
