# MicroPython Build Docs

These instructions are intended to assist deploying custom MicroPython firmware to an ESP32, based on the MicroPython Wiki [1,2]. There are additional instructions available for building MicroPython for ESP32 in Docker [3,4] and several examples on the MicroPython Forum [5].

The advantage of building custom firmware is that it can be configured for a specific purpose, the benefit for the data recorder is that library modules can be added directly to the firmware rather than copied separately to the flash memory in a `lib` directory.

## References

1. Getting Started <https://github.com/micropython/micropython/wiki/Getting-Started>
1. Building Micropython Binaries <https://github.com/micropython/micropython/wiki/Building-Micropython-Binaries>
1. MicroPython Build Environment for ESP32 in a Docker Container <https://forum.micropython.org/viewtopic.php?t=7307>
1. micropython/build-micropython-esp32 <https://hub.docker.com/r/micropython/build-micropython-esp32>
1. Building micropython with 240mhz <https://forum.micropython.org/viewtopic.php?t=12586>

## Download MicroPython

```shell
git clone https://github.com/micropython/micropython.git
cd micropython
```

## Build mpy-cross

```shell
cd mpy-cross
make
```

## Set up ESP toolchain

```shell
cd ports/esp32
make ESPIDF= # make a note of the latest non-experimental hash
export ESPIDF=$HOME/esp/esp-idf # use any path provided it doesn't contain spaces
mkdir -p $ESPIDF
cd $ESPIDF
git clone https://github.com/espressif/esp-idf.git $ESPIDF
git checkout <Current supported ESP-IDF commit hash>
git submodule update --init --recursive
export IDF_PATH=$ESPIDF
```

You may want to add  ESPIDF to your .bashrc file so it is set up everytime you start your terminal.

```shell
echo "export ESPIDF=$HOME/esp/esp-idf" >> ~/.bashrc # optional
echo "export IDF_PATH=$ESPIDF" >> ~/.bashrc # optional
```

## Set up a Python virtual environment

```shell
cd ports/esp32 # in MicroPython repo
python3 -m venv build-venv
source build-venv/bin/activate
pip install --upgrade pip
pip install wheel # if it's not already installed
pip install -r $ESPIDF/requirements.txt
```

To start this environment later, you need to source the activate script again.

```shell
cd ports/esp32
source build-venv/bin/activate
```

## Continue setting up toolchain

Install dependencies:

```shell
sudo apt-get install gcc git wget make libncurses-dev flex bison gperf python python-pip python-setuptools python-serial python-cryptography python-future python-pyparsing libffi-dev libssl-dev libncurses5-dev libncursesw5-dev
```

Download the file available [here](https://docs.espressif.com/projects/esp-idf/en/v3.3.2/get-started/linux-setup.html#toolchain-setup). If you copy the link, you can download in the terminal.

```shell
cd $ESPIDF
wget <download_link> # skip this if you already downloaded it
tar -xzf <downloaded_file>
rm <downloaded_file>
```

Create an alias to activate the toolchain.

```shell
echo "alias get_esp32='export PATH=\"$HOME/esp/xtensa-esp32-elf/bin:$PATH\"'" >> ~/.profile
source ~/.profile
```

Now when you call `get_esp32`, the toolchain will be added to your PATH.

## Test serial connection

Connect the ESP32 devkit to your computer and find the port it is connected to.
You can do this by disconnecting and reconnecting the devkit and seeing which port changes.

```shell
ls /dev/tty*
```

Make a note of the port being used.

If using WSL or MacOS, install [this driver](https://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers). In Windows, open Device Manager, and identify the COM port.
The port will be named `COMx` so use `/dev/ttySx` for all commands in WSL.

You may need to add the user to `dialout`.

```shell
sudo usermod -a -G dialout $USER
```

Test the connection by starting a serial connection with a baudrate of 115200, 8 data bits, 1 stop bit, no parity, and XON/XOFF flow control.
I recommend using PuTTY (GUI) or picocom (CLI). You can install picocom on Linux with `sudo apt install picocom`.

The picocom command is `picocom --b 115200 /dev/ttyX` where `X` is replaced with the port number.

Reboot the board and you should see the ESP32 log printed out.
If there is no log, ensure you have pressed the correct button to reboot the board and that the port is correct.
If the log isn't legible, you may have set one of the serial parameters incorrectly.

Finish by closing the serial connection.

## Test an example build (not MicroPython)

```shell
cd $ESPIDF
cp -r $IDF_PATH/examples/get-started/hello_world .
cd $ESPIDF/hello_world
make menuconfig
```

If `make menuconfig` is successful, you should see a menu.
Change the Default serial port in Serial flasher config to the port the board is connected to.
Press Save and Exit.

With the device connected, build and flash the application.

```shell
make flash
```

This may take a while, but once it finishes you should be able to view the device printing "Hello world!" on the serial port and restarting.
To rebuild the application, you can just run `make app` or `make app-flash` to flash it too.

## Configuring MicroPython build

```shell
cd ports/esp32
touch makefile
```

Name the file `GNUmakefile` if you're on a case-sensitive filesystem.

In `makefile`, add the following lines:

```makefile
ESPIDF ?= $ESPIDF
BOARD ?= GENERIC_SPIRAM
#PORT ?= /dev/ttyUSB0
#FLASH_MODE ?= qio
#FLASH_SIZE ?= 4MB
#CROSS_COMPILE ?= xtensa-esp32-elf-

include Makefile
```

Make sure the submodules are up to date.

```shell
git submodule update --init
make clean
make
```

You should now be able to upload the firmware to the board.

```shell
make erase
make deploy
```

If that is unsuccessful and you have ensured the port is specified correctly in the makefile (this may be an issue in WSL), you can run the `esptool.py` script provided in the `ports/esp32` directory.

```shell
esptool.py --chip esp32 --port /dev/ttyX erase_flash
esptool.py --chip esp32 --port /dev/ttyX write_flash -z 0x1000 build-GENERIC_SPIRAM/firmware.bin
```

Make sure to replace `ttyX` with the correct port number.

You should now be able to access the REPL on the device over serial.

```shell
picocom -b 115200 /dev/ttyX
```

## Adding libraries to the firmware Image

Simply copy the .py files to the `modules/` subdirectory.
This will make the build step freeze the python files into frozen bytecode, and then bake it into the image.
Easy!

---
