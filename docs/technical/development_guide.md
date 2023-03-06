# Development Guide

Once you have the [hardware set up](hardware_setup.md), you have initialised your [dev environment](dev_environment_setup.md), and have uploaded [micropython to the board](micropython_build.md), these instructions show how to get started with development of the embedded software.

## Uploading Device Code

The [build script](/software/device/build.sh) compiles the embedded micropython code into `.mpy` files (frozen bytecode), and compiles the webapp code into minified/gzipped static files.

Running the build script with `./build.sh` generates a `build/` folder, which can be uploaded directly to the device.

This project predominantly uses `rshell` to interact with the device. `rshell` has an `rsync` function that syncronises a local folder with the device folder.

To sync the build folder and device, try:

```repl
rshell --port /dev/ttyXXX --baud 115200 rsync build/ /pyboard
```

***Development note:** If you are only changing a couple of files we recommend copying only the changed files using `cp` (rather than using `rsync`, which will take longer). For example if you made changes in `main.py` and `drivers/modem.py` you can:

```bash
rshell --port /dev/ttyS* -b 115200 cp src/main.py /pyboard
rshell --port /dev/ttyS* -b 115200 cp src/drivers/modem.py /pyboard/drivers
```

## Provisioning The Device

### Initial Device config

The device requires some configuration files, stored on the SD card, to run:

First, copy the example config:

```bash
cd software/device/embedded/src/services/
cp device-config.example.json device-config.json
```

Then, open the file and make some changes.

- `device_name`: Set a unique serial number in the device name - this will be used in setting the MQTT topic.
- `device_id`: Set to match the serial number in device_name
- `send_interval` interval: how often you want the device to send MQTT message.
- `symmetric_key`: MQTT client ID

After saving the config file, upload it to the device's SD card.

```bash
rshell --port /dev/ttyXXX --baud 115200 rsync provision /pyboard/sd/services
```

We have an incomplete [provision step](/software/device/embedded/src/provision.py) to generate this device config based on an interactive prompt.

### u-blox SARA-R4 Modem Registration

The modem needs to register with a network operator to obtain cellular network access. The data recorder registers with Vodafone by default. The manual steps for registration follow.

Open the REPL through rshell.

```shell
rshell --port /dev/ttyXXX -b 115200 repl
```

With the REPL open, run the following:

```python
import provision
provision.provision()
```

Type `modem` and hit enter.

The device will attempt to automatically register with the network operator for you. If successful, you should see a blue LED flashing on the SparkFun Shield which indicates the SARA-R4 modem has successfully registered with the network operator. Press enter to exit.

If you fail to provision the modem after serval attempts you should check the following:

1. Power: Is the SparkFun Shield's red LED lit?
1. SIM card: Do you have a SIM card with plan inserted to the modem?
1. Serial Communication: Is the SERIAL switched to HARD on the modem?

If you have checked those settings and they are all correct, try using the modem driver in Arduino firmware as an alternative way to register to network.

Follow [this](../research/hardware/ublox_modem/Arduino_ESP32/ESP32_Register/README.md) document. ***Note*** You will lose the MicroPython firmware and software, and you will need to repeat the [build process](micropython_build.md) again.

## Running Device Tests

The unit tests are stored [here](software/device/embedded/src/test/test_all.py). Run all the tests with:

```python
import unittest
unittest.main("test/test_all")
```

## Using the device interactively

As outlined in the [software architecture](./architecture/embedded_sw_architecture), we have two main modes - `regular mode` and `configure mode`. The REPL gives instructions on how to run these modes after you initate a soft boot.
