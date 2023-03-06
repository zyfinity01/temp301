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

from django.db import models


class Device(models.Model):
    device_id = models.CharField(max_length=20, unique=True)
    device_name = models.CharField(max_length=50)
    hw_revision = models.CharField(max_length=10, default="4.0")

    send_interval = models.IntegerField(default=1)
    first_send_at = models.IntegerField(default=0)

    # MQTT Settings
    mqtt_host = models.CharField(max_length=100, default="test.mosquitto.org")
    mqtt_port = models.IntegerField(default=1883)
    mqtt_username = models.CharField(max_length=50)
    mqtt_password = models.CharField(max_length=50)
    mqtt_parent_topic = models.CharField(
        max_length=100, default="test/environmentMonitoring/"
    )

    # Monitor My Watershed Settings
    mmw_auth_token = models.CharField(max_length=50)
    mmw_sampling_feature = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.device_id} ({self.device_name})"


class SDI12Sensor(models.Model):
    name = models.CharField(max_length=25)
    enabled = models.BooleanField()
    address = models.IntegerField()
    bootup_time = models.IntegerField(default=0)
    record_interval = models.IntegerField(default=10)
    first_record_at = models.IntegerField(default=0)

    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="sdi12_sensors"
    )

    def __str__(self):
        return f"{self.name} ({self.address})"


class Reading(models.Model):
    reading = models.CharField(max_length=20)
    index = models.IntegerField()
    multiplier = models.IntegerField()
    offset = models.IntegerField()
    unit = models.CharField(max_length=10)
    uuid = models.CharField(max_length=50)

    sdi12_sensor = models.ForeignKey(
        SDI12Sensor, on_delete=models.CASCADE, related_name="readings"
    )

    def __str__(self):
        return f"{self.reading} ({self.index})"
