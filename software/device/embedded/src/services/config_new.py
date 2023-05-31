""" Config of the data recorder """

import json

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

    def __init__(self, save, config):
        self.save = save
        self.config = config

    @property
    def reading(self):
        """Get the reading config"""
        return self.config[self.__reading]

    @reading.setter
    def reading(self, value):
        """Set the reading config"""
        self.config[self.__reading] = value
        self.save()

    @property
    def index(self):
        """Get the index config"""
        return self.config[self.__index]

    @index.setter
    def index(self, value):
        """Set the index config"""
        self.config[self.__index] = value
        self.save()

    @property
    def multiplier(self):
        """Get the multiplier config"""
        return self.config[self.__multiplier]

    @multiplier.setter
    def multiplier(self, value):
        """Set the multiplier config"""
        self.config[self.__multiplier] = value
        self.save()

    @property
    def offset(self):
        """Get the offset config"""
        return self.config[self.__offset]

    @offset.setter
    def offset(self, value):
        """Set the offset config"""
        self.config[self.__offset] = value
        self.save()

    @property
    def unit(self):
        """Get the unit config"""
        return self.config[self.__unit]

    @unit.setter
    def unit(self, value):
        """Set the unit config"""
        self.config[self.__unit] = value
        self.save()

    @property
    def uuid(self):
        """Get the UUID config"""
        return self.config[self.__uuid]

    @uuid.setter
    def uuid(self, value):
        """Set the UUID config"""
        self.config[self.__uuid] = value
        self.save()


class WaterSensorConfig:
    """The water sensor config of the Sdi12"""

    __enabled = "enabled"
    __address = "address"
    __bootup_time = "bootup_time"
    __record_interval = "record_interval"
    __first_record_at = "first_record_at"
    __readings = "readings"

    def __init__(self, save, config):
        self.save = save
        self.config = config

    @property
    def enabled(self):
        """Get the enabled config"""
        return self.config[self.__enabled]

    @enabled.setter
    def enabled(self, value):
        """Set the enabled config"""
        self.config[self.__enabled] = value
        self.save()

    @property
    def address(self):
        """Get the address config"""
        return self.config[self.__address]

    @address.setter
    def address(self, value):
        """Set the address config"""
        self.config[self.__address] = value
        self.save()

    @property
    def bootup_time(self):
        """Get the bootup_time config"""
        return self.config[self.__bootup_time]

    @bootup_time.setter
    def bootup_time(self, value):
        """Set the bootup_time config"""
        self.config[self.__bootup_time] = value
        self.save()

    @property
    def record_interval(self):
        """Get the record_interval config"""
        return self.config[self.__record_interval]

    @record_interval.setter
    def record_interval(self, value):
        """Set the record_interval config"""
        self.config[self.__record_interval] = value
        self.save()

    @property
    def first_record_at(self):
        """Get the first_record_at config"""
        return self.config[self.__first_record_at]

    @first_record_at.setter
    def first_record_at(self, value):
        """Get the first_record_at config"""
        self.config[self.__first_record_at] = value
        self.save()

    @property
    def readings(self):
        """Get the readings config array"""
        readings = self.config[self.__readings]
        return [ReadingConfig(self.save, reading) for reading in readings]

    @readings.setter
    def readings(self, values):
        """Set the readings config array"""
        configs = [value.config for value in values]
        self.config[self.__readings] = configs
        self.save()


class Sdi12Config:
    """The Sdi12 config of the data recorder"""

    __water_sensor = "water_sensor"

    def __init__(self, save, config):
        self.save = save
        self.config = config

    @property
    def water_sensor(self):
        """Get the water sensor config"""
        return WaterSensorConfig(self.save, self.config[self.__water_sensor])

    @water_sensor.setter
    def water_sensor(self, value):
        """Set the water sensor config"""
        self.config[self.__water_sensor] = value.config
        self.save()


class MqttConfig:
    """The MQTT config of the data recorder"""

    __host = "host"
    __port = "port"
    __username = "username"
    __password = "password"
    __parent_topic = "parent_topic"

    def __init__(self, save, config):
        self.save = save
        self.config = config

    @property
    def host(self):
        """Get the host config"""
        return self.config[self.__host]

    @host.setter
    def host(self, value):
        """Set the host config"""
        self.config[self.__host] = value
        self.save()

    @property
    def port(self):
        """Get the port config"""
        return self.config[self.__port]

    @port.setter
    def port(self, value):
        """Set the port config"""
        self.config[self.__port] = value
        self.save()

    @property
    def username(self):
        """Get the username config"""
        return self.config[self.__username]

    @username.setter
    def username(self, value):
        """Set the username config"""
        self.config[self.__username] = value
        self.save()

    @property
    def password(self):
        """Get the password config"""
        return self.config[self.__password]

    @password.setter
    def password(self, value):
        """Set the password config"""
        self.config[self.__password] = value
        self.save()

    @property
    def parent_topic(self):
        """Get the parent_topic config"""
        return self.config[self.__parent_topic]

    @parent_topic.setter
    def parent_topic(self, value):
        """Set the parent_topic config"""
        self.config[self.__parent_topic] = value
        self.save()


class MmwConfig:
    """The MMW config of the data recorder"""

    __auth_token = "auth_token"
    __sampling_feature = "sampling_feature"

    def __init__(self, save, config):
        self.save = save
        self.config = config

    @property
    def auth_token(self):
        """Get the auth_token config"""
        return self.config[self.__auth_token]

    @auth_token.setter
    def auth_token(self, value):
        """Set the auth_token config"""
        self.config[self.__auth_token] = value
        self.save()

    @property
    def sampling_feature(self):
        """Get the sampling_feature config"""
        return self.config[self.__sampling_feature]

    @sampling_feature.setter
    def sampling_feature(self, value):
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

    def __init__(self, file_name, config):
        self.file_name = file_name
        self.config = config

    def save(self):
        """Save the base config"""
        save_config(self.file_name, self.config)

    @property
    def version(self):
        """Get the version setting"""
        return self.config[self.__version]

    @version.setter
    def version(self, value):
        """Set the version setting"""
        self.config[self.__version] = value
        self.save()

    @property
    def device_name(self):
        """Get the device name setting"""
        return self.config[self.__device_name]

    @device_name.setter
    def device_name(self, value):
        """Set the device name setting"""
        self.config[self.__device_name] = value
        self.save()

    @property
    def device_id(self):
        """Get the device id setting"""
        return self.config[self.__device_id]

    @device_id.setter
    def device_id(self, value):
        """Set the device id setting"""
        self.config[self.__device_id] = value
        self.save()

    @property
    def hw_revision(self):
        """Get the hardware revision setting"""
        return self.config[self.__hw_revision]

    @hw_revision.setter
    def hw_revision(self, value):
        """Set the hardware revision setting"""
        self.config[self.__hw_revision] = value
        self.save()

    @property
    def send_interval(self):
        """Get the send interval setting"""
        return self.config[self.__send_interval]

    @send_interval.setter
    def send_interval(self, value):
        """Set the send interval setting"""
        self.config[self.__send_interval] = value
        self.save()

    @property
    def first_send_at(self):
        """Get the first send at setting"""
        return self.config[self.__first_send_at]

    @first_send_at.setter
    def first_send_at(self, value):
        """Set the first send at setting"""
        self.config[self.__first_send_at] = value
        self.save()

    @property
    def wifi_ssid(self):
        """Get the wifi ssid setting"""
        return self.config[self.__wifi_ssid]

    @wifi_ssid.setter
    def wifi_ssid(self, value):
        """Set the wifi ssid setting"""
        self.config[self.__wifi_ssid] = value
        self.save()

    @property
    def wifi_password(self):
        """Get the wifi password setting"""
        return self.config[self.__wifi_password]

    @wifi_password.setter
    def wifi_password(self, value):
        """Set the wifi password setting"""
        self.config[self.__wifi_password] = value
        self.save()

    @property
    def maintenance_mode(self):
        """Get the maintenance mode setting"""
        return self.config[self.__maintenance_mode]

    @maintenance_mode.setter
    def maintenance_mode(self, value):
        """Set the maintenance mode setting"""
        self.config[self.__maintenance_mode] = value
        self.save()

    @property
    def test_mode(self):
        """Get the test_mode config"""
        return self.config[self.__test_mode]

    @test_mode.setter
    def test_mode(self, value):
        """Set the test_mode config"""
        self.config[self.__test_mode] = value
        self.save()

    @property
    def mqtt_settings(self):
        """Get the MQTT settings"""
        return MqttConfig(self.save, self.config[self.__mqtt_settings])

    @mqtt_settings.setter
    def mqtt_settings(self, value):
        """Set the MQTT settings"""
        self.config[self.__mqtt_settings] = value.config
        self.save()

    @property
    def mmw_settings(self):
        """Get the MMW settings"""
        return MmwConfig(self.save, self.config[self.__mmw_settings])

    @mmw_settings.setter
    def mmw_settings(self, value):
        """Set the MMW settings"""
        self.config[self.__mmw_settings] = value.config
        self.save()

    @property
    def sdi12_sensors(self):
        """Get the SDI12 settings"""
        return Sdi12Config(self.save, self.config[self.__sdi12_sensors])

    @sdi12_sensors.setter
    def sdi12_sensors(self, value):
        """Set the SDI12 settings"""
        self.config[self.__sdi12_sensors] = value.config
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

    def __init__(self, file_name: str, config):
        self.file_name = file_name
        self.config = config

    def save(self):
        """Save the data config"""
        save_config(self.file_name, self.config)

    @property
    def last_updated(self):
        """Get the last_updated config"""
        return self.config[self.__last_updated]

    @last_updated.setter
    def last_updated(self, value):
        """Set the last_updated config"""
        self.config[self.__last_updated] = value
        self.save()

    @property
    def last_transmitted(self):
        """Get the last_transmitted config"""
        return self.config[self.__last_transmitted]

    @last_transmitted.setter
    def last_transmitted(self, value):
        """Set the last_transmitted config"""
        self.config[self.__last_transmitted] = value
        self.save()

    @property
    def battery_level(self):
        """Get the battery_level config"""
        return self.config[self.__battery_level]

    @battery_level.setter
    def battery_level(self, value):
        """Set the battery_level config"""
        self.config[self.__battery_level] = value
        self.save()

    @property
    def coverage_level(self):
        """Get the coverage_level config"""
        return self.config[self.__coverage_level]

    @coverage_level.setter
    def coverage_level(self, value):
        """Set the coverage_level config"""
        self.config[self.__coverage_level] = value
        self.save()

    @property
    def messages_sent(self):
        """Get the messages_sent config"""
        return self.config[self.__messages_sent]

    @messages_sent.setter
    def messages_sent(self, value):
        """Set the messages_sent config"""
        self.config[self.__messages_sent] = value
        self.save()

    @property
    def failed_transmissions(self):
        """Get the failed_transmissions config"""
        return self.config[self.__failed_transmissions]

    @failed_transmissions.setter
    def failed_transmissions(self, value):
        """Set the failed_transmissions config"""
        self.config[self.__failed_transmissions] = value
        self.save()

    @property
    def free_sd_space(self):
        """Get the free_sd_space config"""
        return self.config[self.__free_sd_space]

    @free_sd_space.setter
    def free_sd_space(self, value):
        """Set the free_sd_space config"""
        self.config[self.__free_sd_space] = value
        self.save()

    @property
    def rainfall(self):
        """Get the rainfall config"""
        return self.config[self.__rainfall]

    @rainfall.setter
    def rainfall(self, value):
        """Set the rainfall config"""
        self.config[self.__rainfall] = value
        self.save()

    @property
    def date_time(self):
        """Get the date_time config"""
        return self.config[self.__date_time]

    @date_time.setter
    def date_time(self, value):
        """Set the date_time config"""
        self.config[self.__date_time] = value
        self.save()


def read_config(file_name=CONFIG_FILE):
    """Returns an instance of the base config class"""

    with open(file_name, encoding="utf-8") as handle:
        contents = handle.read()
        data = json.loads(contents)
        return BaseConfig(file_name, data)


def read_data(file_name=DYNAMIC_DATA_FILE):
    """Returns an instance of the data config class"""

    with open(file_name, encoding="utf-8") as handle:
        contents = handle.read()
        data = json.loads(contents)
        return DataConfig(file_name, data)


def save_config(file_name, config):
    """Saves the config dictionary as json to the given file"""

    with open(file_name, "w") as handle:
        contents = json.dumps(config, indent=4)
        handle.write(contents)
