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

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

try:
    import asyn
    import drivers.sdi12
except:
    pass


def gather_sensors(sdi, sensors, wake_times):
    """
    Gather a list of functions as Gatherables to read the sensor data

    Args:
        sdi (dict): SDI-12 driver
        sensors (dict): Configuration of all sensors
        wake_times (list): List of times the sensors were woken

    Returns:
        Tuple containing sensor names and array of Gatherables
    """
    sensor_names = list(sensors.keys())
    gatherables = [
        asyn.Gatherable(
            drivers.sdi12.read_sensor, sensors[name], sdi, wake_times[i], name=name
        )
        for i, name in enumerate(sensor_names)
    ]
    return sensor_names, gatherables


def convert_readings(results: tuple, sensor: dict):
    """
    Convert a tuple of readings for a particular sensor to a dict

    Args:
        results (tuple): sensor reading results
        sensor (dict): sensor config

    Returns:
        dictionary of reading name -> result mapping
    """

    if not results:
        return {}

    if not sensor or "readings" not in sensor:
        raise ValueError("Invalid sensor dict")

    readings = sensor["readings"]

    if len(results) != len(readings):
        raise ValueError("Result and readings not same length")

    return {reading["reading"]: result for reading, result in zip(readings, results)}
