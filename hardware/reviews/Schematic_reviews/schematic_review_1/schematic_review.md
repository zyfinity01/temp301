# Schematic review 1

This looks good, current roughly: Ireverse = (Vbat – Vdiode – Vled) / 3300 ohm = (14V – 0.2V – 2V) / 3300 = 3.5mA. Power dissipation of the resistor is therefore well below the rating, but the LED is tested at 25mA so it’ll be pretty weak. Not a huge issue.

Do we want to add overvoltage protection here too? For small spikes, take a look at TVS diodes. There are also ICs that do both overcurrent and overvoltage protection.

![](figures/figure_1.png)

Response: Not looking to improve the system robustness at this stage, may be in the future generation.

Part number and description don’t match. This is a 1/8W 1% resistor. Didn’t check all parts, but a good idea to go through and check each description just to be sure they match the part number.

![](figures/figure_2.png)

Response: I checked all parts (resistors and caps) in yageo serch engine. <https://www.yageo.com/en/Product/Search?target=target_title>

This MOSFET is only rated to 1.5A, it’s pretty small. The system shouldn’t draw that much all the time, but it may do when transmitting from the modem as the peak looks to be 2.4A. It’s best to play is safe and go larger with this one, larger MOSFETs are cheap.

![](figures/figure_3.png)

Response: Change to FDN360P which allows Imax = 2A

The switching regulator TPS562201DDCR you’ve chosen has an input voltage rating of 17V. Do we know how high the lead acid battery gets at full charge? I’d suspect it comes very close to that limit, any surge will likely fry the regulator. The peak modem current is also 2.4A, exceeding the rating. Here’s a Digikey search with some filters:

<https://www.digikey.co.nz/short/mbfvnfzh>

Response: The peak current has decreased due to the modem now use only 0.5A at peak, so no exceeding 2A limit. Lead acid battery do not exceeding 17V unless operating under -20°C. This IC is used in many project powered by car battery so I don’t see there is a problem.

Put a 100nF on the input also, 10uF won’t filter out high freq noise, it’s only used for bulk capacitance. Helps with stability.
I’d consider increasing the size of the bootstrap capacitor (package size and voltage rating). On a switch mode this will see some large switching voltages due to the inductor. Better to jump up to a 0805 25V.

![](figures/figure_4.png)

Response: Added another 100nF cap (0.1uF). Change bootstrap capacitor to higher voltage rating (0805)

This inductor has no stock in most places: <https://octopart.com/search?q=RLB0912-3R3ML-ND&currency=USD&specs=0> I haven’t checked all your parts but a good idea to do this too. Generate a BoM and take a look, I’d recommend trying to use same brands for parts if you can for passives e.g. yageo/murata for caps and resistors.

I’d also recommend surface mount, in production having TH components is hard to manufacture. The datasheet recommends typical 4.7uH not 3.3uH.

![](figures/figure_5.png)

Response: Change to SRN5040-4R7M IND 4.7uH 35mOhm 3.3A surface mount

Is there a reason you went for a LDO for the 3.7V regulator? At the peak modem transmit current we have: P = (5V – 3.7V) * 2.4A = 3.12W. That is a huge amount of power dissipation, the case will get very hot. I’d go switch mode here unless you had a reason for choosing LDO specifically?

![](figures/figure_6.png)

Response: New modem uses 3.3V. So, the 3.8V regulator has removed. To replace that, a 5V to 3.3V switch regulator is added.

Assuming this is a place holder, but when you do select an LED remember to use the formula for the resistor: R = (3.3V – Vf) / Iled

![](figures/figure_7.png)

This looks like it’s missing a 3V3 net. Also add a bypass/decoupling. Datasheet recommends a 22uF and a 100nF. This looks like it’s a wifi/Bluetooth module, what is the reason for using this module instead of a stand alone microcontroller?

![](figures/figure_8.png)

Response: bypass/decoupling caps added.

![](figures/figure_9.png)

How are you planning on programming the microcontroller? I’m not sure if I’m missing something, but this is what the datasheet recommends. Says it’s JTAG, looks a little weird compared with the second pic which is a standard 10-pin JTAG.

![](figures/figure_10.png)![](figures/figure_11.png)

Response: JTAG interface added.

![](figures/figure_12.png)

Response: A USB interface can also be used for programming

LDO input capacitors, I’d suggest a 10uF and a 100nF. The output cap is massive, is there a reason for this?

![](figures/figure_13.png)

Response: Linear regulator has been removed.

UART series resistors, probably include some (\< 100ohm). Useful to protect the bus and for prototyping.

![](figures/figure_14.png)

Response: Resistor added

![](figures/figure_15.png)

I’m not sure I understand from the naming what this circuit is used for, can you explain it for me?

![](figures/figure_16.png)

Response: Normally you need to push the boot button when you program the ESP32. This circuit can generate a signal to IO0 automaticly so you don’t need to push the button to upload the program. This circuit is used on most of the ESP32Devkit.

<https://dl.espressif.com/dl/schematics/ESP32-Core-Board-V2_sch.pdf>

I assume this is just unfinished, but the net doesn’t connect to anything I can see and the caps need values.

![](figures/figure_17.png)

Response: This modem is no longer used

This SD card holder doesn’t appear to be sold anywhere. I’d choose a more common part.

![](figures/figure_18.png)

Response: The actural component can be selected later.

Again I assume this is just not finished, but need to chose an RGB LED and resistor values. Personally I’d chose

![](figures/figure_19.png)

Response: I am considering using a surface mount RGB LED module. Like NeoPixel.

Add some decoupling 100nF caps here.

![](figures/figure_20.png)

Response: Decoupling caps added.

What values are these resistors. I assume the pull-down is to ensure the mosfet is off when the gate isn’t driven?

![](figures/figure_21.png)

Response: This resistor value should be 1M ohm.

This buffer chip absolute max rating is 6.5V on any input. My understand was that SDI-12 is 12V logic-high? Might need to find a higher voltage buffer. I’d also add a 0 ohm resistor in series with the output, in case you need a small resistance to stop the MOSFET switching too fast creating ringing. What is the point of the ForceLO net other than preventing TX from transmitting?

![](figures/figure_22.png)

![](figures/figure_23.png)

Response: The SDI-12 logic operates from -0.5V to 5.5V. I don’t think it is a problem.

Last point is I’d recommend generating a BoM when you have selected your parts, and have a look for them online to gauge stock availability. Make sure no parts are in last-time buy or obsolete status too.

Response: BOM is in the folder

![](figures/figure_24.png)

---
