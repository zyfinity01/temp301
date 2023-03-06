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

from .models import Device, SDI12Sensor, Reading
from rest_framework import serializers


class ReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reading
        fields = "__all__"
        # exclude = ["sdi12_sensor", "id"]


class SDI12SensorSerializer(serializers.ModelSerializer):
    readings = ReadingSerializer(many=True, read_only=True)

    class Meta:
        model = SDI12Sensor
        fields = "__all__"
        # exclude = ["device", "id"]


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    sdi12_sensors = SDI12SensorSerializer(many=True)

    class Meta:
        model = Device
        fields = "__all__"

    def create(self, validated_data):
        sensors = validated_data.pop("sdi12_sensors")
        device = Device.objects.create(**validated_data)
        for sensor_data in sensors:
            readings = sensor_data.pop("readings")
            sensor = SDI12Sensor.objects.create(device=device, **sensor_data)
            for reading_data in readings:
                Reading.objects.create(sdi12_sensor=sensor, **reading_data)
        return device

    # def update(self, instance, validated_data):
    #     sensors = validated_data.pop("sdi12_sensors")
    #     device = Device.objects.update(**validated_data)
    #     for sensor_data in sensors:
    #         readings = sensor_data.pop("readings")
    #         sensor = SDI12Sensor.objects.update(device=device, **sensor_data)
    #         for reading_data in readings:
    #             Reading.objects.update(sdi12_sensor=sensor, **reading_data)
    #     return device

    # def update(self, instance, validated_data):
    #     # TODO: this won't add new sensors or readings

    #     sdi12_sensors = validated_data.pop("sdi12_sensors")
    #     for sensor_data in sdi12_sensors:
    #         sensor = SDI12Sensor.objects.get(device=instance)
    #         readings = sensor_data.pop("readings")

    #         for reading_data in readings:
    #             reading = Reading.objects.filter(
    #                 sdi12_sensor=sensor, index=reading_data["index"]
    #             )  # TODO: how to ensure readings have unique index in ORM?
    #             reading.update(**reading_data)

    #         # set rest of sensor data
    #         for key, value in sensor_data.items():
    #             setattr(sensor, key, value)

    #         sensor.save()

    #     for key, value in validated_data.items():
    #         setattr(instance, key, value)

    #     return instance

    #     ## TODO this isn't quite working. Fix tomorrow and then work on device code
