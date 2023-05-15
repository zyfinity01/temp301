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

Driver for the microSD card reader

Defines functions for mounting and read-write access to the filesystem on
a microSD card, as well as functions called from test/test_sd.py.
"""
import os
import logging
from machine import SDCard
from micropython import const
from util import helpers
from util.time import isoformat

import json

log = logging.getLogger("sdcard")  # __name__ = "drivers.sdcard"
# Enable the following to set a log level specific to this module:
# Don't honour global DEBUG - limited general value in DEBUG messages
log.setLevel(logging.INFO)

# _SD is assigned to an instance of `machine.SDCard` if setup()
# succeeds. Only one instance of `machine.SDCard` can be created
# because the SPI ports are marked "in use" on first instantiation.
# _SD_ENABLED is a simple boolean indicating whether _SD has been
# successfully instantiated, i.e. whether a microSD card is present
# and mounted.
_SD = None
_SD_ENABLED = False

# Define Rev::4.0 connections from ESP32 GPIO to the microSD card
# reader, shown on the ESP32_board schematic, as constants
#
SD_CLK = const(13)  # IO13 (physical pin 16)
SD_DO = const(34)  # IO34 (physical pin 6)
SD_DI = const(23)  # IO23 (physical pin 37)
SD_CS = const(12)  # IO12 (physical pin 14)

SD_DIR = "/sd"
MAIN_FILE = "datalog"
BACKUP_DIR = "daily/"
SYSLOG = "system.log"
FILETYPE = ".csv"

REQUEUE_FILE = "failed_transmissions"

HEADER_STR = "Sensor,Datetime,Data"


def setup(sd_logging=True):
    """Set up the SD card and filesystem.

    Args:
        sd_logging (bool, optional): Set to False if logging should be done on stderr instead of
        into a log file. If no SD card is present, logging will automatically be done to stderr.
        Defaults to True.

    Globals:
        _SD is assigned here to an instance of `machine.SDCard` and is used in this function
        to mount the microSD filesystem at the path SD_DIR.
        _SD_ENABLED is set True here if instantiation and mounting of the filesystem succeeds,
        is set False otherwise, and is referenced/tested elsewhere in the module.
    """
    global _SD_ENABLED, _SD
    if not _SD_ENABLED:
        _SD = SDCard(slot=2, sck=SD_CLK, miso=SD_DO, mosi=SD_DI, cs=SD_CS)
        try:
            os.mount(_SD, SD_DIR)
            _SD_ENABLED = True
        except OSError:
            # If no SD card is present, disable it until next boot (or until setup is called again)
            _SD_ENABLED = False
            _SD.deinit()
            # OSError message is meaningless, so don't log it
            log.error("Failed to mount microSD card")

    if _SD_ENABLED and sd_logging:
        # Save logs to SD card in addition to stderr
        open_log()

    if _SD_ENABLED:
        # Always use statvfs()
        # <https://docs.micropython.org/en/latest/library/os.html#os.statvfs>
        # to query the microSD card parameters. statvfs() returns a
        # tuple with filesystem information in the following order:
        #     f_bsize, f_frsize, f_blocks, f_bfree, ...
        # f_blocks and f_bfree are given in f_frsize units.
        #
        # ioctl() and statvfs() give different values for the block
        # size and number of blocks, but statvfs() shows the closest
        # agreement with the df command in the terminal and agrees with
        # the output of `mpremote df`. It also returns more
        # information about the file system than ioctl().
        # Use statvfs() everywhere.
        sdstat = os.statvfs(SD_DIR)
        log.debug(
            "Mounted microSD card, size={:0.2f} GB".format(
                (sdstat[2] * sdstat[1]) / 1000**3
            )
        )
        # Ensure the expected directory structure exists
        backup_directory = helpers.join_path(SD_DIR, BACKUP_DIR)
        services_directory = helpers.join_path(SD_DIR, "services")
        helpers.deep_mkdir(backup_directory)
        helpers.deep_mkdir(services_directory)

        # Ensure existence of cache file
        with open(REQUEUE_FILE + FILETYPE, "a+") as _:
            pass


def teardown():
    """Cleanly disable the SD card. This is only used for testing."""
    global _SD_ENABLED
    close_log()
    if _SD_ENABLED:
        os.umount(SD_DIR)
        _SD.deinit()
    _SD_ENABLED = False


def gen_path(*path: str) -> str:
    """Generate a path on the SD card if it is present.

    Returns:
        str: The file path.
    """
    if not path:
        return ""
    # If the path already starts with /sd, don't add it again
    return helpers.join_path(
        get_logging_dir() if not path[0].startswith(get_logging_dir()) else "", *path
    )


def get_logging_dir() -> str:
    """Get the name of the directory for logging/telemetry.

    If the SD card is not connected, this will default to the root directory (/).

    Returns:
        str: The path of the logging directory.
    """
    return SD_DIR if _SD_ENABLED else "/"


def get_main_telemetry_file() -> str:
    """Helper function to get the path to the main telemetry file.

    Returns:
        str: The path to the telemetry file.
    """
    return helpers.join_path(get_logging_dir(), MAIN_FILE + FILETYPE)


def get_log_file() -> str:
    """Helper function to get the path to the logging file.

    Returns:
        str: The path to the logging file.
    """
    return helpers.join_path(get_logging_dir(), SYSLOG)


def get_free_space() -> int:
    """Get the available space on the SD card.

    Returns:
        int: The capacity of the SD card in bytes, or -1 if no SD card set up.
    """
    if _SD_ENABLED:
        # Always use statvfs() to query the microSD card parameters.
        # See the comment in setup() for a full explanation.
        sdstat = os.statvfs(SD_DIR)
        log.info(
            "Remaining microSD capacity: {0} of {1} GB".format(
                ((sdstat[1] * sdstat[3]) / 1000**3),
                ((sdstat[1] * sdstat[2]) / 1000**3),
            )
        )
        return sdstat[1] * sdstat[3]

    log.warning("No microSD card present")
    return -1


def write_failed_transmission(data: str):
    """Writes out the json data to the failed transmission file.

    Args:
        data (str): Data to be stored. Must be in the format used to
            send data to the webserver, as it is parsed and re-sent with the
            same format.

        Each failed transmission is stored within an ordered csv file.

    Returns:
        bool: True if successfully written.
    """

    # If the is card is not enabled
    if not _SD_ENABLED:
        log.warning(
            "Can not save data to microSD card because it has not been successfully set up."
            + "This failed transmission will be lost!"
        )
        return False

    # Construct path for writing to failed dir
    out_file = REQUEUE_FILE + FILETYPE
    log.info("Writing failed transmission to {}".format(out_file))

    # Write out json data
    with open(out_file, "a") as f_ptr:
        f_ptr.write(data + "\n")
    return True


def read_failed_transmission() -> str or None:
    """
    Loads a random file to be queued for transmission.

    Transmissions are obtained in the reverse order they were written, as sorting via O(NlogN) gets complex,
    especially given the processing capacity of the ESP32.

    # TODO: https://gitlab.ecs.vuw.ac.nz/course-work/engr301/2023/group3/data-recorder/-/issues/80
         \\ This issue will need to be evaluated to ensure that ordering is inconsequential.
         \\ If ordering is required, this is going to have to be rewritten.

    Returns:
        str: Json data from failed transmission, or None if there are no remaining failed or the
        SD card is not mounted
    """

    # If SD card is not mounted, no files available
    if not _SD_ENABLED:
        return None

    # Grabs latest cached transmission
    in_file = REQUEUE_FILE + FILETYPE

    # Grabs the last line of the file
    with open(in_file, "r") as f_ptr:
        f_ptr.seek(0, 2) #os.SEEK_END

        # If the file has no lines, there is no last line to grab
        if not f_ptr.tell():
            return None

        # Seek to the start of the last line of the file
        index = seek_endl(f_ptr)

        # Return the last line
        return f_ptr.read(
            index
        ).strip()  # FIXME: .strip() is slow, could we guarantee safety with [:-1]?


def delete_latest_failed_transmission() -> bool:
    """
    Attempts to truncate the failed transmission file by the latest transmission.

    This is used to remove transmissions from the cache which have since been successfully transmitted.

    Returns:
        bool: Whether an entry was removed. False if there are no entries present
    """

    # load in the list of entries
    in_file = REQUEUE_FILE + FILETYPE

    # Deletes the last line of the file
    with open("debug.csv", "r+") as f_ptr:
        f_ptr.seek(0, 2) #os.SEEK_END

        # If file is empty, nothing to delete
        if not f_ptr.tell():
            return False

        # Seek to the start of the last line of the file
        index = seek_endl(f_ptr)

        # Don't include the terminating newline if there are remaining lines in the file
        index = index + (index > 0)
        f_ptr.seek(index, 0) #os.SEEK_SET

        # Truncate the last line
        f_ptr.truncate(index)

    return True


def save_telemetry(data: dict):
    """Stores data in the form:

    `reading name,date/time(yyyy-mm-ddThh:mm:ss),data`

    Args:
        data (dict): Must contain the name of the readings as keys with their corresponding values
            as values. The date time in epoch time must be provided as a value for the Time key.
            This should be in the form {"Reading_name_1": val_1, "Reading_name_2": val_2, ...,
            "Reading_name_n": val_n, "Time": epoch_time}

        All the readings will be added to separate lines in the CSV file. The Time key is
        required and logging will not function without it. No further values are required as the
        data on the microSD card does not need to have a lot of information.

    Returns:
        bool: True if successfully logged.
    """
    if not _SD_ENABLED:
        raise RuntimeError(
            "Can not save data to microSD card because it has not been successfully set up"
        )
    data_copy = dict(data)

    try:
        # Remove the time from the dict and deal with it separately
        integer_time = int(data_copy.pop("DateTime"))
    except KeyError:
        log.error("Data being logged is missing timestamp. Raw data is {}".format(data))
        return False
    except ValueError:
        log.error(
            "Data being logged has invalid timestamp. Raw data is {}".format(data)
        )
        return False

    # Get the datetime (timestamp) and the date (date_str)
    timestamp = isoformat(integer_time)

    # Put data into a list for appending to a CSV
    data_list = [
        _gen_data_string(name, value, timestamp) for name, value in data_copy.items()
    ]

    # Create a main file and a backup file
    files = [
        gen_path(MAIN_FILE + FILETYPE),
        gen_path(BACKUP_DIR, MAIN_FILE + "_" + timestamp[:10] + FILETYPE),
    ]

    for fname in files:
        # If file doesn't exist, add header to new file
        if not helpers.check_exists(fname):
            log.info("Generating new log file: {}".format(fname))
            _append_to_csv(fname, [HEADER_STR])
        # Append data to file
        _append_to_csv(fname, data_list)

    return True


def _gen_data_string(name: str, data: float, time: str) -> str:
    """Convert the provided values to a CSV formatted string.

    The time should be a string generated with _gen_time_string.

    Args:
        name (str): The name of the sensor reading.
        data (float): The value returned for that sensor reading.
        time (str): The time the reading was taken.

    Returns:
        str: A CSV formatted string.
    """
    return "{name},{time},{data}".format(name=name, time=time, data=data)


def open_log():
    """Enable logging to the SD card. This will only succeed if the SD card is inserted."""
    if _SD_ENABLED:
        logging._stream.set_file(get_log_file())


def close_log():
    """Reset logging to stderr."""
    log.info("Closing system log file")
    logging._stream.unset_file()


def _append_to_csv(filename: str, data: list):
    """Append data to a file and add a newline to the end.

    Args:
        filename (str): The file to save to.
        data (str): The data to be added to the file.
    """
    # Enable the following debug statement only when troubleshooting
    # problems writing data to the CSV files:
    # log.debug("Writing <<{}>> to {}".format(data, filename))
    with open(filename, "a+") as csvfile:
        for datum in data:
            csvfile.write(datum + "\n")


def open_file(filename, mode="r", no_sd=False) -> FileIO:
    """Open a file on the SD card.

    Args:
        filename (str): The name of the file
        mode (str, optional): Mode that the file is opened in (see open()). Defaults to 'r'.
        no_sd (bool, optional): Allow writing to flash if the SD card is not present.

    Returns:
        FileIO: The file pointer, or None if no_sd is False and the SD card is not present.
    """
    if _SD_ENABLED or no_sd:
        return open(gen_path(filename), mode)
    else:
        raise RuntimeError("No microSD card present.")


def seek_endl(f_ptr):
    """Seeks to the start of the last line in the file.

    Args:
        f_ptr: The file pointer of the file to be traversed.

    Returns:
        int: Index of the file pointer after seeking.
    """
    # Skips the last newline
    index = f_ptr.tell() - 1

    # While we are not pointing at a newline, seek backwards
    while f_ptr.read(1) != "\n" and index > 0:
        index -= 1
        f_ptr.seek(index, 0) #os.SEEK_SET

    return index


def enabled() -> bool:
    """Gets the status of the SD card, to inform user that it has been set up successfully.

    Returns:
        bool: Returns True if microSD card is present.
    """
    log.info("microSD card is {}enabled".format("" if _SD_ENABLED else "not "))
    return _SD_ENABLED
