""" Config of the data recorder """

import json
import typing

CONFIG_FILE = "/services/config.json"
DYNAMIC_DATA_FILE = "/services/data.json"


class ReadingConfig:
    """The reading config of the Sdi12"""

    __reading = "reading"
    __index = "index"
    __multiplier = "multiplier"
    __offset = "offset"
    __unit = "unit"
    __uuid = "uuid"

    def __init__(self, config):
        self.config = config

    @property
    def reading(self) -> str:
        """Get the reading config"""

        return self.config[self.__reading]

    @reading.setter
    def reading(self, value: str):
        """Set the reading config"""

        self.config[self.__reading] = value

    @property
    def index(self) -> int:
        """Get the index config"""

        return self.config[self.__index]

    @index.setter
    def index(self, value: int):
        """Set the index config"""

        self.config[self.__index] = value

    @property
    def multiplier(self) -> int:
        """Get the multiplier config"""

        return self.config[self.__multiplier]

    @multiplier.setter
    def multiplier(self, value: int):
        """Set the multiplier config"""

        self.config[self.__multiplier] = value

    @property
    def offset(self) -> int:
        """Get the offset config"""

        return self.config[self.__offset]

    @offset.setter
    def offset(self, value: int):
        """Set the offset config"""

        self.config[self.__offset] = value

    @property
    def unit(self) -> str:
        """Get the unit config"""

        return self.config[self.__unit]

    @unit.setter
    def unit(self, value: str):
        """Set the unit config"""

        self.config[self.__unit] = value

    @property
    def uuid(self) -> str:
        """Get the UUID config"""

        return self.config[self.__uuid]

    @uuid.setter
    def uuid(self, value: str):
        """Set the UUID config"""

        self.config[self.__uuid] = value


class WaterSensorConfig:
    """The water sensor config of the Sdi12"""

    __enabled = "enabled"
    __address = "address"
    __bootup_time = "bootup_time"
    __record_interval = "record_interval"
    __first_record_at = "first_record_at"
    __readings = "readings"

    def __init__(self, config):
        self.config = config

    @property
    def enabled(self) -> bool:
        """Get the enabled config"""

        return self.config[self.__enabled]

    @enabled.setter
    def enabled(self, value: bool):
        """Set the enabled config"""

        self.config[self.__enabled] = value

    @property
    def address(self) -> int:
        """Get the address config"""

        return self.config[self.__address]

    @address.setter
    def address(self, value: int):
        """Set the address config"""

        self.config[self.__address] = value

    @property
    def bootup_time(self) -> int:
        """Get the bootup_time config"""

        return self.config[self.__bootup_time]

    @bootup_time.setter
    def bootup_time(self, value: int):
        """Set the bootup_time config"""

        self.config[self.__bootup_time] = value

    @property
    def record_interval(self) -> int:
        """Get the record_interval config"""

        return self.config[self.__record_interval]

    @record_interval.setter
    def record_interval(self, value: int):
        """Set the record_interval config"""

        self.config[self.__record_interval] = value

    @property
    def first_record_at(self) -> int:
        """Get the first_record_at config"""

        return self.config[self.__first_record_at]

    @first_record_at.setter
    def first_record_at(self, value: int):
        """Get the first_record_at config"""

        self.config[self.__first_record_at] = value

    @property
    def readings(self) -> typing.List[ReadingConfig]:
        """Get the readings config array"""

        readings = self.config[self.__readings]
        return [ReadingConfig(reading) for reading in readings]

    @readings.setter
    def readings(self, value: typing.List[ReadingConfig]):
        """Set the readings config array"""

        self.config[self.__readings] = value


class Sdi12Config:
    """The Sdi12 config of the data recorder"""

    __water_sensor = "water_sensor"

    def __init__(self, config):
        self.config = config

    @property
    def water_sensor(self) -> WaterSensorConfig:
        """Get the water sensor config"""

        return WaterSensorConfig(self.config[self.__water_sensor])

    @water_sensor.setter
    def water_sensor(self, value: WaterSensorConfig):
        """Set the water sensor config"""

        self.config[self.__water_sensor] = value


class MqttConfig:
    """The MQTT config of the data recorder"""

    __host = "host"
    __port = "port"
    __username = "username"
    __password = "password"
    __parent_topic = "parent_topic"

    def __init__(self, config):
        self.config = config

    # todo: host

    # todo: port

    # todo: username

    # todo: password

    # todo: parent_topic


class MmwConfig:
    """The MMW config of the data recorder"""

    __auth_token = "auth_token"
    __sampling_feature = "sampling_feature"

    def __init__(self, config):
        self.config = config

    # todo: auth_token

    # todo: sampling_feature


class BaseConfig:
    """The base data recorder config"""

    __version = "version"
    __device_name = "device_name"
    __device_id = "device_id"
    __hw_revision = "hw_revision"
    __send_interval = "send_interval"
    __first_send_at = "first_send_at"
    __wifi_ssid = "wifi_ssid"
    __wifi_password = "wifi_password"
    __maintenance_mode = "maintenance_mode"
    __test_mode = "test_mode"
    __mqtt_settings = "mqtt_settings"
    __mmw_settings = "mmw_settings"
    __sdi12_sensors = "sdi12_sensors"
    __water_sensor = "water_sensor"

    def __init__(self, config):
        self.config = config

    @property
    def version(self) -> str:
        """Get the version setting"""

        return self.config[self.__version]

    @version.setter
    def version(self, value: str) -> str:
        """Set the version setting"""

        self.config[self.__version] = value

    # todo: device_name
    @property
    def device_name(self) -> str:
        """Get the device name setting"""

        return self.config[self.__device_name]

    @device_name.setter
    def device_name(self, value: str) -> str:
        """Set the device name setting"""

        self.config[self.__device_name] = value

    # todo: device_id
    @property
    def device_id(self) -> str:
        """Get the device id setting"""

        return self.config[self.__device_id]

    @device_id.setter
    def device_id(self, value: str) -> str:
        """Set the device id setting"""

        self.config[self.__device_id] = value

    # todo: hw_revision
    @property
    def hw_revision(self) -> str:
        """Get the hardware revision setting"""

        return self.config[self.__hw_revision]

    @hw_revision.setter
    def hw_revision(self, value: str) -> str:
        """Set the hardware revision setting"""

        self.config[self.__hw_revision] = value

    # todo: send_interval
    @property
    def send_interval(self) -> int:
        """Get the send interval setting"""

        return self.config[self.__send_interval]

    @send_interval.setter
    def send_interval(self, value: int) -> int:
        """Set the send interval setting"""

        self.config[self.__send_interval] = value

    # todo: first_send_at
    @property
    def first_send_at(self) -> str:
        """Get the first send at setting"""

        return self.config[self.__first_send_at]

    @first_send_at.setter
    def first_send_at(self, value: str) -> str:
        """Set the first send at setting"""

        self.config[self.__first_send_at] = value

    # todo: wifi_ssid
    @property
    def wifi_ssid(self) -> str:
        """Get the wifi ssid setting"""

        return self.config[self.__wifi_ssid]

    @wifi_ssid.setter
    def wifi_ssid(self, value: str) -> str:
        """Set the wifi ssid setting"""

        self.config[self.__wifi_ssid] = value

    # todo: wifi_password
    @property
    def wifi_password(self) -> str:
        """Get the wifi password setting"""

        return self.config[self.__wifi_password]

    @wifi_password.setter
    def wifi_password(self, value: str) -> str:
        """Set the wifi password setting"""

        self.config[self.__wifi_password] = value

    # todo: maintenance_mode
    @property
    def maintenance_mode(self) -> bool:
        """Get the maintenance mode setting"""

        return self.config[self.__maintenance_mode]

    @maintenance_mode.setter
    def maintenance_mode(self, value: bool) -> bool:
        """Set the maintenance mode setting"""

        self.config[self.__maintenance_mode] = value

    # todo: test_mode

    @property
    def mqtt_settings(self) -> MqttConfig:
        """Get the MQTT settings"""

        return self.config[self.__mqtt_settings]

    @mmw_settings.setter
    def mmw_settings(self) -> MmwConfig:
        """Set the MQTT settings"""

        return self.config[self.__mmw_settings]

    @property
    def sdi12_sensors(self) -> Sdi12Config:
        """Get the SDI12 settings"""

        return self.config[self.__sdi12_sensors]

    @sdi12_sensors.setter
    def water_senor(self) -> WaterSensorConfig:
        """Set the SDI12 settings"""

        return self.config[self.__water_sensor]


class DataConfig:
    """The dynamic data config of the data recorder"""

    __last_updated = "last_updated"
    __last_transmitted = "last_transmitted"
    __battery_level = "battery_level"
    __coverage_level = "coverage_level"
    __messages_sent = "messages_sent"
    __failed_transmissions = "failed_transmissions"
    __free_sd_space = "free_sd_space"
    __rainfall = "rainfall"
    __date_time = "date_time"

    def __init__(self, config):
        self.config = config

    # todo: last_updated

    # todo: last_transmitted

    # todo: battery_level

    # todo: coverage_level

    # todo: message_sent

    # todo: failed_transmissions

    # todo: free_sd_space

    # todo: rainfall

    # todo: date_time


def read_config(file_name: str = CONFIG_FILE) -> BaseConfig:
    """Returns an instance of the base config class"""

    with open(file_name, encoding="utf-8") as handle:
        contents = handle.read()
        data = json.loads(contents)
        return BaseConfig(data)


def read_data(file_name: str = DYNAMIC_DATA_FILE) -> DataConfig:
    """Returns an instance of the data config class"""

    with open(file_name, encoding="utf-8") as handle:
        contents = handle.read()
        data = json.loads(contents)
        return DataConfig(data)
