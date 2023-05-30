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

import gc
import unittest
from lib.tinyweb import webserver
from services.restapi.monitor import Monitor
from services.restapi.sdi12 import Rename, Delete
from test.test_tinyweb import mockReader, mockWriter, HDRE, HDR, run_coro
import json
from drivers import sdi12
from services import config

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio


class TestResourceSync:
    def get(self, data):
        return '{"data":"yep"}'


class TestResourceSyncStatic:
    """
    Class that uses static methods instead of bound methods.
    """

    @staticmethod
    def get(data):
        return '{"data":"yep"}'


class TestResourceAsync:
    """
    Class that uses async methods instead of sync methods.
    async methods should be static methods.
    """

    @staticmethod
    async def get(data):
        await asyncio.sleep(0)
        return '{"data":"yep"}'


class TinyWebTests(unittest.TestCase):
    """
    These tests test the additional functionality added to the tinyweb library (namely coroutine support to resources)
    """

    def setUp(self):
        self.server = webserver()
        self.server.conns[id(1)] = None
        self.server.add_resource(TestResourceSync, "/resource_sync")
        self.server.add_resource(TestResourceSyncStatic, "/resource_sync_static")
        self.server.add_resource(TestResourceAsync, "/resource_async")

    def resource_test_helper(self, url):
        rdr = mockReader(["GET {0} HTTP/1.0\r\n".format(url), HDRE])
        wrt = mockWriter()
        run_coro(self.server._handler(rdr, wrt))
        payload = '{"data":"yep"}'
        exp = [
            "HTTP/1.0 200 MSG\r\n"
            + "Access-Control-Allow-Origin: *\r\n"
            + "Access-Control-Allow-Headers: *\r\n"
            + "Content-Length: {0}\r\n".format(len(payload))
            + "Access-Control-Allow-Methods: GET\r\n"
            + "Content-Type: application/json\r\n\r\n",
            payload,
        ]
        print("Received: ", wrt.history)
        self.assertEqual(wrt.history, exp)

    def test_resource_sync(self):
        self.resource_test_helper("/resource_sync")

    def test_resource_sync_static(self):
        self.resource_test_helper("/resource_sync_static")

    def test_resource_sync_async(self):
        self.resource_test_helper("/resource_async")


class MonitorTests(unittest.TestCase):
    """
    Test the monitor.

    These are more like integration tests because they involve the integration between device config, the web server and the sdi-12 sensors

    TODO: when !168 is merged, move this to the integration test suite

    """

    sdi = sdi12.init_sdi(0)
    device_config = config.read_config_file(
        "test/integration/device-config.test.json", sd=False
    )
    wake = sdi12.turn_on_sensors(sdi)

    def setUp(self):
        self.server = webserver()
        self.server.conns[id(1)] = None
        self.server.add_resource(
            Monitor,
            "/monitor",
            sdi=lambda: self.sdi,
            device_config=lambda: self.device_config,
            sensor_wake_time=lambda: self.wake,
        )

    def tearDown(self):
        gc.collect()

    def test_valid_input(self):
        command = '{"command": "?!"}'

        rdr = mockReader(
            [
                "GET /monitor HTTP/1.0\r\n",
                HDR("Content-Length: {0}".format(len(command))),
                HDR("Content-Type: application/json"),
                HDRE,
                command,
            ]
        )
        wrt = mockWriter()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.server._handler(rdr, wrt))
        resp = json.loads(wrt.history[1])
        print("received " + wrt.history[1])
        self.assertTrue("response" in resp)
        self.assertTrue("command" in resp)
        self.assertEqual("1\r\n", resp["response"])


class RenameTests(unittest.TestCase):

    device_config = config.read_config_file(
        "test/integration/device-config.test.json", sd=False
    )

    def save(self, config):
        self.device_config = config

    def setUp(self):
        self.server = webserver()
        self.server.conns[id(1)] = None
        self.server.add_resource(
            Rename,
            "/rename/<sensor_name>",
            device_config=lambda: self.device_config,
            save_callback=self.save,
        )

    def test_rename(self):
        # test without webserver
        rename = Rename()
        conf = {"sdi12_sensors": {"current": {"address": 1}}}
        expected = {"sdi12_sensors": {"new_name": {"address": 1}}}

        def save(config):
            self.assertEqual(config, expected)

        message, response_code = rename.post(
            {"name": "new_name"},
            sensor_name="current",
            device_config=lambda: conf,
            save_callback=save,
        )
        self.assertEqual(response_code, 200)

    def test_rename_invalid(self):
        # test without webserver

        rename = Rename()
        conf = {"sdi12_sensors": {"current": {"address": 1}}}

        def save(conf):
            pass

        # invalid sensor name
        message, response_code = rename.post(
            {"name": "new_name"},
            sensor_name="invalid",
            device_config=lambda: conf,
            save_callback=save,
        )
        self.assertEqual(response_code, 400)

    def test_no_name_supplied(self):
        # test without webserver

        rename = Rename()
        conf = {"sdi12_sensors": {"current": {"address": 1}}}

        def save(conf):
            pass

        # invalid sensor name
        message, response_code = rename.post(
            {},
            sensor_name="current",
            device_config=lambda: conf,
            save_callback=save,
        )
        self.assertEqual(response_code, 400)

    def test_name_too_long(self):
        rename = Rename()
        conf = {"sdi12_sensors": {"current": {"address": 1}}}

        def save(conf):
            pass

        message, response_code = rename.post(
            {"name": "new_name"},
            sensor_name="a_much_too_long_sensor_name",
            device_config=lambda: conf,
            save_callback=save,
        )
        self.assertEqual(response_code, 400)

    def test_invalid_regex(self):
        rename = Rename()
        conf = {"sdi12_sensors": {"current": {"address": 1}}}

        def save(conf):
            pass

        message, response_code = rename.post(
            {"name": "new_name"},
            sensor_name="invalid_!@#$%^&",
            device_config=lambda: conf,
            save_callback=save,
        )
        self.assertEqual(response_code, 400)

    def test_webserver_rename(self):
        body = json.dumps({"name": "new_name"})
        rdr = mockReader(
            [
                "POST /rename/water_sensor HTTP/1.0\r\n",
                HDR("Content-Length: {0}".format(len(body))),
                HDR("Content-Type: application/json"),
                HDRE,
                body,
            ]
        )
        wrt = mockWriter()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.server._handler(rdr, wrt))
        resp = json.loads(wrt.history[1])
        print("received " + wrt.history[1])
        self.assertTrue("message" in resp)
        expected = "renamed {0} to {1}".format("water_sensor", "new_name")
        self.assertEqual(expected, resp["message"])
        self.assertTrue("new_name" in self.device_config["sdi12_sensors"])


class DeleteTests(unittest.TestCase):

    device_config = config.read_config_file(
        "test/integration/device-config.test.json", sd=False
    )

    def save(self, config):
        self.device_config = config

    def setUp(self):
        self.server = webserver()
        self.server.conns[id(1)] = None
        self.server.add_resource(
            Delete,
            "/delete/<sensor_name>",
            device_config=lambda: self.device_config,
            save_callback=self.save,
        )

    def test_delete(self):
        # test without webserver
        delete = Delete()
        conf = {"sdi12_sensors": {"current": {"address": 1}}}
        expected = {"sdi12_sensors": {}}

        def save(config):
            self.assertEqual(config, expected)

        message, response_code = delete.post(
            {},
            sensor_name="current",
            device_config=lambda: conf,
            save_callback=save,
        )
        self.assertEqual(response_code, 200)

    def test_delete_invalid(self):
        # test without webserver

        delete = Delete()
        conf = {"sdi12_sensors": {"current": {"address": 1}}}

        def save(conf):
            pass

        # invalid sensor name
        message, response_code = delete.post(
            {},
            sensor_name="invalid",
            device_config=lambda: conf,
            save_callback=save,
        )
        self.assertEqual(response_code, 400)

    def test_webserver_delete(self):
        body = ""
        rdr = mockReader(
            [
                "POST /delete/water_sensor HTTP/1.0\r\n",
                HDR("Content-Length: {0}".format(len(body))),
                HDRE,
                body,
            ]
        )
        wrt = mockWriter()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.server._handler(rdr, wrt))
        resp = json.loads(wrt.history[1])
        print("received " + wrt.history[1])
        self.assertTrue("message" in resp)
        self.assertFalse("water_sensor" in self.device_config["sdi12_sensors"])
