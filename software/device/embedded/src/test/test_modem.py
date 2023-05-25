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


Test AT commands and network for modem
"""

import unittest
from drivers import modem as modem_driver
from services import config_new
from util.time import isoformat

import time


class TestModem(unittest.TestCase):
    """Test class for modem"""

    def __init__(self):
        super().__init__()
        self.modem = modem_driver.Modem()
        self.device_config = config_new.read_config(config_new.TEST_CONFIG_FILE)

    def test_power_on(self):
        """Test if the power pin can wake up the modem."""
        # boot up modem
        boot_attempts = 0
        while not self.modem.command_at() and boot_attempts < 3:
            boot_attempts += 1
            self.modem.power_on()

        result = self.modem.command_at()
        self.assertTrue(result, "Modem fail to turn on")

    def test_serial(self):
        """Test if the modem can communicate with AT command."""
        result = self.modem.command_at()
        self.assertTrue(result, "Fail to passthough AT command")

    def test_network(self):
        """Test if the modem can registor to network."""
        result = self.modem.initialise()
        self.assertTrue(result, "Modem fail to register to network.")

    def test_network_time(self):
        """Test if the modem can get network time."""
        result = self.modem.get_network_time()
        print(result)
        self.assertIsNotNone(result, "Modem fail to get network time.")

    def test_mqtt_setup_client(self):
        """Test setting up mqtt client"""
        client_id = self.device_config.mqtt_settings.username
        server = self.device_config.mqtt_settings.host
        self.modem.mqtt_reset()
        result = self.modem.mqtt_set_client(client_id, server)
        self.assertTrue(result, "Unable to set client")

    def test_connect(self):
        """Test connect to mqtt broker"""
        result = self.modem.mqtt_connect()
        self.assertTrue(result, "Unable to connect to server")

    def test_publish(self):
        """Test publish mqtt message"""
        topic = "test/environmentMonitoring/{}".format(self.device_config.device_name)
        payload = '{"DateTime": "2021-12-08T10:12:33", "temperature": 0.0, "rainfall": 0, "flow": 0.0}'
        result = self.modem.mqtt_publish(topic, payload)
        self.assertTrue(result, "Unable to publish message")

    def test_disconnect(self):
        """Test disconnect from broker"""
        result = self.modem.mqtt_disconnect()
        self.assertTrue(result, "Unable to disconnect to server")

    def test_http_post(self):
        """
        Use the MonitorMyWatershed test sensor as the unit-test endpoint
        """
        registration_token = "97f38860-679f-4a0e-9196-6a6f473bbc84"
        sampling_feature = "c9b1d92e-d52b-454a-a294-e2ca7736eb3b"
        timestamp = isoformat(time.localtime()) + "+12:00"
        data = {"66019fe3-6e8e-4143-bbf8-f7acbc131829": 100}

        # connect to server mmw
        connect = self.modem.http_connect()
        self.assertIn("OK", connect)

        connect_mattermost = self.modem.http_connect(modem_driver.MATTERMOST_SERVER)
        self.assertIn("OK", connect_mattermost)

        # send data to test endpoint
        post = self.modem.http_send(
            registration_token, sampling_feature, timestamp, data
        )
        self.assertTrue(post, "failed to send data")

    def test_file_write(self):
        result = self.modem.file_write("test_file", "test data")

        self.assertTrue(result)

        # file should exist in modem filesystem
        result = self.modem.send_command_read(
            "{0}=".format(modem_driver.MODEM_COMMAND_FILE_LIST)
        )
        self.assertIn("test_file", result, "modem doesn't contain file in filesystem")

        # file should contain correct contents
        result = self.modem.send_command_read(
            '{0}="{1}"'.format(modem_driver.MODEM_COMMAND_FILE_READ, "test_file")
        )

        self.assertIn("test data", result, "File doesn't have data")

    # FIXME This currently does not work, fix in next revision
    # this tests our new method for on off switch
    # def test_on_off_switch(self):
    #     """Test if the power pin can wake up the modem."""
    #     # if modem is on turn off
    #     if self.modem.command_at:
    #         self.modem.on_off_switch()
    #         result = self.modem.command_at()
    #         self.assertFalse(result, "Modem failed to turn off")
    #     # if modem is off turn on
    #     else:
    #         self.modem.on_off_switch()
    #         result = self.modem.command_at()
    #         self.assertTrue(result, "Modem failed to turn on")


if __name__ == "__main__":
    unittest.main()
