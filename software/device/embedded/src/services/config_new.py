""" Config of the data recorder """

import json
import typing

CONFIG_FILE = "/services/config.json"
DYNAMIC_DATA_FILE = "/services/data.json"


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

    # todo: enabled

    # todo: address

    # todo: bootup_time

    # todo: record_interval

    # todo: first_record_at

    @readings
    def readings(self) -> typing.List[ReadingConfig]:
        """Get the readings config array"""

        return self.config[self.__readings]


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

    # todo: reading

    # todo: index

    # todo: multiplier

    # todo: offset

    # todo: unit

    # todo: uuid


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


class Sdi12Config:
    """The Sdi12 config of the data recorder"""

    __water_sensor = "water_sensor"

    def __init__(self, config):
        self.config = config

    @property
    def water_sensor(self) -> WaterSensorConfig:
        """Get the water sensor config"""

        return self.config[self.__water_sensor]


class BaseConfig:
    """The base data recorder config"""

    __version = "version"
    __devie_name = "device_name"
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

    # todo: devie_name

    # todo: device_id

    # todo: hw_revision

    # todo: send_interval

    # todo: first_send_at

    # todo: wifi_ssid

    # todo: wifi_password

    # todo: maintenance_mode

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
