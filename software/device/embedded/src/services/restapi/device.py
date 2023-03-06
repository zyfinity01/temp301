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

from services import validators
import json
import logging

log = logging.getLogger("restapi.device")
# Enable the following to set a log level specific to this module:
# log.setLevel(logging.DEBUG)


class Config:
    def post(
        self,
        data: dict,
        device_config,
        save_callback=None,
        maintenance_mode_callback=None,
    ):
        """
        Update an arbitrary configuration value

        Args:
            data (dict): dict of POST request body parameters
            device_config (function): callback method to retrieve device config
            save_callback (function): callback method to save changed data
            maintenance_mode_callback (function): callback method to signal maintenance mode change
        Returns:
            JSON string of list of values updated from data.keys()
        """
        log.debug("Data: {0}".format(data))

        # validate incoming parameters
        try:
            validators.validate_device_settings(data)
        except ValueError as e:
            log.debug("ValueError: {0}".format(e))
            return json.dumps({"error": e}), 400

        # signal if maintenance mode was set
        if "maintenance_mode" in data:
            maintenance_mode_callback(data["maintenance_mode"])

        # modify copy of device config, rather than original config
        # This is a more "immutable" approach, and might help prevent race conditions
        # TODO: more memory efficient version of this
        new_config = device_config().copy()
        new_config.update(data)

        save_callback(new_config)  # write to file
        # in reality, probably won't save the config file every update - would queue the changes up

        # TODO: handle adding new sensors

        return json.dumps({"updated": list(data.keys())}), 200

    def get(self, data: dict, device_config, **kwargs):
        """
        Get the value of config data

        GET requests can have the `param` parameter set in the query string to return a config value,
        otherwise will return the entire config

        Args:
            data (dict): GET request query string values (ie from /config?param=value)
            device_config (function): callback method to retrieve device config
            kwargs: unused params
        Returns:
            JSON response of config value from key
        """
        log.debug("Received GET /config")

        # get a particular config item
        if "param" in data.keys():
            param = data["param"]
            log.debug("Data: {0}, param: {1}".format(data, param))
            return json.dumps({param: device_config()[param]}), 200

        # return entire config as JSON
        return json.dumps(device_config()), 200
