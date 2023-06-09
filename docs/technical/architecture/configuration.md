# Device Configuration Schema

This document standardises the device configuration JSON file and API schema, discussed in #161 and in other places.
It should be the source of truth and used as reference.

## Device Configuration

- device_name: str
- device_id: str
- hardware_revision: str
- send_interval: int (mins) - multiple of record_interval
- first_send_at: int (unix time)
- wifi_ssid: str
- wifi_password: str (hashed)
- maintenance_mode: bool
- mqtt_settings: dict
  - host: str
  - port: int
  - username: str
  - password: str
  - parent_topic: str
- mmw_settings: dict
  - auth_token: str
  - sampling_feature: str
- sdi12_sensors: list
  - sensor_name: str
  - enabled: bool
  - address: char/byte/string
  - bootup_time: int (seconds)
  - record_interval: int (mins)
  - first_record_at: int (unix time)
  - readings: list
    - reading: string
    - index: int
    - unit: string
    - multiplier: int (mm)
    - offset: int (mm)
- rainfall_sensor: dict
  - enabled: boolean
  - record_interval: int (mins)
- adc_calibration: dict

## Device Data

dynamic data file (json): stores dynamic data generated by the controller.

- last_updated: int (unix time)
- last_transmitted: int (unix time)
- battery_level: int (voltage)
- coverage_level: int (dBm)
- messages_sent: int
- failed_transmissions: int

## Notes

- [Signal Strength measures](https://wiki.teltonika-networks.com/view/RSRP_and_RSRQ)
