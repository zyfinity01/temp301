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

import json
import drivers.sdi12
import logging

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

log = logging.getLogger("monitor")
# Enable the following to set a log level specific to this module:
# log.setLevel(logging.DEBUG)


class Monitor:
    @staticmethod
    async def get(data: dict, sdi, device_config, sensor_wake_time):
        """
        Get raw output from the SDI-12 sensor.
        Requires maintenance mode to be set.

        Args:
            data (dict): query params containing command
            sdi (function): SDI-12 driver dict callback function
            device_config (function): device configuration callback method (used to get maintenance mode)
            sensor_wake_time (function): callback function to get the time when the sensor started up

        Returns:
            JSON response of the monitor output
        """

        if "command" not in data:
            return json.dumps({"error: command not supplied"})
        if not device_config()["maintenance_mode"]:
            return json.dumps({"error": "maintenance mode not enabled"})

        wake_time = sensor_wake_time()
        if wake_time < 0:
            return json.dumps(
                {
                    "error": "sensors haven't been started yet. Is maintenance mode enabled?"
                }
            )

        command = data["command"]

        try:
            result = await drivers.sdi12.run_command(command, sdi(), wake_time)
            return json.dumps({"command": command, "response": result}), 200
        except (ValueError, RuntimeError, TypeError) as e:
            log.critical("Exception: {0}".format(e))
            return json.dumps({"error": e}), 400
