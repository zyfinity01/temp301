# Change Log

## Revision 4.0 (May 2022)

### New Features

- SDI-12 operation is driven solely by the ESP32; the I/O extender is no longer used for SDI-12 functions.
- The rain gauge counter is directly connected to the I/O extender, allowing the bucket tip count to be read over the I2C bus.
- Adds header blocks for secure connection of the SparkFun SARA-R4 LTE CAT M1/NB-IoT Shield to the underside of the main board.
- Operational cellular network connection via the ublox SARA-R410M-02B cellular module and Hologram SIM on the SparkFun Shield.
- Data transmission by MQTT protocol to test server implemented.

### Bug Fixes

- Use the correct footprint for N-MOSFETs`Q501` and `Q502`on the PCB layout, restoring their original orientation.
- Remove the multiplexer from the rain gauge circuit, reducing the IC count by one.
- Reverse polarity protection for 12 V supply functions as intended.

## Revision 3.1 (October 2021)

<!--
Shown in the current photograph in the [Hardware Setup](docs/technical#hardware-setup) section of the technical docs.
-->

### Bug fixes

Operating as intended by making the following physical modifications to the PCB:

- Rotate N-MOSFETs `Q501` and `Q502` 120 degrees on the manufactured PCB to work-around the footprint mismatch.
- Use a jumper wire to connect a pull-down resistor to the multiplexer output, allowing the ESP32 bootloader to run on startup.
- Use jumper wires to connect spare output pins on the I/O extender to `SDI_EN` and  `SDI_FOut`; update SDI-12 driver to use I/O extender for `SDI_EN` and  `SDI_FOut`.

### Documentation

- H. Li, _Development of an IoT system for Environmental Monitoring_, Honours Report, Victoria University of Wellington (2021).

## Revision 3.0 (September 2021)

### New features

- Single-board PCB design based on surface-mount components.
- Tipping bucket rain gauge interface and counting circuit.
- Terminal block interface for UART connection to an external modem.
- Terminal block interface for I2C bus.

### Known Problems

Non-operational due to the following issues:

- N-MOSFET `Q501` and `Q502` are incorrectly connected due to an incorrect footprint in the PCB layout.
- ESP32 unable to enter bootloader on startup due to multiplexer direct connection to ESP32 `GPIO2`.
- ESP32 `GPIO34` and `GPIO35` are connected as outputs `SDI_EN` and  `SDI_FOut` to the SDI-12 interface circuit, but `GPIO34` and `GPIO35` are input-only pins.
- Reverse polarity protection amended but still does not protect the board from damage if the power is misconnected.

## Revision 2.0 (November 2020)

Final revision of the 2020 project using an ESP32 DevKit-C and header board configuration.

### New features

- SDI-12 interface via expansion board headers and driver
- External 12 V power on SDI-12 expansion board.
- Modem interface headers on main board holding the ESP32-DevKit-C.

### Known Problems

- Reverse polarity protection on 12 V power input does not protect the board from damage if the power is misconnected.

### Documentation

- J. Behrent, _Development of an IoT System for Environmental Monitoring_, Honours Report, Victoria University of Wellington (2020)
- B. Secker, _Development of an IoT System for Environmental Monitoring: Software_, Honours Report, Victoria University of Wellington (2020)

---
