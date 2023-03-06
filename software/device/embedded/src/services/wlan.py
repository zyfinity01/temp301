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

import network
import machine
import time
import logging

log = logging.getLogger("wlan")
# Enable the following to set a log level specific to this module:
# log.setLevel(logging.DEBUG)


def start_ap_mode(ssid: str, password: str = None):
    """
    Enable the access point on the device.

    Args:
        ssid (str): AP SSID
        password (str): AP password

    Returns:
        network interface object
    """

    log.info("Starting Access Point (AP) WLAN mode")
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)
    if password:
        ap_if.config(
            essid=ssid,
            password=password,
            authmode=network.AUTH_WPA2_PSK,
        )
    else:
        ap_if.config(essid=ssid)

    while not ap_if.active():
        pass

    log.info("AP WLAN mode started")
    log.info("Interface configuration: {0}".format(ap_if.ifconfig()))

    return ap_if


def connect_wifi(wlan, networks):
    """
    Attempt to connect to a wifi network.
    Args:
        wlan: wireless interface driver object
        networks: list of tuples of (SSID, password) to try connect to

    Returns:
        connected (bool)
    """
    for ssid, password in networks:
        log.info("Attempting to connect to {0}".format(ssid))
        wlan.connect(ssid, password)
        time.sleep(1)

        # keep reconnecting 3 times, then give up
        connection_attempts = 0
        while not wlan.isconnected() and connection_attempts < 3:
            machine.idle()  # save power while waiting
            connection_attempts += 1
            log.warning(
                "WLAN connection failed. Attempt {0}".format(connection_attempts)
            )
            time.sleep(5)

        if wlan.isconnected():
            log.info("WLAN connection succeeded! IP: {0}".format(wlan.ifconfig()[0]))
            return True
        else:
            log.error("Failed to connect to {0}".format(ssid))

    log.critical("Could not connect to any network. Disabling wifi")
    wlan.active(False)
    return False
