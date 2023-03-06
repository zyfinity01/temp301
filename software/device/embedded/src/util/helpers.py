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

import os
import urequests
import logging

_sep = "/"

log = logging.getLogger("helpers")
# Enable the following to set a log level specific to this module:
# log.setLevel(logging.DEBUG)


def cat(path):
    """
    Print contents of a file to stdout
    Args:
        path: path to file
    """
    with open(path, "r") as f_in:
        print(f_in.read())


def ls(path="", sizes=False):
    """
    Print the contents of a directory.
    Args:
        path (str): path to print
        sizes (bool): if true, prints the directory filesize on each line

    Returns:

    """

    # construct and format each line with the filesize
    # TODO: this doesn't always work
    if sizes:
        output = [
            "{file}\t{size}".format(file=file, size=size)
            for file, size in list(
                map(
                    lambda file: (file, dir_size(file)),
                    filter(lambda dir: get_file_size(dir) == -1, os.listdir(path)),
                )
            )
        ]
    else:
        output = os.listdir(path)

    # print each line individually
    for file in output:
        print(file)


def dir_size(directory):
    """
    Return the total size of a folder in bytes
    """
    total_size = 0
    for contents in os.listdir(directory):
        full_path = directory + _sep + contents
        size = get_file_size(full_path)
        if size == -1:  # folder
            total_size += dir_size(full_path)
        else:  # file
            total_size += size
    return total_size


def deep_rmdir(directory):
    """
    Recursively remove every file/folder in a directory (including itself)
    """
    for contents in os.listdir(directory):
        full_path = directory + _sep + contents
        if get_file_size(full_path) == -1:  # folder
            deep_rmdir(full_path)
        else:  # file
            os.remove(full_path)
    os.rmdir(directory)


def get_file_size(path):
    """
    Returns the file size in bytes. Returns -1 if path is to a directory.
    """
    # 16384 represents a dir and 32768 represents a file for whatever reason
    if os.stat(path)[0] == 16384:
        return -1
    else:
        return os.stat(path)[6]


def chdir_mkdir(directory):
    """
    Move into a directory. Make it if it doesn't already exist.
    """
    if not check_exists(directory):
        log.info("Creating directory: {}".format(directory))
        os.mkdir(directory)
    os.chdir(directory)


def deep_mkdir(path: str):
    subpaths = path.split(_sep)
    for subpath in subpaths:
        chdir_mkdir(subpath)
    # Return to original directory
    if path.startswith("/"):
        os.chdir("/")
    else:
        for subpath in subpaths:
            # This will ignore any extraneous _sep characters
            if subpath:
                os.chdir("..")


def join_path(path1, *path2) -> str:
    # Remove all instances of _sep from start and end of strings (including duplicates)
    p1 = path1.strip(_sep)
    p2 = [p.strip(_sep) for p in path2]
    # If there was at least one instance of _sep at the start, add it back
    if path1.startswith(_sep):
        p1 = _sep + p1
    return p1 + _sep + _sep.join(p2)


def check_exists(file_path: str) -> bool:
    split_path = file_path.strip(".").split(_sep)
    # Catching an OSError can be risky, so we'll check every dir iteratively
    for i in range(len(split_path)):
        # Just skip it if it is an empty string/path
        if not split_path[i]:
            continue
        # If the next item doesn't exist, return False
        deepest_path = split_path[:i]
        if split_path[i] not in os.listdir(
            join_path(*deepest_path) if deepest_path else ""
        ):
            return False
    # Return True if the entire path exists
    return True
