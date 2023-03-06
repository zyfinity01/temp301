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

from services import config
from services import validators
import logging
import json
import re
import drivers.sdi12
import services.config

log = logging.getLogger("restapi.sdi12")
# Enable the following to set a log level specific to this module:
# log.setLevel(logging.DEBUG)

SENSOR_NAME_REGEX = "^[a-zA-Z_0-9]+$"


class Config:
    """
    Resource for updating SDI12 sensor configuration
    """

    def post(self, data: dict, sensor_name: str, device_config, save_callback):
        """
        update the configuration values of an SDI-12 sensor.

        If the sensor doesn't exist, create a new one

        Args:
            data: new config values
            sensor_name: sensor to update (key in config.json)
            device_config (function): callback method to retrieve device config
            save_callback: callback function to save data
        """

        if data is None:
            return (
                {
                    "error": "no data received (make sure Content-Type header is application/json)",
                },
                400,
            )

        log.debug("Received Data for {0}: {1}".format(sensor_name, str(data)))

        # validate incoming data
        try:
            validators.validate_sensor_settings(data)
        except ValueError as e:
            log.debug("ValueError: {0}".format(e))
            return json.dumps({"error": e}), 400

        if sensor_name not in config.get_sensor_names(device_config()):

            if not re.match(SENSOR_NAME_REGEX, sensor_name):
                return (
                    {
                        "error": "Invalid sensor name (letters, numbers and underscores only)"
                    },
                    400,
                )

            new_config = config.create_sensor(device_config(), sensor_name)
            save_callback(new_config)
            log.info("Created new sensor {0}".format(sensor_name))
            return {"message": "created new sensor!"}, 200

        updated_config = config.update_sensor(device_config(), sensor_name, **data)
        save_callback(updated_config)
        return {"message": "updated {0}".format(sensor_name)}, 200


class Rename:
    def post(self, data: dict, sensor_name: str, device_config, save_callback):
        if data is None:
            return (
                {
                    "error": "No data received (make sure Content-Type header is application/json)",
                },
                400,
            )

        if "name" not in data:
            return {"error": "New name not in request body"}, 400
        log.debug("Data: {0}".format(data))

        new_name = data["name"]

        # validate name
        if len(new_name) > 20:
            log.info("Invalid name supplied (too long): {0}".format(new_name))
            return {"error": "New name is too long"}, 400
        if not re.match(SENSOR_NAME_REGEX, sensor_name):
            return (
                {
                    "error": "Invalid sensor name (letters, numbers and underscores only)"
                },
                400,
            )

        # update dict and save
        new_config = device_config().copy()

        # ensure sensor exists
        if sensor_name not in config.get_sensor_names(new_config):
            message = "{0} isn't in sensor config".format(sensor_name)
            log.warning(message)
            return {"message": message}, 400

        new_config["sdi12_sensors"][new_name] = new_config["sdi12_sensors"].pop(
            sensor_name
        )
        save_callback(new_config)

        message = "Renamed {0} to {1}".format(sensor_name, new_name)
        log.info(message)
        return {"message": message}, 200


class Delete:
    def post(self, data: dict, sensor_name: str, device_config, save_callback):
        log.info("Deleting {0} (data: {1})".format(sensor_name, data))

        new_config = device_config().copy()

        # ensure sensor exists
        if sensor_name not in config.get_sensor_names(new_config):
            message = "{0} isn't in sensor config".format(sensor_name)
            log.warning(message)
            return {"message": message}, 400

        new_config["sdi12_sensors"].pop(sensor_name)
        save_callback(new_config)

        message = "Deleted sensor: {0}".format(sensor_name)
        log.info(message)
        return {"message": message}, 200


class Test:
    @staticmethod
    async def get(data: dict, sensor_name: str, sdi, device_config, sensor_wake_time):
        """
        Test the SDI-12 sensor.

        Args:
            data (dict): unused
            sensor_name (str): name of the sensor to read
            sdi (function): callback method to retrieve SDI-12 driver
            device_config (function): callback method to retrieve device config
            sensor_wake_time (function): callback method to retrieve wake time of the sensor

        Returns:

        """

        if not device_config()["maintenance_mode"]:
            return json.dumps({"error": "maintenance mode not enabled"})

        wake_time = sensor_wake_time()
        if wake_time < 0:
            return json.dumps(
                {
                    "error": "sensors haven't been started yet. Is maintenance mode enabled?"
                }
            )

        sensor: dict = services.config.get_sensor(device_config(), sensor_name)
        log.debug("Requesting data from sensor: {0}".format(sensor))

        try:
            result = await drivers.sdi12.read_sensor(sensor, sdi(), wake_time)
            log.info("Test result: {0}".format(result))
            return json.dumps({"response": result}), 200
        except (ValueError, RuntimeError, TypeError) as e:
            log.critical("Exception: {0}".format(e))
            return json.dumps({"error": e}), 500
