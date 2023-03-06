# Schematic Review 3

## Water Sensor Hub

Put some 100nF caps in here, datasheet doesn’t call for it but they help with filtering the switching noise of the power supply from the output and input.

![](figures/figure_1.png)

Response: Cap added

Can you check the stock for this, or chose a part (or a part that has a generic footprint). My experience is that they often don’t have generic footprints for SD card holders, so it needs to be chosen before PCB layout.

![](figures/figure_2.png)

Response: Using MEM2075-00-140-01-A from kicad

[Datasheet](https://www.digikey.com/en/products/detail/gct/MEM2075-00-140-01-A/9859614)

[Footprint](https://www.snapeda.com/parts/MEM2075-00-140-01-A/Global%20Connector%20Technology/view-part/?ref=digikey)

## Battery Schematics

Some stuff that can be DNP i.e. we’ll put it on the PCB but don’t place the component when you assemble it.

Do-not-place (DNP) these ones, probably don’t need them:

![](figures/figure_3.png)

I can’t find where the SDA/SCL signals are connected to the microcontroller. I2C lines also need pull-ups, use 10K to minimize power draw and lower them if the signals rise-time is too long (makes the square waves look very rounded).

![](figures/figure_4.png)

Response:

- SCL: USB_D-
- SDA: USB_D+

![](figures/figure_5.png)

Response: Pull up resister added

Not sure if you found something to say ground these, if so ignore, but it isn’t recommended to ground / connect to VCC anything that doesn’t explicitly tell you to do so in the datasheet. I would leave it floating.

![](figures/figure_6.png)

Response: Leave unconnected

For the current sense resistor, you need to determine what the total (approximate) current draw of the system will be. The just use Ohms law to chose a resistor
   V=IR => 125mV/Itotal = Rsense

   You don’t plan on drawing more than 1.25A so I’d say you could go for ~ 0.1 ohm/0.25W  resistor. This is assuming the battery won’t be charged while plugged in, and is only connected when powering the system. If that isn’t the case, the current you use will instead be the charging current with some safety factor.

![](figures/figure_7.png)

Response: Add 0.1ohm resistor

I noticed these caps (I haven’t checked others but you should) appear to be 0201. That’s pretty small, fine for boards you’re getting PCBA’d and close to finished but horrible for prototypes. I would go 0402 or larger, as 0201 is very hard to solder by hand.

![](figures/figure_8.png)

Response: Change all 0201 to 0603 or bigger.

---
