""" Config of the data recorder """

import json
import typing

CONFIG_FILE = "/services/config.json"
TEST_CONFIG_FILE = "/services/test-config.json"
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
    def readings(self, values: typing.List[ReadingConfig]):
        """Set the readings config array"""
        configs = [value.config for value in values]
        self.config[self.__readings] = configs


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
        self.config[self.__water_sensor] = value.config


class MqttConfig:
    """The MQTT config of the data recorder"""

    __host = "host"
    __port = "port"
    __username = "username"
    __password = "password"
    __parent_topic = "parent_topic"

    def __init__(self, save: typing.Callable[[], None], config):
        self.save = save
        self.config = config

    @property
    def host(self) -> str:
        """Get the host config"""
        return self.config[self.__host]

    @host.setter
    def host(self, value: str):
        """Set the host config"""
        self.config[self.__host] = value

    @property
    def port(self) -> int:
        """Get the port config"""
        return self.config[self.__port]

    @port.setter
    def port(self, value: int):
        """Set the port config"""
        self.config[self.__port] = value

    @property
    def username(self) -> str:
        """Get the username config"""
        return self.config[self.__username]

    @username.setter
    def username(self, value: str):
        """Set the username config"""
        self.config[self.__username] = value

    @property
    def password(self) -> str:
        """Get the password config"""
        return self.config[self.__password]

    @password.setter
    def password(self, value: str):
        """Set the password config"""
        self.config[self.__password] = value

    @property
    def parent_topic(self) -> str:
        """Get the parent_topic config"""
        return self.config[self.__parent_topic]

    @parent_topic.setter
    def parent_topic(self, value: str):
        """Set the parent_topic config"""
        self.config[self.__parent_topic] = value


class MmwConfig:
    """The MMW config of the data recorder"""

    __auth_token = "auth_token"
    __sampling_feature = "sampling_feature"

    def __init__(self, save: typing.Callable[[], None], config):
        self.save = save
        self.config = config

    @property
    def auth_token(self) -> str:
        """Get the auth_token config"""
        return self.config[self.__auth_token]

    @auth_token.setter
    def auth_token(self, value: str):
        """Set the auth_token config"""
        self.config[self.__auth_token] = value
        self.save()

    @property
    def sampling_feature(self) -> str:
        """Get the sampling_feature config"""
        return self.config[self.__sampling_feature]

    @sampling_feature.setter
    def sampling_feature(self, value: str):
        """Set the sampling_feature config"""
        self.config[self.__sampling_feature] = value
        self.save()


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

    def __init__(self, file_name: str, config):
        self.file_name = file_name
        self.config = config        

    def save(self):
        """Save the base config"""
        save_config(self.file_name, self.config)

    @property
    def version(self) -> str:
        """Get the version setting"""
        return self.config[self.__version]

    @version.setter
    def version(self, value: str):
        """Set the version setting"""
        self.config[self.__version] = value
        self.save()

    @property
    def device_name(self) -> str:
        """Get the device name setting"""
        return self.config[self.__device_name]

    @device_name.setter
    def device_name(self, value: str):
        """Set the device name setting"""
        self.config[self.__device_name] = value
        self.save()

    @property
    def device_id(self) -> str:
        """Get the device id setting"""
        return self.config[self.__device_id]

    @device_id.setter
    def device_id(self, value: str):
        """Set the device id setting"""
        self.config[self.__device_id] = value
        self.save()

    @property
    def hw_revision(self) -> str:
        """Get the hardware revision setting"""
        return self.config[self.__hw_revision]

    @hw_revision.setter
    def hw_revision(self, value: str):
        """Set the hardware revision setting"""
        self.config[self.__hw_revision] = value
        self.save()

    @property
    def send_interval(self) -> int:
        """Get the send interval setting"""
        return self.config[self.__send_interval]

    @send_interval.setter
    def send_interval(self, value: int):
        """Set the send interval setting"""
        self.config[self.__send_interval] = value
        self.save()

    @property
    def first_send_at(self) -> str:
        """Get the first send at setting"""
        return self.config[self.__first_send_at]

    @first_send_at.setter
    def first_send_at(self, value: str):
        """Set the first send at setting"""
        self.config[self.__first_send_at] = value
        self.save()

    @property
    def wifi_ssid(self) -> str:
        """Get the wifi ssid setting"""
        return self.config[self.__wifi_ssid]

    @wifi_ssid.setter
    def wifi_ssid(self, value: str):
        """Set the wifi ssid setting"""
        self.config[self.__wifi_ssid] = value
        self.save()

    @property
    def wifi_password(self) -> str:
        """Get the wifi password setting"""
        return self.config[self.__wifi_password]

    @wifi_password.setter
    def wifi_password(self, value: str):
        """Set the wifi password setting"""
        self.config[self.__wifi_password] = value
        self.save()

    @property
    def maintenance_mode(self) -> bool:
        """Get the maintenance mode setting"""
        return self.config[self.__maintenance_mode]

    @maintenance_mode.setter
    def maintenance_mode(self, value: bool):
        """Set the maintenance mode setting"""
        self.config[self.__maintenance_mode] = value
        self.save()

    @property
    def test_mode(self) -> bool:
        """Get the test_mode config"""
        return self.config[self.__test_mode]

    @test_mode.setter
    def test_mode(self, value: bool):
        """Set the test_mode config"""
        self.config[self.__test_mode] = value
        self.save()

    @property
    def mqtt_settings(self) -> MqttConfig:
        """Get the MQTT settings"""
        return MqttConfig(self.save, self.config[self.__mqtt_settings])

    @mqtt_settings.setter
    def mqtt_settings(self, value: MqttConfig):
        """Set the MQTT settings"""
        self.config[self.__mqtt_settings] = value.config
        self.save()

    @property
    def mmw_settings(self) -> MmwConfig:
        """Get the MMW settings"""
        return MmwConfig(self.save, self.config[ self.__mmw_settings])

    @mmw_settings.setter
    def mmw_settings(self, value: MmwConfig):
        """Set the MMW settings"""
        self.config[self.__mmw_settings] = value.config
        self.save()

    @property
    def sdi12_sensors(self) -> Sdi12Config:
        """Get the SDI12 settings"""
        return Sdi12Config(self.config[self.__sdi12_sensors])

    @sdi12_sensors.setter
    def sdi12_sensors(self, value: Sdi12Config):
        """Set the SDI12 settings"""
        self.config[self.__sdi12_sensors] = value.config
        self.save()

    @property
    def water_sensor(self) -> WaterSensorConfig:
        """Get the water_sensor settings"""
        return WaterSensorConfig(self.config[self.__water_sensor])

    @water_sensor.setter
    def water_sensor(self, value: WaterSensorConfig):
        """Set the water_sensor settings"""
        self.config[self.__water_sensor] = value.config
        self.save()


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

    @property
    def last_updated(self) -> int:
        """Get the last_updated config"""
        return self.config[self.__last_updated]

    @last_updated.setter
    def last_updated(self, value: int):
        """Set the last_updated config"""
        self.config[self.__last_updated] = value

    @property
    def last_transmitted(self) -> int:
        """Get the last_transmitted config"""
        return self.config[self.__last_transmitted]

    @last_transmitted.setter
    def last_transmitted(self, value: int):
        """Set the last_transmitted config"""
        self.config[self.__last_transmitted] = value

    @property
    def battery_level(self) -> int:
        """Get the battery_level config"""
        return self.config[self.__battery_level]

    @battery_level.setter
    def battery_level(self, value: int):
        """Set the battery_level config"""
        self.config[self.__battery_level] = value

    @property
    def coverage_level(self) -> int:
        """Get the coverage_level config"""
        return self.config[self.__coverage_level]

    @coverage_level.setter
    def coverage_level(self, value: int):
        """Set the coverage_level config"""
        self.config[self.__coverage_level] = value

    @property
    def messages_sent(self) -> int:
        """Get the messages_sent config"""
        return self.config[self.__messages_sent]

    @messages_sent.setter
    def messages_sent(self, value: int):
        """Set the messages_sent config"""
        self.config[self.__messages_sent] = value

    @property
    def failed_transmissions(self) -> int:
        """Get the failed_transmissions config"""
        return self.config[self.__failed_transmissions]

    @failed_transmissions.setter
    def failed_transmissions(self, value: int):
        """Set the failed_transmissions config"""
        self.config[self.__failed_transmissions] = value

    @property
    def free_sd_space(self) -> int:
        """Get the free_sd_space config"""
        return self.config[self.__free_sd_space]

    @free_sd_space.setter
    def free_sd_space(self, value: int):
        """Set the free_sd_space config"""
        self.config[self.__free_sd_space] = value

    @property
    def rainfall(self) -> typing.List(int):
        """Get the rainfall config"""
        return self.config[self.__rainfall]

    @rainfall.setter
    def rainfall(self, value: typing.List(int)):
        """Set the rainfall config"""
        self.config[self.__rainfall] = value

    @property
    def date_time(self) -> typing.List(int):
        """Get the date_time config"""
        return self.config[self.__date_time]

    @date_time.setter
    def date_time(self, value: typing.List(int)):
        """Set the date_time config"""
        self.config[self.__date_time] = value


def read_config(file_name: str = CONFIG_FILE) -> BaseConfig:
    """Returns an instance of the base config class"""

    with open(file_name, encoding="utf-8") as handle:
        contents = handle.read()
        data = json.loads(contents)
        return BaseConfig(file_name, data)

def read_data(file_name: str = DYNAMIC_DATA_FILE) -> DataConfig:
    """Returns an instance of the data config class"""

    with open(file_name, encoding="utf-8") as handle:
        contents = handle.read()
        data = json.loads(contents)
        return DataConfig(data)

def save_config(file_name: str, config):
    """Saves the config dictionary as json to the given file"""
    
    with open(file_name, 'w') as handle:
        contents = json.dumps(config, indent=4)
        handle.write(contents)
