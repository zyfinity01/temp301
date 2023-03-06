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

import time
import logging

log = logging.getLogger("scheduler")
# Enable the following to set a log level specific to this module:
# log.setLevel(logging.DEBUG)


def get_time_to_next_recording(current_time: float, sensor: dict) -> float:
    """
    Get the next time to take a sensor recording

    Args:
        current_time (float): current time to measure from
        sensor (SDI12Sensor): sensor to read

    Returns:
        Time in seconds until the next recording
    """

    # Get difference between current time and first recording. This will be
    # positive if the first recording is in the future.
    #
    # NOTE: `first_record_at` should be treated as "integer seconds since
    # midnight" per the HyQuest SDI-12 sensor configuration setting "First
    # Measure At"  which displays `HH:MM:ss`; see #577.
    time_diff = sensor["first_record_at"] - current_time

    # When time_diff is positive, the first recording hasn't happened yet, so
    # time_diff could be greater than sensor.record_interval.
    # If this is the case, just return the number of seconds until the first
    # recording, rather than using modulo as that could make things messy
    if time_diff > 0:
        return time_diff

    # Return the time until the next reading. Need to multiply by 60 to convert
    # to seconds. The brackets around `60 * sensor[...]` are very important
    # because `*` does not take precedence over `%`
    return time_diff % (60 * sensor["record_interval"])


def should_transmit(current_time: int, last_send_at: int, send_interval: int):
    """
    Return whether or not the device should transmit this wakeup.

    Args:
        send_interval (int): seconds between sending data

    Returns:
        True if the device should transmit
    """
    log.debug("Last send time: {:d}".format(last_send_at))
    log.debug("Current time:   {:d}".format(current_time))

    time_diff = current_time - last_send_at

    if time_diff < 0:
        # A negative time_diff indicates the last transmission was in the
        # future. This could happen in one of two circumstances:
        #
        #   1. last_transmitted (last_send_at) was updated when the ESP32 RTC
        #      had been set to NZDT by rshell and the RTC has subsequently been
        #      set to NZST (NZDT -3600), or
        #   2. the ESP32 RTC has lost power and reset to the epoch and neither
        #      network time nor external RTC module are available.
        #
        # Fix by either (1) removing either 3600 s from last_send_at or (2)
        # disregarding last_sent_at altogether.
        log.error("Difference between current_time and last_send_at is negative")
        if time_diff > -3600:
            log.error("last_send_at appears to be NZDT, correcting by 3600 s")
            time_diff = current_time - (last_send_at - 3600)
        elif time_diff < -730000000:
            log.error("Resetting last_send_at to force a transmission")
            time_diff = send_interval  # Force transmission now

    if last_send_at == 0:
        log.debug("No prior transmission timestamp recorded (last_send_at = 0)")
    log.debug("Elapsed time:   {:9d}".format(time_diff))
    log.debug("Send interval:  {:9d}".format(send_interval))

    # If within 60-seconds of the send interval, proceed with the transmission
    if ((send_interval) - time_diff) <= 60:
        should_transmit = True
    else:
        should_transmit = False

    log.debug("Should{}transmit this time".format(" " if should_transmit else " not "))

    return should_transmit


def calculate_sleep_time(current_time: int, sensors: dict) -> int:
    """
    Calculate time to go into deep sleep for, taking into account the next
    recording time, sensor boot time and next scheduled recording

    Args:
        current_time (int): unix timestamp
        sensors (dict): dict of sensor_name -> sensor_data

    Returns:
        time (seconds) to sleep for
    """

    next_record = min(
        [
            get_time_to_next_recording(current_time, sensor)
            for name, sensor in sensors.items()
        ]
    )
    max_boot = max([sensor["bootup_time"] for name, sensor in sensors.items()])

    return next_record - max_boot
