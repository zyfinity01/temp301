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

import logging
import re

MQTT_TOPIC_REGEX = "^(?!\/)\w+.*\/$"  # don't start with a "/", and always end in a "/"
ADDRESS_REGEX = "^[A-Za-z0-9]$"
UNITS = ["c", "m/s"]


def validate_settings(values: dict, validator_map):
    """
    Validate incoming settings.

    Used primarily by the webserver. Recursively iterates through the items in the dictionary and checks
    sane values for each argument

    Args:
        values (dict): device settings (see configuration schema in docs)
        validator_map (dict): custom map of validators to use (see DEVICE_SETTINGS_VALIDATIONS for example)
    Raises:
        ValueError if any of the inputs are invalid
        ValueError if an unrecognised argument exists
    """

    for k, v in values.items():
        if k not in validator_map:
            raise ValueError("Unexpected Argument {0}".format(k))

        validators = validator_map[k]

        # recursively check nested dict
        if isinstance(validators, dict):
            validate_settings(values[k], validators)
        else:
            # run the validator
            # the validator function is the first index of the iterable, and the rest are the function arguments
            for validator in validators:
                validator[0](v, *validator[1:])


def validate_device_settings(data: dict):
    validate_settings(data, DEVICE_SETTINGS_VALIDATIONS)


def validate_sensor_settings(data: dict):
    validate_settings(data, SENSOR_SETTINGS_VALIDATIONS)


def validate_list(input_list: list, validators: dict):
    """
    Validate a json list of non-nested objects

    This could be improved in the future by supporting nested objects, ie
    [{'key':{'one':1, 'two':2}}, ...]

    Args:
        input_list: list of objects
        validators: validator for each object in list

    Raises:
        ValueError if any list element is invalid
    """

    for item in input_list:

        if not isinstance(item, dict):
            raise ValueError("Expected list of objects")

        for k, v in item.items():
            item_validators = validators[k]

            for validator in item_validators:
                validator[0](v, *validator[1:])


def validate_length(input_str: str, minimum=0, maximum=100):
    """
    Validate the length of an input string.

    Args:
        input_str: input string
        minimum: minimum number of characters (inclusive)
        maximum: maximum number of characters (exclusive)

    Returns:
        True if validated successfully

    Raises:
        ValueError if the input is out of bounds

    """

    assert minimum < maximum, "minimum is greater or equal to maximum"
    assert minimum >= 0, "minimum length is too small"

    if minimum <= len(input_str) < maximum:
        return True

    raise ValueError(
        "String {0} out of length bounds (should be between {1} and {2})".format(
            input_str, minimum, maximum
        )
    )


def validate_base64(input_str: str):
    """
    Validate a base64 encoded string (empty string is valid)

    Args:
        input_str: base64 string

    Returns:
        True if valid

    Raises:
        ValueError if invalid

    """
    if input_str == "":
        return True

    if not re.match("^[A-Za-z0-9+/]*=*$", input_str):
        raise ValueError("Invalid Base64 string")

    return True


def validate_regex(input_str: str, regex: str):
    """
    Validate against a regular expression (using standard ruleset)
    see https://docs.micropython.org/en/latest/library/ure.html

    Args:
        input_str: input string
        regex: regular expression

    Returns:
        True if valid

    Raises:
        ValueError if invalid (no match)

    """
    if not re.match(regex, input_str):
        raise ValueError("Input did not match regex: {0}".format(regex))

    return True


def validate_num(input_num, minimum=0, maximum=None):
    """
    Validate a number is between bounds
    Args:
        input_num (number): input number
        minimum (number): minimum value (inclusive)
        maximum (number): maximum number (exclusive, can be None to not validate maximum)

    Returns:
        True if valid

    Raises:
        ValueError if out of bounds
    """

    if maximum is None:
        if minimum <= input_num:
            return True

        raise ValueError(
            "Number {0} too small (should be larger than {1})".format(
                input_num, minimum
            )
        )

    else:
        if minimum <= input_num < maximum:
            return True

        raise ValueError(
            "Number {0} out of bounds (should be between {1} and {2})".format(
                input_num, minimum, maximum
            )
        )


def validate_enum(input_str: str, possible_values: list):
    """
    Validate input string is one of the possible values

    Args:
        input_str: input string
        possible_values: list of string values to match against

    Returns:
        True if valid

    Raises:
        ValueError if input_string isn't in possible_values
    """
    if input_str in possible_values:
        return True

    raise ValueError(
        "{0} is an invalid input (expected one of: {1}".format(
            input_str, "|".join(possible_values)
        )
    )


def validate_type(input_var, *types):
    """
    Validate the input variable is (one of) a particular type using instanceof()

    Args:
        input_var: input variable of any type
        *types: types to check (eg: int, dict, str)
    Returns:
        True if valid

    Raises:
        ValueError if invalid type
    """

    for type_ in types:
        if isinstance(input_var, type_):
            return True

    raise ValueError(
        "{0} is of wrong type (expected {1})".format(
            input_var, "|".join([str(_type) for _type in types])
        )
    )


# Dict mapping the input to a list of validators, with their arguments.
DEVICE_SETTINGS_VALIDATIONS = {
    "device_name": [(validate_type, str), (validate_length, 1, 30)],
    "device_id": [(validate_type, str), (validate_length, 1, 20)],
    "wifi_ssid": [(validate_type, str), (validate_length, 1, 32)],
    "wifi_password": [(validate_type, str), (validate_length, 5, 30)],
    "first_send_at": [(validate_type, int), (validate_num, 0)],
    "send_interval": [(validate_type, int), (validate_num, 1)],
    "maintenance_mode": [(validate_type, bool)],
    "mqtt_settings": {
        "host": [(validate_type, str), (validate_length, 1, 50)],
        "port": [(validate_type, int), (validate_num, 1)],
        "username": [(validate_type, str), (validate_length, 1, 50)],
        "password": [(validate_type, str), (validate_length, 1, 50)],
        "parent_topic": [(validate_type, str), (validate_regex, MQTT_TOPIC_REGEX)],
    },
    "mmw_settings": {
        "auth_token": [(validate_type, str), (validate_length, 30, 50)],
        "sampling_feature": [(validate_type, str), (validate_length, 30, 50)],
    },
}

SENSOR_SETTINGS_VALIDATIONS = {
    "enabled": [(validate_type, bool)],
    "address": [(validate_type, str), (validate_regex, ADDRESS_REGEX)],
    "bootup_time": [(validate_type, int), (validate_num, 0)],
    "record_interval": [(validate_type, int), (validate_num, 0)],
    "first_record_at": [(validate_type, int), (validate_num, 0)],
    "readings": [
        (validate_type, list),
        (
            validate_list,
            {
                "reading": [(validate_type, str), (validate_length, 1, 20)],
                "index": [(validate_type, int), (validate_num, 0)],
                "unit": [(validate_type, str)],
                "multiplier": [(validate_type, int, float)],
                "offset": [(validate_type, int, float)],
                "uuid": [(validate_type, str), (validate_length, 30, 40)],
            },
        ),
    ],
}
