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

from configservice.models import Reading, SDI12Sensor, Device

# quick script to initially seed a dev DB with data


def run():
    device = Device.objects.create(
        device_name="test device",
        device_id="id",
        hw_revision="rev::4",
        send_interval=1,
        first_send_at=1,
        mqtt_host="test-host",
        mqtt_port=1000,
        mqtt_username="username",
        mqtt_password="password",
        mqtt_parent_topic="test/",
        mmw_auth_token="test token",
        mmw_sampling_feature="abdef",
    )

    sensor = SDI12Sensor.objects.create(
        enabled=True,
        address=1,
        bootup_time=1,
        record_interval=10,
        first_record_at=0,
        device=device,
    )

    reading = Reading.objects.create(
        reading="test",
        index=0,
        multiplier=1,
        offset=0,
        unit=10,
        uuid="abcdef",
        sdi12_sensor=sensor,
    )

    print("Test device created in the database.")
