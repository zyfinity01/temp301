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


This module is use to handle basic modem operation by AT command

"""
import time
import json
import ure
from machine import UART, Pin
from util.time import isoformat

import logging

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
import asyn

log = logging.getLogger("modem")
# Enable the following to set a log level specific to this module:
# log.setLevel(logging.DEBUG)


MODEM_STANDARD_RESPONSE_TIMEOUT = 1000  # Standard AT command time out (ms)
MODEM_SET_BAUD_TIMEOUT = 10000  # Setting baud rate time out (ms)
MODEM_POWER_ON_PULSE_PERIOD = 300  # Low time to trigger power-on (ms)
MODEM_POWER_OFF_PULSE_PERIOD = 1750  # Low time to trigger graceful power-off (ms)
MODEM_MQTT_CONNECT_TIMEOUT = 120000  # MQTT connection time out (ms)

# Time constants in seconds
MODEM_MQTT_PING_PERIOD = 60  # Keep-alive period

# Suported AT Commands
# General
MODEM_COMMAND_AT = "AT"  # AT "Test"
MODEM_COMMAND_ECHO = "E"  # Local Echo
MODEM_COMMAND_IMEI = "+CGSN"  # IMEI identification
MODEM_COMMAND_IMSI = "+CIMI"  # IMSI identification
MODEM_COMMAND_CCID = "+CCID"  # SIM CCID
MODEM_COMMAND_OFF = "+CPWROFF"  # Turn off the modem
# Control and status
MODEM_COMMAND_FUNC = "+CFUN"  # Functionality (reset, etc.)
MODEM_COMMAND_CLOCK = "+CCLK"  # Clock
MODEM_COMMAND_AUTO_TZ = "+CTZU"  # Automatic time zone update
# Network service
MODEM_COMMAND_MNO = "+UMNOPROF"  # MNO (mobile network operator) Profile
MODEM_SIGNAL_QUALITY = "+CSQ"  # Signal quality
MODEM_REGISTRATION_STATUS = "+CREG"
MODEM_MESSAGE_PDP_DEF = "+CGDCONT"  # Network connection parameters (context definition)
MODEM_OPERATOR_SELECTION = "+COPS"  # Network operator info
MODEM_COMMAND_BAUD = "+IPR"  # Baud rate
# HTTP
MODEM_COMMAND_HTTP_CONTROL = "+UHTTP"  # HTTP Control
MODEM_COMMAND_HTTP_COMMAND = "+UHTTPC"  # HTTP Command
MODEM_COMMAND_HTTP_ERROR = "+UHTTPER"  # HTTP Error
# File
MODEM_COMMAND_FILE_WRITE = "+UDWNFILE"  # Write file to filesystem. Called "Download File" in ublox documentation, which can be confusing
MODEM_COMMAND_FILE_DELETE = "+UDELFILE"  # Delete file
MODEM_COMMAND_FILE_LIST = "+ULSTFILE"  # List all files in filesystem
MODEM_COMMAND_FILE_READ = "+URDFILE"  # Read file

# Response
MODEM_RESPONSE_OK = "OK"
MODEM_RESPONSE_ERROR = "ERROR"

# GPIO config
MODEM_POWER_PIN = 4
MODEM_TX_PIN = 27
MODEM_RX_PIN = 26

# Baud rate config
NUM_SUPPORTED_BAUD = 6
MODEM_SUPPORTED_BAUD = [115200, 9600, 19200, 38400, 57600, 230400]
MODEM_DEFAULT_BAUD = 115200

# HTTP temporary file on modem for POSTing MonitorMyWatershed data
HTTP_POST_DATA_FILE = "post_data.tmp"

# 2023 Data Recorder Webhook
MATTERMOST_WEBHOOK = "https://mattermost.ecs.vuw.ac.nz/hooks/3g7p6bm3ojfijpigdoers15awr"

MATTERMOST_SERVER = "https://mattermost.ecs.vuw.ac.nz"

MATTERMOST_CHANNEL_PATH = "/engr301-2023/channels/group-3-data-recorder"


class ModemTimeout(Exception):
    """Raised when modem commands time out"""


class ModemFileError(Exception):
    """Raised when the modem raises a file error"""


class Modem:
    def __init__(
        self,
        baud=MODEM_DEFAULT_BAUD,
        tx_pin=MODEM_TX_PIN,
        rx_pin=MODEM_RX_PIN,
    ) -> None:
        self.serial = UART(1, baud, bits=8, parity=None, stop=1, tx=tx_pin, rx=rx_pin)
        self.has_serial = False
        self.has_network = False
        self.signal_power = 99
        self.lock = asyn.Lock()

    def initialise(self):
        """Initialize the modem
        This method assumed tha the modem has set to correct baud rate,
        If not, run autobaud() or do this in provision

        - Power-on modem if not already on
        - Register to network
        - Set network parameters
        """
        log.debug("Initialising modem")

        # Power-on modem
        # If it's desired to attempt power-on more than once, restore the following:
        # boot_attempts = 0
        # while not self.has_serial and boot_attempts < 3:
        #     boot_attempts += 1
        #     log.warning("Power-on attempt {0}".format(boot_attempts))
        #     self.has_serial = self.power_on()
        if not self.has_serial:
            self.has_serial = self.power_on()

        # Connect to network
        if self.has_serial:
            # Testing indicates that TCP/IP communication is _not_ dependent on
            # the acquisition of an IP address. Try deferring or even omitting
            # the wait-for-IP-address loop.
            # self.acquire_network()
            self.has_network = True  # !!! May cause problems !!!

            # Network settings
            if self.has_network:
                # Enable auto time zone
                # !!! Parameter stored in NVM - do not need to check this _every time_ !!!
                # !!! Move this to first-boot configuration check/enforcement !!!
                response = self.send_command_read("+CTZU?")
                response = response.split("  ")
                if MODEM_RESPONSE_OK in response:
                    # Expecting response to be ['AT+CTZU?', '+CTZU: <on_off>', 'OK']
                    auto_timezone_update = response[1].split()[1]
                    if auto_timezone_update is not "1":
                        self.send_command_check("+CTZU=1")

                # Logout from MQTT in case it is still connected
                # 2022-11-08: Why is MQTT Logout necessary?
                self.mqtt_disconnect()
        else:
            log.error("Unable to establish serial connection to the modem")

        return self.has_network

    def command_at(self):
        """
        Send AT command to modem
        Standard testing for serial communication
        response is OK if serial communication with modem
        is successful.
        """
        return self.send_command_check("")

    def _send_command(self, command: str, prefix_at: bool = True):
        """
        Format and send a command to the SARA-R4 modem.
        Section 1.3.2 of the SARA-R4 AT Commands Manual describes the
        command line syntax: `AT<command_name><string><S3_character>`

        Note: The factory-programmed `<S3_character>` (command line
        termination character) is "\r" and _not_ "\r\n".
        """

        # Clear the serial buffer by reading its contents, per Section 5.2 of
        # the SARA-R4 Application Development Guide: "The DTE should flush the
        # AT channel (i.e. check if there is data waiting to be read) before
        # sending a new AT command." One reason is that the AT channel may
        # contain Unsolicited Result Codes (URCs), Section 2.2.5 of the SARA-R4
        # AT Commands Manual.
        #
        residual = self.serial.read()
        # Use the following for debugging residual content on the serial buffer,
        # particularly `\r\n` terminators (#602):
        if residual is not None:
            log.warning("_send_command() serial.read(): {}".format(repr(residual)))

        serial_message = "{}{}".format("AT" if prefix_at else "", command)
        # NOTE: by default the modem echoes the command and <S3_character>
        # terminator to the serial interface (Section 10.20 of the SARA-R4 AT
        # Commands Manual) making the following debug log statement redundant
        # under normal circumstances. Uncomment the following line only when
        # troubleshooting command send problems.
        #
        # log.debug("Sending command: {}".format(repr(serial_message)))
        self.serial.write("{}\r".format(serial_message))

    def read_response(self):
        """
        Read the response.

        NOTE: mostly just used for development.
        """
        response = ""
        try:
            response += self.serial.read().decode("utf-8")
        except Exception as serial_exc:
            # Nothing available to read via serial?
            log.debug("read_response(): Exception {0}".format(serial_exc))

        return response

    def send_command_check(
        self,
        command: str,
        command_timeout: int = MODEM_STANDARD_RESPONSE_TIMEOUT,
        silent_timeout: bool = False,
        prefix_at: bool = True,
    ) -> bool:
        """
        Format the command and send it to modem and compare the
        response with expected response ("OK").
        """

        response = self.send_command_read(
            command, command_timeout, silent_timeout, prefix_at
        )

        return MODEM_RESPONSE_OK in response.split("  ")

    def send_command_read(
        self,
        command: str,
        command_timeout: int = MODEM_STANDARD_RESPONSE_TIMEOUT,
        silent_timeout: bool = False,
        prefix_at: bool = True,
    ) -> str:
        """
        Format the command, send it to modem, and read the response

        Arguments:
            command (str): AT command **without** the `AT` prefix.
            command_timeout (int): maximum timeout for the command.

        Returns:
            str: command output

        Raises:
            None
        """
        self._send_command(command, prefix_at)
        # Wait for a response to become available on the UART interface.
        # See #602 (comment 357067) for details of the design decision.
        time.sleep_ms(10)

        # Loop until a Final Result Code (FRC) has been returned or the timeout
        # period has been exceeded. The outer loop tests the timeout period, a
        # conditional test breaks out of the loop earlier when a Final Result
        # Code is read from the modem.

        timed_out = False
        response = ""
        response_str = ""
        loop_count = 0
        time_in = time.ticks_ms()

        while not timed_out:
            # Some commands can take a significant time to return a FRC, e.g.
            # the  MQTT Login command `UMQTTC=1` which has a maximum response
            # time "< 120 s" according to the data sheet and in typically takes
            # several seconds to return the FRC and a URC indicating login
            # status.
            #
            # Poll `self.serial.any()` and avoid thrashing the UART interface
            # by throttling the number of iterations through the loop with a
            # sleep delay chosen by trial-and-error. The time between data
            # becoming available and it being read will be half the following
            # delay time, on average.
            if self.serial.any() == 0:
                # Blink the LED here when #662 is resolved.
                time.sleep_ms(25)
                loop_count += 1
            else:
                # !!! Should be guaranteed that read_str will be non-empty
                # !!! so the decode will succeed without error, but decode has
                # !!! been a fragile operation generating tracebacks in the past,
                # !!! so be cautious about this.
                try:
                    read_str = self.serial.read()
                    response += read_str.decode("utf-8")
                    # Split the response string into a list
                    # Assumes modem responses are returned in verbose mode (default).
                    # - Strips trailing `\r` character from command echo elements
                    # - Strips additional trailing `\r` characters from `UMQTT` command
                    #   echo and text string elements
                    # - Removes empty elements from the list caused by the normal
                    #   occurrence of `\r\n\r\n\` between text string and response
                    #   code, as well as the abnormal occurrence of `\r\n\r\r\n` in the
                    #   trailing (after the response code) response from the `UMQTTC=1`
                    #   command
                    response_list = list(
                        filter(None, (item.strip() for item in response.split("\r\n")))
                    )
                    response_str = "  ".join(response_list)
                    # Look for the Final Result Code in the response list.
                    # Expect only "OK" or "ERROR".
                    if MODEM_RESPONSE_OK in response_list:
                        log.debug(response_str)
                        break  # Exit the while loop
                    elif (MODEM_RESPONSE_ERROR in response_list) or any(
                        item.startswith("+CME ERROR") for item in response_list
                    ):
                        log.error(response_str)
                        break  # Exit the while loop
                except AttributeError as serial_exc:
                    log.error(
                        "AttributeError in send_command_read(): {0}".format(serial_exc)
                    )
                    time.sleep_ms(25)
                except Exception as serial_exc:
                    log.error(
                        "Exception in send_command_read(): {0}".format(serial_exc)
                    )
                    time.sleep_ms(100)

            timed_out = time.ticks_diff(time.ticks_ms(), time_in) > command_timeout

        # # TRACE-level logging:
        # if loop_count > 1:
        #     log.debug("Looped {0} times waiting for final result code".format(loop_count))

        if timed_out:
            # raise ModemTimeout("AT{0}  Final result code not received within {1:d} ms".format(command, command_timeout), response_str)
            found = False
            if not silent_timeout:
                # Write a timeout message to the log
                if len(response_str) == 0:
                    log.error(
                        "AT{0}  No response received within {1:d} ms".format(
                            command, command_timeout
                        )
                    )
                else:
                    log.error(response_str)
                    log.error(
                        'Response "{0}" not received within {1:d} ms'.format(
                            MODEM_RESPONSE_OK, command_timeout
                        )
                    )

        return response_str

    def set_network(
        self,
        apn: str = "hologram",
    ):
        """Setup network
        Register to Vodafone NZ
        Use hologram sim card

        NOTE: only used in the provision step.
        """
        operator = "53001"
        log.info("Setting up the network")

        # deregister to network
        self.send_command_check("+COPS=2")

        # set to minimum function
        self.send_command_check("+CFUN=0")

        # set mno to VF
        self.send_command_check(MODEM_COMMAND_MNO + "=19")

        # reset
        log.info("Reset modem wait for 15s")
        self.send_command_check("+CFUN=15")
        time.sleep(15)

        # set APN
        command = '+CGDCONT = 1,"IP","{}"'.format(apn)
        self.send_command_check(command)
        log.info("Registering to Vodaphone. This will take upto 3 minutes")
        self.send_command_check("+COPS=?", command_timeout=MODEM_MQTT_CONNECT_TIMEOUT)
        command = '+COPS=1,2,"{}"'.format(operator)
        self.send_command_check(command, command_timeout=MODEM_MQTT_CONNECT_TIMEOUT)

        return self.check_network()

    def check_network(self):
        """
        Check if the modem is connected to the network by testing the
        IP address returned by the PDP context definition command
        (Section 13.4 of the SARA-R4 AT Commands Manual). The IP
        address will be "0.0.0.0" if there is no network connection.
        Example: '+CGDCONT: 1,"IP","hologram","0.0.0.0",0,0,0,0  OK'
        """

        command = MODEM_MESSAGE_PDP_DEF + "?"
        response = self.send_command_read(command)

        self.has_network = '"0.0.0.0"' not in response

        return self.has_network

    def acquire_network(self):
        """
        Wait for a period of time for an IP address to be automatically
        acquired. On timeout, execute a soft reset of the modem and check
        again. Sets modem.has_network to the network status.
        """

        # log.info("Verifying network connectivity")
        # The following will set self.has_network
        self.check_network()

        # Check every 2 seconds for an IP address obtained via automatic
        # network registration, timing-out after 10 seconds.
        timed_out = False
        time_in = time.ticks_ms()
        while not self.has_network and not timed_out:
            time.sleep(2)
            self.check_network()
            timed_out = time.ticks_diff(time.ticks_ms(), time_in) > 10000

        # If have still not registered automatically and obtained
        # an IP address then soft reset the modem and repeatedly
        # check for an IP address.
        #
        # Note: If there is no network connectivity (worst-case)
        # then this process will take 40 seconds to execute. May
        # want instead to "fail fast" and/or make this an async
        # check to allow measurements and other processing to take
        # place while waiting for the modem to register to the
        # network and obtain an IP address.
        if not self.has_network:
            log.warning(
                "Automatic network registration failed, soft resetting the modem"
            )
            self.send_command_check("+CFUN=15")
            log.debug("Waiting 15 seconds for automatic registration after soft reset")
            time.sleep(15)
            # Try 5 times to see if an an IP address has been
            # obtained, waiting 5 seconds between checks.
            self.check_network()
            checks = 1
            while not self.has_network and checks < 6:
                log.error("No IP address after network check {0}".format(checks))
                time.sleep(5)
                self.check_network()
                checks += 1

        if not self.has_network:
            log.error("Unable to obtain an IP address from the LTE network")

    def get_signal_power(self):
        # Retrieve signal power information
        # - Single-instance problem solution follows.
        # - Requires generalisation to allow code reuse.
        # - Predicated on a response string formatted _exactly_ as
        #   `AT+CSQ  +CSQ: 10,99  OK`
        # itr: information text response
        # frc: final result code
        attempts = 0
        while self.signal_power is 99 and attempts < 3:
            response = self.send_command_read(MODEM_SIGNAL_QUALITY)
            # response[0] is an echo of command (including `\r`),
            # response[1] is <text>, often with the command text prefixed,
            # response[2] is final result code (expect this to be "OK")
            itr = response.split("  ")[1]
            # itr[0] is "+CSQ:" i.e. (MODEM_SIGNAL_QUALITY + ":")
            # itr[1] is <signal_power>,<qual>
            # <signal_power> can take values 0-31, 99
            # <qual> is not supported on the SARA-R410, and is
            # always set to 99 "Not known or not detectable".
            self.signal_power = int(itr.split()[1].split(",")[0])
            attempts = attempts + 1
            if self.signal_power == 99 and attempts < 3:
                log.debug("Retrying +CSQ request in 1 second")
                time.sleep(1)
        if self.signal_power == 0:
            log.warning("Cellular network RSSI <= -113 dBm")
        elif self.signal_power == 99:
            # Try again before failing
            log.error("Cellular network RSSI not known or not detected")
        else:
            log.info(
                "Radio signal strength: {0} ({1:d}%)".format(
                    self.signal_power, int(100 * self.signal_power / 31)
                )
            )

    def autobaud(self, desiredBaud: int = MODEM_DEFAULT_BAUD):
        """
        The baud rate on the shield may be not set to 115200
        This program open a UART port in each supported baud rate
        and set a command to change the baud rate of the shield to
        desired baud rate which is 115200.

        NOTE: only used in the provision step.
        """
        b = 0
        err = False
        while not err and b < NUM_SUPPORTED_BAUD:
            log.info("Trying {}".format(MODEM_SUPPORTED_BAUD[b]))
            Modem(baud=MODEM_SUPPORTED_BAUD[b])
            time.sleep(5)
            if self.command_at():
                if self.send_command_check("+IPR=115200"):
                    Modem(baud=desiredBaud)
                    time.sleep(5)
                    err = self.command_at()

            b = b + 1

    def configure(self):
        """
        Enforce a standard configuration for the modem.

        This method is intended to be called on first boot, to avoid
        polling/setting on each wake parameters which are stored in NVM.
        """
        # Enable automatic time zone update
        # !!! Originally set in initialise()
        response = self.send_command_read("+CTZU?")
        response = response.split("  ")
        if MODEM_RESPONSE_OK in response:
            # Expecting response to be ['AT+CTZU?', '+CTZU: <on_off>', 'OK']
            auto_timezone_update = response[1].split()[1]
            if auto_timezone_update is not "1":
                log.warning("Enabling automatic time zone update")
                self.send_command_check("+CTZU=1")

        # Make sure that both eDRX and PSM are disabled as both of
        # these will interfere with the delivery of MQTT packets.
        # !!! Originally from mqtt_connect()
        #
        # 2022-11-07: Not sure these are required to be set on _every_
        # MQTT connection, these settings should persist and both of
        # them are the default values! SARA-R4 AT Commands Manual References:
        # Section 7.24 eDRX setting +CEDRXS
        #   "0 (default and factory-programmed value): use of eDRX disabled"
        # Section 15.2 Power Saving Mode Setting +CPSMS
        #   "0 (default value): disable the use of PSM"
        #
        # 2022-11-25: Disable (comment-out) the setting of these parameters to
        # see if anything breaks.
        # 2023-02-19: Nothing broke.
        # self.send_command_check("+CPSMS=0")
        # self.send_command_check("+CEDRXS=0")

    def general_information(self):
        """
        Queries the modem for general information, as specified in the AT commands manual section 2.4
        """
        self.send_command_read("+CGMI")  # Manufacturer information
        self.send_command_read("+CGMM")  # Model identification
        self.send_command_read("+CGMR")  # Firmware version identification
        self.send_command_read(
            "+CGSN"
        )  # International Mobile station Equipment Identity (IMEI). Note: the <snt> parameter is not supported on teh SARA-R4
        self.send_command_read("ATI", prefix_at=False)  # Identification information
        self.send_command_read(
            "+CIMI"
        )  # International Mobile Subscriber Identity (IMSI)
        self.send_command_read(
            "+CCID"
        )  # Integrated Circuit Card ID (ICCID), a serial number identifying the SIM.
        self.send_command_read("+GCAP")  # Complete capabilities list

    def toggle_power(self):
        """Turn on the SparkFun SARA-R4 modem
        Pull down the power pin over 3 seconds
        and then return to high impedance mode
        """
        log.info("Toggling modem...")
        Pin(MODEM_POWER_PIN, Pin.IN, Pin.PULL_DOWN)
        time.sleep_ms(10 * MODEM_POWER_ON_PULSE_PERIOD)
        Pin(MODEM_POWER_PIN, Pin.IN, None)
        # 2022-11-07: Not certain why the following additional sleep
        # is implemented, because the power pin will stay at high
        # impedance indefinitely. Is it to allow a period for the
        # modem to start-up? If so, could perhaps instead test for
        # start-up completion with an `AT` loop and also measure the
        # typical startup period.
        time.sleep_ms(10 * MODEM_POWER_ON_PULSE_PERIOD)

    def power_on(self):
        """
        Turn on the SparkFun SARA-R4 modem when it is in the power-off or Power
        Saving Mode (PSM) with a valid VCC supply. Applies a low pulse on the
        PWR_ON input pin for a period within the minimum and maximum times
        specified in the data sheet.

        Section 1.6.1 of the SARA-R4 System Integration Manual

        From the data sheet:
        PWR_ON low time (s):
            Min: 0.15 Max: 3.20  Low time to trigger module switch on from power off mode
            Min: 0.15 Max: 3.20  Low time to trigger module wake-up from PSM deep sleep
            Min: 1.50            Low time to trigger module graceful switch off

        References
        1. SARA-R4 System Integration Manual
        2. SARA-R4 Data Sheet
        """
        # Should really check first whether the modem is _already_ powered-on.
        # If it is then this procedure will likely turn it off!
        responsive = self.send_command_check(
            "", command_timeout=100, silent_timeout=True
        )
        if responsive:
            # Modem is responding, therefore on already
            log.warning("power-on(): modem responded to 'AT'")
            log.warning("power-on(): skipping low pulse of PWR_ON")
        else:
            log.info("Powering-on")
            modem_PWR_ON = Pin(MODEM_POWER_PIN, Pin.OUT, value=1)
            modem_PWR_ON.off()
            time.sleep_ms(MODEM_POWER_ON_PULSE_PERIOD)
            modem_PWR_ON.on()
            # Takes just over 4 seconds for SARA-R4 to enter the operational
            # state after the start-up event. Measurements (ms): 4093, 4028,
            # 4304, ...
            #
            # Give a generous 5 seconds for the SARA-R4 to generate the
            # greeting text.
            poweron_timeout = 5000
            # Note: the `+CSGT` "Set Greeting Text" command is supported by
            # the SARA-R410M-02B-01 (SARA-R4 AT Commands Manual, Section 5.8).
            # Poll the modem serial interface for the greeting text.
            time_in = time.ticks_ms()
            loop_count = 0
            responsive = False
            timed_out = False
            start_ticks = time.ticks_ms()
            while not responsive and not timed_out:
                if self.serial.any() == 0:
                    time.sleep_ms(75)
                    loop_count += 1
                else:
                    # !!! Should be guaranteed that read_str will be non-empty
                    # !!! so the decode will succeed without error, but decode has
                    # !!! been a fragile operation generating tracebacks in the past,
                    # !!! so be cautious about this.
                    try:
                        read_str = self.serial.read().decode("utf-8")
                        response = "  ".join(
                            list(
                                filter(
                                    None,
                                    (item.strip() for item in read_str.split("\r\n")),
                                )
                            )
                        )
                        responsive = response == "SARA-R410M-02B-01 Operational"
                    except AttributeError as serial_exc:
                        log.error(
                            "AttributeError in power_on(): {0}".format(serial_exc)
                        )
                        time.sleep_ms(100)
                timed_out = time.ticks_diff(time.ticks_ms(), time_in) > poweron_timeout
            end_ticks = time.ticks_ms()
            if timed_out:
                log.warning(
                    "Expected greeting text not received within {:d} seconds, testing response to the AT command".format(
                        poweron_timeout
                    )
                )
                responsive = self.send_command_check(
                    "", command_timeout=100, silent_timeout=True
                )
            log.info(
                "SARA-R410M-02B-01 {0}operational in {1} ms".format(
                    "not " if not responsive else "",
                    time.ticks_diff(end_ticks, start_ticks),
                )
            )
            # Try setting the pin to a high-impedance input with no pull
            # resistor, relying on the SARA-R4 PWR_ON pin internal pull-up
            # resistor to maintain the high logic state. Suggested by
            # <https://forum.sparkfun.com/viewtopic.php?p=205151#p205151>
            modem_PWR_ON.init(mode=Pin.IN, pull=None)
            if modem_PWR_ON.value() == 0:
                log.error(
                    "MODEM_POWER_PIN pin at low logic level in high-impedance input mode after power-on"
                )
                log.info("Setting MODEM_POWER_PIN pin to output high logic level")
                modem_PWR_ON.init(mode=Pin.OUT)
                modem_PWR_ON.on()
            # else:
            #     # TRACE-level logging:
            #     log.debug(
            #         "MODEM_POWER_PIN pin logic level: {0}".format(modem_PWR_ON.value())
            #     )

        return responsive

    def power_off(self):
        """
        Turn off the SparkFun SARA-R4 modem using the "+PWROFF" AT command.
        """
        log.info("Powering-off modem")
        # Need to make sure that MODEM_POWER_PIN is in a high state. If it is
        # in a low state then the SARA-R4 will restart immediately after
        # power-off.
        modem_PWR_ON = Pin(MODEM_POWER_PIN, Pin.IN, None)
        # # TRACE-level logging:
        # log.debug(
        #     "MODEM_POWER_PIN value in high-impedance input mode: {0}".format(
        #         modem_PWR_ON.value()
        #     )
        # )
        if modem_PWR_ON.value() == 0:
            # This should not occur under normal operation. Raise an error and
            # try to recover from the situation.
            log.error(
                "MODEM_POWER_PIN at low logic level in high-impedance input mode prior to power-off"
            )
            log.info(
                "Setting MODEM_POWER_PIN to output high logic level then switching to high-impedance input mode"
            )
            modem_PWR_ON.init(mode=Pin.OUT)
            modem_PWR_ON.on()
            modem_PWR_ON.init(mode=Pin.IN, pull=None)
            if modem_PWR_ON.value() == 0:
                log.error("MODEM_POWER_PIN still at low logic level")
                log.info("Reasserting high logic level in output mode")
                modem_PWR_ON.init(mode=Pin.OUT, value=1)
                if modem_PWR_ON.value() == 0:
                    # Log as a critical error and proceed
                    log.critical(
                        "Unable to set PWR_ON pin to high logic level, modem may remain powered-on or become uncommunicative"
                    )

        self.send_command_check("+CPWROFF", command_timeout=1500)
        # +CPWROFF command maximum response time is quoted to be "< 40 s".
        # While it would be preferable to delay until the "OK" Final Response
        # Code (FRC) has been received, the SARA-R4 will silently and
        # immediately power-off the module, i.e. _without_ returning a FRC, in
        # the circumstance that the modem was powered-on at the same time as
        # the ESP32 power was connected. This is a problem which needs to be
        # fixed, but until then use a reduced timeout of 1.5 seconds (10x the
        # measured shutdown period) as a compromise.
        #
        # Measured delay to shutdown after FRC receipt is around 150 ms. Wait
        # this long and then confirm the modem is unresponsive to "AT".
        time.sleep_ms(200)
        # !!! Not sure bombarding the modem with AT commands to confirm
        # !!! power-off is the best approach when the +CPWROFF command has
        # !!! returned "OK". An alternate approach is to take the modem at
        # !!! its word that it will power-off in the immediate future, even
        # !!! if it's responsive now.

        # Allow 1 second for the SARA-R4 to become unresponsive to "AT".
        poweroff_timeout = 1000
        loop_count = 0
        time_in = time.ticks_ms()
        timed_out = False
        responsive = self.send_command_check("", command_timeout=0, silent_timeout=True)
        start_ticks = time.ticks_ms()
        while responsive and not timed_out:
            responsive = self.send_command_check(
                "", command_timeout=0, silent_timeout=True
            )
            timed_out = time.ticks_diff(time.ticks_ms(), time_in) > poweroff_timeout
            loop_count += 1
        end_ticks = time.ticks_ms()
        # TRACE-level logging:
        log.debug(
            "Power-off {0}, elapsed time: {1} ms".format(
                "failed" if responsive else "succeeded",
                time.ticks_diff(end_ticks, start_ticks),
            )
        )
        # Check that the modem is indeed off
        if self.send_command_check("", command_timeout=0, silent_timeout=True):
            # Received a response when we should have received a timeout
            log.error("Failed to power-off the modem with the `+CPWROFF` AT command")
            log.info("Attempting power-off via the PWR-ON pin")
            modem_PWR_ON.init(mode=Pin.OUT)
            modem_PWR_ON.off()
            time.sleep_ms(MODEM_POWER_OFF_PULSE_PERIOD)
            modem_PWR_ON.on()
            # Power-off is immediate, check response to `AT`
            if self.send_command_check("", command_timeout=0):
                log.error("Failed to power-off the modem via the PWR-ON pin")
            else:
                log.info("Power-off confirmed")
        else:
            log.info("Power-off confirmed")

        return responsive

    def get_network_time(self):
        """
        Get current time from the modem and convert to seconds since J2000 in
        New Zealand Standard Time (+12 hours).

        The "+CCLK" command returns the time as a string formatted as
        '"YY/MM/DD,hh:mm:ss+TZ"' (double quotes included). Note that the time
        is always UTC, regardless of the Time Zone (TZ) portion of the string.
        The TZ information is updated during modem network registration when
        automatic time zone update is enabled via the "+CTZU" command, and can
        range from -96 to +96. On failure, a CME ERROR will be returned.
        """
        response = self.send_command_read("+CCLK?")
        # Could parse the response with str.split() and str.replace() per the
        # following transcript:
        #
        # >>> response = modem.send_command_read("+CCLK?")
        # 2023-02-19 14:52:22  DEBUG  modem: AT+CCLK?  +CCLK: "23/02/19,02:52:22+52"  OK
        # >>> response
        # 'AT+CCLK?  +CCLK: "23/02/19,02:52:22+52"  OK'
        # >>> response.split("  ")[1]
        # '+CCLK: "23/02/19,02:52:22+52"'
        # >>> response.split("  ")[1].split(" ")[1]
        # '"23/02/19,02:52:22+52"'
        # # Note the double quote marks, use str.replace() to remove these and
        # # the other punctuation. str.translate() does not appear to be
        # # implemented in MicroPython.
        # >>> response.split("  ")[1].replace('"','').split(" ")[1].split("+")[0].replace("/"," ").replace(":"," ").replace(",", " ").split()
        # ['23', '02', '19', '02', '52', '22']
        # >>> timestamp = ['23', '02', '19', '02', '52', '22']
        # >>> timestamp[0] = "20" + timestamp[0]
        # >>> timestamp.append("0")
        # >>> timestamp.append("0")
        # >>> time.mktime([eval(item) for item in timestamp])
        # 730090342

        matches = ure.search(
            r"(\d\d)\/(\d\d)\/(\d\d)\,(\d\d)\:(\d\d)\:(\d\d)([\+\-]\d\d)(?:\,(\d))?",
            response,
        )
        if matches is None:
            log.error("Unable to obtain network time")
            NZST = None
        else:
            data = [0] * 8
            for i in range(len(data)):
                # Value will be None if it was optional but not provided
                val = matches.group(i + 1)
                if val:
                    data[i] = int(val)
                else:
                    break

            networktime = time.mktime(
                (2000 + data[0], data[1], data[2], data[3], data[4], data[5], 0, 0)
            )

            # Add 12 hours to network time
            NZST = networktime + 12 * 60 * 60

            # log.debug("Network time: {0} UTC".format(isoformat(networktime, sep=" ")))
            log.info("Network time: {0} NZST".format(isoformat(NZST, sep=" ")))

        return time.localtime(NZST)

    def mqtt_reset(self):
        """Reset MQTT client profile"""
        self.send_command_check("+UMQTTNV=0")

    def on_off_switch(self):
        """Turn the modem off/on"""
        if self.has_serial:
            self.has_serial = self.power_off()
            self.send_command_check("+CPWROFF")
        else:
            self.has_serial = self.power_on()
            self.send_command_check("+CPWRON")

    def mqtt_set_client(self, client_id, server):
        """Set MQTT client profile and save to NVM

        Arguments:
            client_id (str): a unique client id
            server (str): url of mqtt broker

        """
        command = '{}"{}"'.format("+UMQTT=0,", client_id)
        self.send_command_check(command)

        command = '{}"{}"'.format("+UMQTT=2,", server)
        self.send_command_check(command)

        # Store current MQTT client profile parameters to NVM
        err = self.send_command_check("+UMQTTNV=2")

        return err

    def set_http_connection(self, server: str):
        """Set http connections

        Arguments:
            server (str): server that is passed in, either mattermost or MMW
        """

        self.http_connect(server)
        # command = '{}"{}"'.format("+UMQTT=0,", client_id)
        # self.send_command_check(command)

        # command = '{}"{}"'.format("+UMQTT=2,", server)
        # self.send_command_check(command)

        # # Store current MQTT client profile parameters to NVM
        # err = self.send_command_check("+UMQTTNV=2")

        return err

    def mqtt_connect(self):
        """Connect to MQTT broker

        Returns:
            bool: False for unable to connect
            True for successfully connect
        """
        # Set MQTT client profile parameters to values stored previously in NVM
        #
        # After logout (AT+UMQTTC=0), MQTT settings need to be re-set
        # individually or restored from the NVM with the AT+UMQTTNV=1 command
        # to login again.
        self.send_command_check("+UMQTTNV=1")

        # Keep alive pings
        command = "+UMQTT=10,{}".format(MODEM_MQTT_PING_PERIOD)
        self.send_command_check(command)

        # 2022-11-11: This command is taking several seconds to
        # complete, check to see if reconnection to the MQTT broker is
        # strictly necessary on each wake, or whether the server
        # can/does cache the connection. See the Eclipse forum and
        # documentation for advice on connection caching.
        command = "{}={}".format("+UMQTTC", 1)
        err = self.send_command_check(
            command, command_timeout=MODEM_MQTT_CONNECT_TIMEOUT
        )

        return err

    def mqtt_publish(self, topic, message):
        """publish a mqtt message
        Attributes:
            topic (str): a topic is the destination of the message
            we use topic to classify different types of data
            message (str): a message can be anything as long as it is a string

        Returns:
            bool: False for unable to send
            True for send successful
        """
        command = '{}"{}","{}"'.format("+UMQTTC=2,0,0,", topic, message)
        err = self.send_command_check(
            command, command_timeout=MODEM_MQTT_CONNECT_TIMEOUT
        )
        return err

    # sending directly to mattermost
    def http_publish_mattermost(self, message):
        """publish a mqtt message
        Attributes:
            topic (str): a topic is the destination of the message
            we use topic to classify different types of data
            message (str): a message can be anything as long as it is a string

        Returns:
            bool: False for unable to send
            True for send successful
        """
        # command = '{}"{}","{}"'.format("+UMQTTC=2,0,0,", topic, message)
        command = '{}"{}","{}"'.format(
            "+UHTTPC=1,5,",
            MATTERMOST_CHANNEL_PATH,
            "telemetryData",
            "Doms Straight to mattermost test",
        )
        err = self.send_command_check(
            command, command_timeout=MODEM_MQTT_CONNECT_TIMEOUT
        )
        return err

    def mqtt_disconnect(self):
        """Disconnect from the mqtt broker

        Returns:
            bool: False for fail to disconnect
            True successfully disconnect
        """
        command = "+UMQTTC=0"
        err = self.send_command_check(command)
        return err

    def http_connect(self, server="data.envirodiy.org"):
        """
        Attributes:
            server (str): hostname of server to connect to. If not provided, defaults to MonitorMyWatershed server.
        """
        # connect to server
        if server == MATTERMOST_SERVER:
            self.send_command_read('+UHTTP=1,1,"{0}"'.format(server))
            return self.send_command_read(
                "+UHTTP=1,6"
            )  # Setting up HTTPS on this mattermost profile

        return self.send_command_read('+UHTTP=0,1,"{0}"'.format(server))

    def http_send(
        self,
        registration_token: str,
        sampling_feature: str,
        timestamp: str,
        values: dict,
        path="/api/data-stream/",
    ):
        """
        Sends a MonitorMyWatershed-compatible HTTP POST request

        Arguments:
            registration_token (str): Sensor registration token. Used as authentication
            sampling_feature (str): UUID of sensor Sampling Feature
            timestamp (str): iso 8601 timestamp of sensor reading. Must include TZ data.
                For example: 2022-05-12T22:29:51+12:00
            values (dict): dict of mapping [Sensor ID -> sensor reading]
            path (str): URI path to post to

        Ref: https://github.com/ODM2/ODM2DataSharingPortal/blob/main/doc/example_rest_requests.md

        Returns:
            True if packet was successful
        """

        # set auth headers
        # MonitorMyWatershed only supports HTTP, so the security of this is dubious
        self.send_command_read(
            '{0}=0,9,"0:TOKEN:{1}"'.format(
                MODEM_COMMAND_HTTP_CONTROL, registration_token
            )
        )

        # Construct data
        data = {
            "sampling_feature": sampling_feature,
            "timestamp": timestamp,
        }
        data.update(values)
        data_str = json.dumps(data).encode("utf-8")

        # write to temporary file on modem
        self.file_write(HTTP_POST_DATA_FILE, data_str)

        # POST the data to the server
        return "OK" in self.send_command_read(
            '{0}=0,4,"{1}","post_resp",{2},4'.format(
                MODEM_COMMAND_HTTP_COMMAND, path, HTTP_POST_DATA_FILE
            )
        )

    def http_get_error(self):
        """
        Check for any errors from the HTTP commands

        ref: ublox SARA-R4/N4 series AT commands manual, Appendix A.6

        Returns:
            str: error string
        """
        return self.send_command_read("{0}=0".format(MODEM_COMMAND_HTTP_ERROR))

    def file_write(self, filename: str, data: str, append=False):
        """
        Write some data to a file on the modem.

        Arguments:
            filename (str): filename on modem
            data (str): utf-8-encoded data to write
            append (bool): don't delete file before writing (default False)

        Returns:
            True if successful
        """

        if not append:
            # if it fails to delete, just let this command log an error
            log.debug("Deleting file from modem: {0}".format(filename))
            self.send_command_read(
                '{0}="{1}"'.format(MODEM_COMMAND_FILE_DELETE, filename)
            )

        self.send_command_read(
            '{0}="{1}",{2}'.format(MODEM_COMMAND_FILE_WRITE, filename, len(data))
        )
        time.sleep(0.1)
        self.serial.write(data)
        time.sleep(0.5)  # give it some time to upload

        # once all bytes have been written, should say OK
        response = self.read_response()
        log.debug(response.replace("\n", "").replace("\r", " "))
        if "OK" not in response:
            raise ModemFileError("Writing file {0} failed".format(filename))

        return True
