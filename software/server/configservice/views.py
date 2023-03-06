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

from django.shortcuts import render

# Rest framework imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, permissions

from configservice.serializers import (
    DeviceSerializer,
    ReadingSerializer,
    SDI12SensorSerializer,
)

from .models import Device, Reading, SDI12Sensor


class DeviceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows devices to be viewed or edited.
    """

    queryset = Device.objects.all().order_by("device_name")
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]


class SensorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows sensors to be viewed or edited.
    """

    queryset = SDI12Sensor.objects.all()
    serializer_class = SDI12SensorSerializer
    permission_classes = [permissions.IsAuthenticated]

    # def get_queryset(self):
    #     print(self.kwargs)
    #     return SDI12Sensor.objects.filter(name=self.kwargs['sdi12_sensors_pk'])


class ReadingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows devices to be viewed or edited.
    """

    queryset = Reading.objects.all()
    serializer_class = ReadingSerializer
    permission_classes = [permissions.IsAuthenticated]
