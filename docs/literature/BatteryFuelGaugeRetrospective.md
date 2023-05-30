# Battery Fuel Gauge Retrospective and Lessons Learnt

## Research we did - summary of datasheets

Background investigation was completed and compiled into a LaTeX document found in issue #15 [LaTex-Document](https://gitlab.ecs.vuw.ac.nz/course-work/engr301/2023/group3/data-recorder/uploads/ea0835b59d4042676c8adcc2486e9ccc/BQ34Z110_Battery_Fuel_Gauge_and_Alarm_Battery_12V_7Ah.pdf). By looking through the datasheet for the BQ34Z110, it was realized that the flash memory on the chip would need to be configured for our particular application to work. I2C communication with the chip would need to be implemented for communication between the onboard ESP-32 microprocessor and the BQ34Z110, there were plenty of examples of how this communication could be achieved with an outline of simple and complicated methods depending on the level of customization. We investigated the supplied 12V 7Ah lead acid battery specified, while this is a standard battery to be implemented with a data recorder, it does limit our options for battery fuel gauge ICs. The selected battery fuel gauge IC needs to be compatible with the internal chemistry of the battery to be able to correctly collect data about the battery, the lead-acid internal chemistry is specified as compliant with the BQ34Z110.

### I2C communication

The ESP32 on the data recorder runs micropython, which has a library for I2C communication. This was used to communicate with the battery fuel gauge to send and receive data between the ESP32 and the BQ34Z10.

The below code initialized I2C and instructs all devices on the line to return their addresses. The BQ34Z110 has an address of 85 for this application, we observed the correct vale returning as well as the manufacturer information using this script.

```python
from machine import I2C
i2c = I2C(0)
i2c.scan()
```

You could then communicate using the below code, where the contents of the array in `bytearray()` were the command to be sent. The list of commands you can use is in the [BQ34Z110-data-sheet](https://www.ti.com/lit/ds/symlink/bq34z110.pdf?ts=1685152355290&ref_url=https%253A%252F%252Fwww.ti.com%252Fproduct%252FBQ34Z110). `0x6e` is the "manufacturer name" command. On reading, the returned bytes would start with "Texas Inst.". In the `readfrom()` function, the second parameter is the number of bytes to be read from the I2C line.

```python
i2c.writeto(85, bytearray([0x6e])
i2c.readfrom(85, 64)
```

## Why it didn't work

We would need to configure the BQ34Z110 for our particular purpose by programming the flash memory. There are default values for all the data flash memory settings, but some would need to be altered to work with the chemistry of the battery as the chemistry affects the rate of discharge and current state of charge. [This](https://www.ti.com/lit/an/slua790/slua790.pdf?ts=1683050503158&ref_url=http%253A%252F%252Fti.com%252Fproduct%252FBQ34110) document reviewed in issue #70 said to use the software provided by Texas Instruments, we tried to chase down the particular software as detailed in issue #71. The first software package that was attempted for use was BQSTUDIO, which was found to not support the BQ34Z110. Software specifically designed for the BQ34Z110 was found on the Texas Instruments website, however, this required hardware - a [BQ34Z110EVM](https://www.digikey.co.nz/en/products/detail/texas-instruments/BQ34Z110EVM/4090776) evaluation module to be used. As the BQ34Z110 is an old chip, this EVM board is no longer manufactured and the correct software required to pair with the board no longer receives updates or functions on any Windows machine older than Windows 7. Due to these circumstances of incompatibility, we conclude that the BQ34Z110 is not fit for purpose for this application, the battery fuel gauge IC needs to be upgraded to a newer version that is still compatible with a lead acid battery chemistry and has up to date software to configure the flash drive.

## How it could be made to work

After looking through data sheets and comparing the information to what we had found in the Texas Instruments forum, this shows that the BQ34Z110 is outdated, and therefore any software that we tried to use was not compatible with it. We recommend using a more up-to-date fuel gauge for this project. An example of one would be the [BQ34Z100-R2](https://www.ti.com/lit/ds/symlink/bq34z100-r2.pdf?ts=1685424793452&ref_url=https%253A%252F%252Fwww.ti.com%252Fproduct%252Fja-jp%252FBQ34Z100-R2%253Futm_source%253Dgoogle%2526utm_medium%253Dcpc%2526utm_campaign%253Dapp-null-null-gpn_jp-cpc-pf-google-jp_cons%2526utm_content%253DBQ34Z100-R2%2526ds_k%253DBQ34Z100-R2%2526DCM%253Dyes%2526gclid%253DEAIaIQobChMIqdC9oaac_wIVEFhgCh24yQU3EAAYASAAEgJr__D_BwE%2526gclsrc%253Daw.ds), this is a newer chip that is compatible with the BQSTUDIO software, is compatible with the selected lead-acid battery and has an available, and still being manufactured, [evaluation](https://www.ti.com/tool/BQ34Z100EVM) board. The other option for our particular application is to change the chemistry of our selected battery. We are currently running on a lead-acid battery supply that results in our using older chips manufactured by Texas Instruments and, therefore, older evaluation boards and software making the overall process more difficult. If we were to switch the battery chemistry to a lithium-ion or lithium-polymer such as the [battery](https://www.jaycar.co.nz/12-8v-7ah-lithium-deep-cycle-battery/p/SB2210)[option](https://www.jaycar.co.nz/12-8v-7ah-lithium-deep-cycle-battery/p/SB2210), this would allow us to select a newly manufactured [battery fuel gauge chip](https://www.ti.com/lit/ds/symlink/bq28z620.pdf?ts=1685452445347&ref_url=https%253A%252F%252Fwww.ti.com%252Fpower-management%252Fbattery-management%252Fproducts.html). Selecting a newly manufactured chip gives us the advantage of better assistance from Texas Instruments on the functionality of the chip and allows us to use a new [evaluation board](https://www.ti.com/tool/BQ28Z620EVM-071) that is easier to use and compatible with the newest version of BQSTUDIO.

---
