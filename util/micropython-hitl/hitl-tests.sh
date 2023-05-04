#!/bin/bash -e

# This script does the following tasks:
# Uploads latest micropython code to the device
# Runs HITL tests directly on the device
# Returns an exit code based on the test results.
# Based on https://docs.micropython.org/en/latest/reference/pyboard.py.html

# usage: ./hitl-tests.sh code_root_dir [device] [baud rate]

# verify command line args
if [[ $# -eq 0 ]]; then
    echo "no arguments supplied (expected 1)"
    exit 1;
fi

# Check rshell can execute
command -v rshell >/dev/null 2>&1 || { echo >&2 "Script requires rshell but it's not installed.  Aborting."; exit 1; }

# Check runner has the pyserial library installed (for pyboard.py)
# pip list | grep pyserial > /dev/null 2>&1 || { echo >&2 "Script requires pip library \"pyserial\" to be installed. Aborting."; exit 1; }

# parse command line args
CODE_ROOT=$(readlink -f "$1")
PROV_ROOT=$(dirname "$0")/provision
DEVICE=${2:-"/dev/ttyUSB0"}
BAUD=${3:-115200}
PYBOARD_PATH=$(dirname "$0")

# make configure.py
echo "
WIFI_MODE = 'OFF'
AP_SSID = ''
AP_PASSWORD = ''
IP_ADDR = ''
SUBNET = ''
GATEWAY = ''
DNS_SERVER = ''
NETWORKS = []
" > "${CODE_ROOT}/configure.py"

# Upload code with rshell
echo "########################"
echo "Uploading contents of ${CODE_ROOT} to ${DEVICE}"
rshell --port "${DEVICE}" --buffer-size 1024 rsync "${CODE_ROOT}" /pyboard/
sleep 1

# Upload provisioning data
echo "########################"
echo "Uploading contents of ${PROV_ROOT} to ${DEVICE}"
rshell --port "${DEVICE}" --buffer-size 1024 rsync "${PROV_ROOT}" /pyboard/sd/services
# Run HITL tests with pyboard
echo "########################"
echo "Running unit Tests"
python3 "${PYBOARD_PATH}"/pyboard.py -b "${BAUD}" -d "${DEVICE}" "${CODE_ROOT}/test/test_all.py" 2>&1 | tee unit_test_output.txt

# Run HITL tests with pyboard
echo "########################"
echo "Running integration Tests"
python3 "${PYBOARD_PATH}"/pyboard.py -b "${BAUD}" -d "${DEVICE}" "${CODE_ROOT}/test/integration/test_regular.py" 2>&1 | tee integration_test_output.txt

# Grep test output for FAIL and set output code
grep -e "FAIL" -q test_output.txt && echo "Test Failures Found!" && exit 1 || echo "Tests passed!" && exit 0;
