# Battery Fuel Gauge Retrospective and Lessons Learnt

## Research we did - summary of datasheets

Backgound investigation was completed and compiled into a LaTeX doucment found in issue #15. By looking through the datasheet for the BQ34Z110, it was realised that the flash memory on the chip would need to be configured for our particular application to work. I2C communication with the chip would need to be implemented for communication between the onboard ESP-32 microprocessor and the BQ34Z110, there was plenty of examples of how this communication could be achieved.

### I2C communication

The ESP32 on the datarecorder runs micropython, which has a library for I2C communication. This was used to communicate with the battery fuel gauge

The below code initialized I2C, and instructs all devices on the line to return their addresses. 85 corrsponds to the BQ34Z110

```python
from machine import I2C
i2c = I2C(0)
i2c.scan()
```

You could then communicate using the below code, where the contents of the array in `bytearray()` were the command to be sent. The list of commands you can use is in the [BQ34Z110 data sheet](https://www.ti.com/lit/ds/symlink/bq34z110.pdf?ts=1685152355290&ref_url=https%253A%252F%252Fwww.ti.com%252Fproduct%252FBQ34Z110). `0x6e` is the "manufacturer name" command. On reading, the returned bytes would start with "Texas Inst.". In the `readfrom()` function, the second parameter is the number of bytes to be read from the I2C line.

```python
i2c.writeto(85, bytearray([0x6e])
i2c.readfrom(85, 64)
```

## Why it didn't work

We would need to configure the BQ34Z110 for our particular purpose by programming the flash memory. [This](https://www.ti.com/lit/an/slua790/slua790.pdf?ts=1683050503158&ref_url=http%253A%252F%252Fti.com%252Fproduct%252FBQ34110) document reviewed in issue #70 said to use software provided by Texas Instruments. We tried to chase down the particular software, as detailed in issue #71. We first tried BQSTUDIO, which was found to not support the BQ34Z110. We then found support software on the TI page for the BQ34Z110. However, this required hardware - a [BQ34Z110EVM](https://www.digikey.co.nz/en/products/detail/texas-instruments/BQ34Z110EVM/4090776) evaluation module to be used, as the BQ34Z110 is an old chip this EVM board is no longer manufactured.

## How it could be made to work

After looking through data sheets and comparing the information to what we had found in the texas instruments forum, this shows that the BQ34Z110 is outdated, and therefore any software that we tried to use was not compatible with it. We recommend using a more up to date fuel gauge for this project. An example of one would be the BQ34Z100-R2, this is a newer chip that is compatable with the BQSTUDIO software.

---
