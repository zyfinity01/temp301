# Device Code

This subfolder contains the micropython code that is uploaded onto the devices.

## Setup

Add config file:

```shell
cp configure_example.py configure.py
```

Set up WLAN config as directed in configure.py

```shell
vim configure.py
```

export PORT variable:

```shell
export PORT=/dev/ttyUSB0
```

upload the src directory (no build):

```shell
make uploadsrc
```

build `.mpy` files and upload to device:

```shell
make upload
```

enter the repl using picocom:

```shell
make repl
```

## Tools

The following tools are suggested:

- `rshell` - sync directories over flash, open the REPL, other useful stuff
- `esptool.py` - communicate with the ESP32 ROM bootloader

## Building MPY Files

A build script, `./build-device.sh`, creates a `build/` subdirectory with the library files saved as bytecode.

[Essential Reading](http://hinch.me.uk/html/reference/constrained.html)

Converting all the python files in the `lib/` directory to `.mpy` files:

```shell
find device/lib -iname '*.py' -exec python -m mpy_cross {} \;
```
