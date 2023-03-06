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

import ujson
from services import config
import logging

log = logging.getLogger("build")
# Enable the following to set a log level specific to this module:
# log.setLevel(logging.DEBUG)

BUILD_INFO_FILE = "BUILD.json"


def log_build_info():
    """
    Print build information that was uploaded to the device as part of the provisioning process.

    Looks for a file called BUILD.json in the device root directory with the following schema:

    {
        "sha": "latest commit hash",
        "clean": true|false (false if there were locally modified files at build time)
        "built_at": "timestamp of build"
    }
    """

    try:
        with open(BUILD_INFO_FILE, "r", encoding="utf8") as build_info_file:
            build = ujson.load(build_info_file)
            configuration = config.read_config_file()

            log.info(
                "Data Recorder: {0}{1}".format(
                    configuration["device_name"],
                    "({0})".format(configuration["device_id"])
                    if len(configuration["device_id"]) > 0
                    else "",
                )
            )
            log.info("Hardware Revision {0}".format(configuration["hw_revision"]))
            log.info(
                "Software Revision {0:7.7s} [{1}]{2}".format(
                    build["sha"],
                    build["built_at"],
                    "" if build["clean"] else " with uncommitted changes",
                )
            )

    except ValueError:
        log.error(
            "Error reading {0}. File contents: {1}".format(
                BUILD_INFO_FILE, build_info_file.read()
            )
        )
    except OSError:
        log.error("Could not load {0}".format(BUILD_INFO_FILE))
