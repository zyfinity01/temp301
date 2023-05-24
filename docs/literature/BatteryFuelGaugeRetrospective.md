# Battery Fuel Gauge Retrospective and Lessons Learnt

## Research we did - summary of datasheets

Backgound investigation was completed and compiled into a LaTeX doucment found in issue #15. By looking through the datasheet for the BQ34Z110, it was realised that the flash memory on the chip would need to be configured for our particular application to work. I2C communication with the chip would need to be implemented for communication between the onboard ESP-32 microprocessor and the BQ34Z110, there was plenty of examples of how this communication could be achieved.

## Why it didn't work

We would need to configure the BQ34Z110 for our particular purpose by programming the flash memory. [This](https://www.ti.com/lit/an/slua790/slua790.pdf?ts=1683050503158&ref_url=http%253A%252F%252Fti.com%252Fproduct%252FBQ34110) document reviewed in issue #70 said to use software provided by Texas Instruments. We tried to chase down the particular software, as detailed in issue #71. We first tried BQSTUDIO, which was found to not support the BQ34Z110. We then found support software on the TI page for the BQ34Z110. However, this needed hardware - a [BQ34Z110EVM](https://www.ti.com/lit/ug/sluua15/sluua15.pdf?ts=1684892790315&ref_url=https%253A%252F%252Fwww.google.com%252F) evaluation module to be used. This cost around 400USD, which was well outside our budget. Therefore we couldn't continue with our evaluation.

## How it could be made to work

---
