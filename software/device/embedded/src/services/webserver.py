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


The webserver service sends static data to the user, and updates the configuration of the device.

The server uses a REST API.

Endpoints are described in `docs/technical/architecture/webserver.md`.

refer to device/webapp/src/components/interfaces.ts or the example json files for configuration values
"""
import os
import json
import logging
import time

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

import lib.tinyweb as tinyweb
from lib.aswitch import Delay_ms

import services.config as config
from services.restapi import data, device, sdi12, monitor
import drivers.sdi12

log = logging.getLogger("webserver")
# Enable the following to set a log level specific to this module:
# log.setLevel(logging.DEBUG)

FILETYPE_ENCODINGS = {
    "js": "application/javascript",
    "css": "text/css",
    "html": "text/html",
}


class TimedWebserver(tinyweb.webserver):
    """
    Subclass of the tinyweb webserver class that adds a watchdog timer to automatically sleep the device if there is no activity

    """

    def __init__(self, timeout=300000, callback=None, **kwargs):
        """
        Initialise the webserver.
        Args:
            timeout (int): number of milliseconds to wait before timing out (default 5 minutes)
            callback (func): callback function for when the watchdog times out
            **kwargs: parameters to tinyweb webserver class
        """
        super().__init__(**kwargs)
        self.timeout_duration = timeout
        self.callback = callback
        self.watchdog = Delay_ms(self.timeout, (), duration=self.timeout_duration)

    async def _handler(self, reader, writer):
        log.debug("Timeout watchdog reset")
        self.watchdog.trigger()
        await super()._handler(reader, writer)

    def timeout(self):
        log.debug("Watchdog timed out")
        if self.callback:
            self.callback()

    def start_watchdog(self):
        log.debug("Webserver watchdog timer started")
        self.watchdog.trigger()


class WebServer:
    """
    Web Server driver object.
    """

    HOST = "0.0.0.0"
    PORT = 80

    def __init__(self, device_config, device_data, sdi):
        self.app = TimedWebserver(
            callback=self.stop, debug=True, max_concurrency=1, backlog=10
        )
        self.config = device_config
        self.data = device_data
        self.wake_time = -1
        self.sdi = sdi

        self.app.add_resource(
            device.Config,
            "/config",
            device_config=self.get_config,
            save_callback=self.save_config,
            maintenance_mode_callback=self.set_maintenance_mode,
        )
        self.app.add_resource(
            sdi12.Config,
            "/config/sdi12/update/<sensor_name>",
            device_config=self.get_config,
            save_callback=self.save_config,
        )
        self.app.add_resource(
            sdi12.Rename,
            "/config/sdi12/rename/<sensor_name>",
            device_config=self.get_config,
            save_callback=self.save_config,
        )
        self.app.add_resource(
            sdi12.Delete,
            "/config/sdi12/delete/<sensor_name>",
            device_config=self.get_config,
            save_callback=self.save_config,
        )
        self.app.add_resource(
            sdi12.Test,
            "/config/sdi12/test/<sensor_name>",
            sdi=self.get_sdi,
            device_config=self.get_config,
            sensor_wake_time=self.get_wake_time,
        )
        self.app.add_resource(
            data.Data,
            "/data",
            device_data=self.get_data,
            save_callback=None,
        )
        self.app.add_resource(
            monitor.Monitor,
            "/monitor",
            sdi=self.get_sdi,
            device_config=self.get_config,
            sensor_wake_time=self.get_wake_time,
        )
        self.app.add_route("/", self.get_main_page)
        self.app.add_route("/<file>", self.get_static_file)
        self.running = False

    def run(self):
        if not self.running:
            log.info(
                "Running webserver at {0} on port {1}".format(self.HOST, self.PORT)
            )
            self.app.run(host=self.HOST, port=self.PORT, loop_forever=False)
            self.running = True
            self.app.start_watchdog()

    async def clean_shutdown(self):
        """
        Ensure webserver coro is shut down

        References:
        - https://github.com/belyalov/tinyweb/
        - https://github.com/peterhinch/micropython-async/blob/master/v2/PRIMITIVES.md#4-task-cancellation
        """
        await asyncio.sleep_ms(100)

    def stop(self):
        log.info("Shutting down webserver and asyncio event loop")
        self.running = False
        self.app.shutdown()
        loop = asyncio.get_event_loop()
        loop.stop()

    def is_running(self):
        return self.running

    def get_config(self):
        return self.config

    def get_data(self):
        return self.data

    def get_wake_time(self):
        return self.wake_time

    def get_sdi(self):
        return self.sdi

    def set_maintenance_mode(self, enabled: bool):
        """
        Callback function called by the device config endpoint when maintenance mode is changed.

        Should initialise the SDI-12 sensors if enabled

        Args:
            enabled (bool): maintenance mode enabled

        """
        if enabled:
            wake_time = drivers.sdi12.turn_on_sensors(self.sdi)
            self.set_wake_time(wake_time)
        else:
            drivers.sdi12.turn_off_sensors(self.sdi)

    def set_wake_time(self, wake_time):
        log.debug("Sensor wake time set to {0}".format(wake_time))
        self.wake_time = wake_time

    def save_config(self, new_config: dict):
        log.debug("New configuration: " + str(new_config))
        self.config = new_config
        log.info("Writing configuration to non-volatile memory")
        config.write_config_file(new_config)

    def _check_file_exists(self, path: str):
        """
        Check if a file exists.
        Args:
            path (str): path to file

        Returns:
            boolean
        """
        try:
            os.stat(path)
            return True
        except OSError as e:
            log.error("OSError: {0}".format(e))
            return False

    async def get_main_page(self, req, resp):
        """
        send the index.html page
        """
        log.info("Returning index page")
        await resp.send_file(
            "static/index.html.gz", content_encoding="gzip", content_type="text/html"
        )

    async def get_static_file(self, req, resp, file: str):
        """
        Get a static file.

        Args:
            req:
            resp:
            file:

        Returns:

        """
        path = "static/{file}".format(file=file)
        log.info("Requested file: {0}".format(path))

        # Manually apply content-type and content_encoding header for some types of files.
        content_type = None
        content_encoding = None
        filetype = file.rsplit(".", 1)[-1]
        if filetype in FILETYPE_ENCODINGS.keys():
            content_type = FILETYPE_ENCODINGS[filetype]
            content_encoding = "gzip"

        # Send gzipped version if specified, otherwise send original file
        log.info(
            "Sending file with type {0} and encoding {1}".format(
                content_type, content_encoding
            )
        )
        await resp.send_file(
            path + (".gz" if content_encoding == "gzip" else ""),
            content_type=content_type,
            content_encoding=content_encoding,
        )
