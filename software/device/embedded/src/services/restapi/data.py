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
import json

log = logging.getLogger("restapi.data")
# Enable the following to set a log level specific to this module:
# log.setLevel(logging.DEBUG)


class Data:
    def get(self, data: dict, device_data, save_callback=None):
        """
        Get device data

        Args:
            data: unused
            device_data: getter method for device data

        Returns:
            a json string of the entire config data

        """
        log.debug("Received GET /data")
        return json.dumps(device_data()), 200
