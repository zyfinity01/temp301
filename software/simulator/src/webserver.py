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

from flask import Flask, send_from_directory
from flask_restful import Resource, Api, request
from flask_cors import CORS
import json
import os
import random
import time

CONFIG_DIR = "../../device/embedded/src/services/"
WEBAPP_DIR = "../../device/webapp/build/"

app = Flask(__name__, static_folder=WEBAPP_DIR)
api = Api(app)
CORS(app)


def loadjson(filename, local=False):
    """
    Load a JSON file as a dictionary.

    Arguments:
        filename (str): name of the JSON file to load
        local (bool): if enabled, load from script directory (mainly for azure deployment purposes),
                        otherwise find the file in the relative device code path

    Returns:
        dict
    """
    path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            CONFIG_DIR + "{filename}".format(filename=filename)
            if not local
            else filename,
        )
    )
    print(" * Loading JSON from", os.path.relpath(path))
    with open(path, "r") as f_in:
        return json.load(f_in)


# Check to see if $LOCAL_CONFIG env var is set (best way for azure web apps)
use_local_configs = True if "LOCAL_CONFIG" in os.environ else False

# load the example device configs from the device/src directory
device_config = loadjson("config.example.json", use_local_configs)
data_config = loadjson("data.example.json", use_local_configs)


class ConfigMock(Resource):
    def get(self):
        return device_config

    def post(self):
        print("reading")
        json_data = request.get_json(force=True)
        print(json_data)
        return "success"


class SensorMock(Resource):
    def post(self, sensor):
        print(request.get_data())
        print(sensor)
        return {"message": "updated successfully"}


class RenameSensorMock(Resource):
    def post(self, sensor):
        print("Rename!")
        return {"message": "renamed successfully"}


class DeleteSensorMock(Resource):
    def post(self, sensor):
        print("delete!", sensor)
        return {"message": "deleted successfully"}


class TestMock(Resource):
    def get(self, sensor):
        time.sleep(2)
        return {
            "response": {
                "voltage": random.randint(10, 13),
                "temperature": random.randint(20, 40),
            }
        }


class DataMock(Resource):
    def get(self):
        return data_config


class SensorReadingMock(Resource):
    def get(self):
        command = request.args.get("command")
        if not command:
            return {"error": "no `command` supplied in query params"}, 400
        reading = random.randint(0, 100)
        # sleep 5 seconds
        time.sleep(5)
        return {"response": reading, "command": command}


@app.route("/<path:path>")
def send_static_file(path):
    return send_from_directory(WEBAPP_DIR, path)


@app.route("/")
@app.route("/index.html")
def index():
    return app.send_static_file("index.html")


api.add_resource(ConfigMock, "/config")
api.add_resource(SensorMock, "/config/sdi12/update/<string:sensor>")
api.add_resource(RenameSensorMock, "/config/sdi12/rename/<string:sensor>")
api.add_resource(DeleteSensorMock, "/config/sdi12/delete/<string:sensor>")
api.add_resource(TestMock, "/config/sdi12/test/<string:sensor>")
api.add_resource(DataMock, "/data")
api.add_resource(SensorReadingMock, "/monitor")

if __name__ == "__main__":
    app.run(debug=True)
