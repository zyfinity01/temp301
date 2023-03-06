# SDI-12 Configuration in HyQuest Data loggers

Screenshots to detail the process we would follow to achieve the outcomes we want with our current equipment.

We would power-up the SDI-12 sensor using the Digital Output (Relay supplying 12v) on a schedule. In the example below we’re assuming the sensor takes 20 secs to power up ready to take a measurement and we want the measurement taken on the prime 15 minute (0,15,30,45 mins).

HyQuest equipment only allow schedules to start and finish to a resolution of a minute so we would power up the sensor at 14 minutes ready for the 15 minute logged value.  We’d prefer to set schedules to the second resolution if possible?

The Sensor will be powered up for 120 secs and the process will be repeated every 15 minutes.

![](figures/figure_1.png)

We set up the SDI-12 Device.

In this example it is a Shaft Encoder with address ‘zero’ and we’ve chosen to use the ‘M’ command for measurement.  Other options are ‘MC’ for measurement with checksum, ‘C’ for concurrent and ‘CC’ for concurrent with checksum (I think)

We’ve set the sensor up to send the measurement command to the SDI-12 device at 14mins 50 secs past the hour and then at an interval of 15 minutes onwards.  That gives the logger 10 secs to retrieve the measurement from the sensor before the data is ‘logged’ at the prime 15 minute interval.

There’s something going on behind-the-scenes at this point.  If we we’re sending the commands manually via a terminal program we’d have typed 0M!, to which the SDI-12 device will have replied with a string along the lines of 002.  The first zero is the SDI-12 device’s address followed by the number of seconds it will take the sensor to have a value ready for retrieval, in this case 2 seconds.

After waiting 2 seconds a zero would appear on the Terminal screen indicating the measurement has been taken. We’d then issue the ‘give me your data command’ 0D0! Would return the last reading from sensor address zero.  The device would then return the data string.

We don’t see any of that going on in the set-up page, so all that timing and back-and-forth must be programmed into the device.

**Note: The data strings retrieved from the device are saved to a temporary storage location in the logger.**

![](figures/figure_2.png)

Next we set up the individual ‘sensors’ – basically the recorded variables / parameters from the different SDI-12 sensors attached to the device.

This example is Water level which is derived from SDI-12 sensor address ‘0’ which is aliased as ‘HS Shaft Encoder’ in the previous set-up screen. That isn’t really necessary for our device we could easily just use the address number.

Then we tell the device which variable we want to record from the returned data string from the sensor.  In this case water level is the first variable in the string.

We tell the logger that we want to apply a multiplier of 1000 (converting meters to millimetres) and an offset of zero to the returned value. **Note: Multiplier is always applied before offset in our calculations.**

![](figures/figure_3.png)

Then we tell the logger how often we want the values to be recorded to the data logger’s permanent storage.  In this case every 15 minutes.

On the prime 15 minute mark, the data logger accesses the store string in the temporary storage location, extracts variable 1 applies the multiplier and offset calculations and stores the time-stamped value in it’s permanent memory.

**Note 1:** We **REALLY** like recording data on the prime minute (no seconds) with SDI-12 sensors. I guess it’s just ‘tidy’ so that values from different sensors / sites can be compared easily in data management suites, and for environmental monitoring a few seconds either way from the exact time isn’t all that important. It’s up to us to get the timing of sensor data retrieval as close to that prime point as possible.

That said if rounding to the minute is an issue on the device we could just accept that we’re having second values recorded and ‘knock’ them off in the data management on the server?

**Note 2:** We **REALLY** like recording rainfall data to the nearest second as the pulse is recorded on the device. This helps with sub-minute rainfall intensity analysis.

![](figures/figure_4.png)

---
