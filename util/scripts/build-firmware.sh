#!/bin/sh
#
# Script to upload the micropython firmware to the ESP32

# parse command line args
FIRMWARE=${1-"$HOME/artefacts/esp32spiram-idf4-20210202-v1.14.bin"}
DEVICE=${2:-"/dev/ttyUSB0"}

# Erase flash
echo "########################"
echo "Erasing flash of ${DEVICE}"
esptool.py --port "${DEVICE}" erase_flash

# Upload firmware
echo "########################"
echo "Uploading firmware to ${DEVICE}"
esptool.py --chip esp32 --port "${DEVICE}" write_flash -z  0x1000 "${FIRMWARE}"
