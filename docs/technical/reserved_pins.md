# Reserved pins on the ESP32

![esp32 pinout](figures/esp32_pinout.png)

The following tables provides the GPIO number, pin number, pinout name, use, and additional notes about each GPIO pin.

- If the  *Used for* column is empty, the pin has not yet been reserved.
- The *Alt* column indicates any alternative GPIO pins for the current use.

This should only be filled in if the pin is currently reserved.
If any non-reserved pin can be used it will say *any*, and if no other pins can be used it will say *none*.

Source for some of the pins: <https://randomnerdtutorials.com/esp32-pinout-reference-gpios/>. There is more information here, so it is worth looking at before adding a new component.\*

The accessible pins on the DevKitC are: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33, 34, 35, 36, and 39.

## System

These pins are reserved by the ESP32.
It is not possible to use these pins for anything else.

| GPIO Number | Pin Number | Name | Used for | Alt  | Special Functions | Notes |
| ----------- | ---------- | ---- | -------- | ---- | ----------------- | ----- |
| 1           | 41         | TXD0 | USB      | none | TX                | UART0 |
| 3           | 40         | RXD0 | USB      | none | RX                | UART0 |
| 6           | 31         | CLK  | Flash    | none |                   |       |
| 7           | 32         | SD0  | Flash    | none |                   |       |
| 8           | 33         | SD1  | Flash    | none |                   |       |
| 9           | 28         | SD2  | Flash    | none |                   |       |
| 10          | 29         | SD3  | Flash    | none |                   |       |
| 11          | 30         | CMD  | Flash    | none |                   |       |
| 16          | 25         | IO16 | SPIRAM   | none | RX                | UART2 |
| 17          | 27         | IO17 | SPIRAM   | none | TX                | UART2 |

## Base Board

| GPIO Number | Pin Number | Name | Used for      | Alt                    | Special Functions | Notes                                                    |
| ----------- | ---------- | ---- | ------------- | ---------------------- | ----------------- | -------------------------------------------------------- |
| 0           | 23         | IO0  | LED - G       |                        | ADC, RTC          | Outputs PWM on boot.                                     |
| 2           | 22         | IO2  | LED - R       | any                    | ADC, RTC, SPI     | Using UART1.                                             |
| 4           | 24         | IO4  | (LED - B)     | any                    | ADC, RTC, SPI     |                                                          |
| 5           | 34         | IO5  | SD - CS       | 15                     | SPI               |                                                          |
| 14          | 17         | IO14 | WiFi - EN     | any                    | ADC, RTC, SPI     | Outputs PWM on boot. Wakes wireless comms.               |
| 15          | 21         | IO15 | Battery - EN  |                        | ADC, RTC, SPI     | Outputs PWM on boot.                                     |
| 18          | 35         | IO18 | SD - CLK      | 14                     | SPI               |                                                          |
| 19          | 38         | IO19 | SD - DO       | 12                     | SPI               |                                                          |
| 23          | 36         | IO23 | SD - DI       | 13                     | SPI               |                                                          |
| 25          | 14         | IO25 | Battery - DAC | 26                     | DAC, ADC, RTC     | DAC to calibrate battery.                                |
| 26          | 15         | IO26 | Modem - Tx    |                        | DAC, ADC, RTC     |                                                          |
| 27          | 16         | IO27 | Modem - EN    | any                    | ADC, RTC          | Enable battery.                                          |
| 32          | 12         | IO32 | (Rain gauge)  | any (output capable)   | ADC, RTC          | Input 1. Use internal pull up                            |
| 33          | 13         | IO33 | (Rain gauge)  | any (output capable)   | ADC, RTC          | Input 2. Use internal pull up                            |
| 34          | 10         | IO34 | (Reserved)    |                        | ADC, RTC          | Input only. Reserved for future use.                     |
| 35          | 11         | IO35 | Modem Rx      | any (pref. input only) | ADC, RTC          | Input only. Using UART1.                                 |
| 36          | 5          | SVP  | Battery - ADC | 34, 35, 39             | ADC, RTC          | Input only. Read battery voltage. Needs 0.1uF capacitor. |

Items in brackets indicate that they may not be in use on the base board, so can be used on expansion boards.
In the case of *LED - B*, the pin may be freed up if deemed to not be necessary.
These pins may be used for something in future revisions, so expansion boards using these pins may not be compatible with newer base boards.

## Expansion Boards

The following table contains a template for expansion boards.

| GPIO Number | Pin Number | Name | Used for | Alt | Special Functions | Notes                     |
| ----------- | ---------- | ---- | -------- | --- | ----------------- | ------------------------- |
| 12          | 18         | IO12 |          |     | ADC, RTC, SPI     | Do not pull high on boot. |
| 13          | 20         | IO13 |          |     | ADC, RTC, SPI     |                           |
| 21          | 42         | IO21 |          |     | I2C               |                           |
| 22          | 39         | IO22 |          |     | I2C               |                           |
| 39          | 8          | SVN  |          |     | ADC, RTC          | Input only                |

It is possible to use I2C on pins 21 and 22, and UART or SPI can be used with an IO MUX to redirect the driver to one of the 5 pins.
Up to two SPI devices can be connected.

### SDI-Expansion

| GPIO Number | Pin Number | Name | Used for   | Alt | Special Functions | Notes                     |
| ----------- | ---------- | ---- | ---------- | --- | ----------------- | ------------------------- |
| 12          | 18         | IO12 | SDI - EN   | any | ADC, RTC, SPI     | Do not pull high on boot. |
| 13          | 20         | IO13 | SDI - FOut | any | ADC, RTC, SPI     |                           |
| 21          | 42         | IO21 | SDI - Dir  | any | I2C               |                           |
| 22          | 39         | IO22 | SDI - Tx   | any | I2C               |                           |
| 39          | 8          | SVN  | SDI - Rx   | any | ADC, RTC          | Input only                |

**Note:** when calling a pin in code, use the GPIO number, e.g. `machine.Pin(gpio_num, Pin.IN)`

- All output pins can be used for PWM.
- Any pins that output PWM on boot will remain high until set low.
- Input only pins do not have internal pull-up/pull-down resistors.
- All other pins are low on boot.
- The max current draw per GPIO is 40mA.
- All GPIO pins can be configured as interrupts.
- ADC pins are 12-bit analog to digital converters.
- DAC pins are 8-bit digital to analog converters.
- RTC pins can be used in deep sleep with the ULP.
- The RTC numbering is different from the GPIO numbering.

---
