# SDI-12 Investigation

A writeup of all of our research on the sdi-12 system on the data recorder as part of our evaluation

## Script for querying addresses of devices on the SDI12 line

I ran all this code in the repl loop, so writing it up here. Function to run any sdi-12 command on line. Bootleg version of run_command in sdi-12 driver. This function couldn't be used as you need to specify a sensor address, which the address query does not use

```python
def send_cmd(sdi, cmd)
    sdi12._wake_sensors(sdi)
    sdi["dir_"](0)
    uart = sdi["uart"]
    uart.write(cmd)
    time.sleep_us(8333 * len(cmd))
    sdi["dir_"](1)
    r1 = uart.read()
    time.sleep_ms(1000)
    r2 = uart.read()
    return [r1, r2]
```

Once that function has been defined in the repl loop, can run the address query command

```python
from drivers import sdi12
sdi=sdi12.init_sdi()
sdi12.turn_on_sensors(sdi)
r=send_cmd(sdi, "?!")
```

r will contain the returned addresses in the second return value

## Results of script

We found the Rain Gauge has the address 1, and the Water Level has the address 0. We could get the addresses when both were connected or when each was connected individually.

## 12V Line

We also investigated the behavior of the 12V line. One of the requirements to meet SDI-12 protocols is an uninterrupted 12V supply line to each sensor along the SDI-12 bus. The 12V can be sourced from the data recorder or an external 12V supply but it must be a constant supply. The first attempt at investigating the 12V supply led to us using a multimeter and probes, we noticed the voltage across the SDI-12 12V output and ground was the same as the voltage across the power input to the data recorder and ground. We noticed the voltage was initially only reaching 9V, this was due to a faulty power supply to the data recorder. Once the power supply was amended, there was a match between the 12V power supply to the data recorder and the 12V across the SDI-12 12V line and ground. Now we had a consistent 12V being supplied from the data recorder, the next stage was to observe the voltage level of the SDI-12 12V line during normal function and deep sleep mode. We noticed there was a drop in voltage along the 12V line during initialization, after investigating the code we noticed during the __init__ function each sensor is initialized as asleep by default. Having the sensors asleep by default means the SDI enable line was dragged low, this meant the 12V line was dragged low. Directly after the sensors are initialized the turn_on_sensors() function is run and the SDI enable line is put back to high and reads 12V again. While the SID-12 12V line is only pulled low for a very short period, to be SDI-12 protocol compliant this can never happen. To fix this, the code will be edited so sensors are initialized as awake to keep the enable line high, or separate the awake/sleep status of the sensors to a different field and constantly have the enable line high.

---
