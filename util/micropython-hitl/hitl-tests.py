#!/usr/bin/env python
# todo: fix this being broken in pycharm
from pyboard import execfile
import argparse
import subprocess
import os

# NOTE: This script functionality is currently implemented by hitl-tests.sh
# This file is kept here in case we need to improve the HITL test runner with
# advanced capabilities that require python, but for now a bash script suffices.

# This script does the following tasks:
# Uploads latest micropython code to the device
# Runs HITL tests directly on the device
# Returns an exit code based on the test results.
# Based on https://docs.micropython.org/en/latest/reference/pyboard.py.html


class HITL(object):
    def __init__(self, device, baud, code_path):
        self.device = device
        self.baud = baud
        self.code_path = os.path.abspath(code_path)

    def start(self):
        print("Beginning HITL tests on {0}".format(self.device))
        self.copy_files()

    def copy_files(self):
        """
        Copy device code to hitl device with rshell (external program)
        """
        print("############")
        print("Copying device code from {0}".format(self.code_path))
        os.system(
            "rshell --port {0} rsync {1} /pyboard".format(self.device, self.code_path)
        )

    def run_tests(self):
        """
        Run the HITL tests on the device.
        """
        print("############")
        print("Running HITL Tests")
        filename = "not implemented"
        # execfile(filename, self.device, self.baud)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--baud", default=115200, type=int, help="baud rate")
    parser.add_argument("-d", "--device", default="/dev/ttyUSB0", help="serial device")
    parser.add_argument(
        "-p", "--path", default="device/", help="root code directory to upload"
    )

    options = parser.parse_args()

    hitl = HITL(device=options.device, baud=options.baud, code_path=options.path)
    hitl.start()
