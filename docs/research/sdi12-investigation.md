# SDI-12 Investigation

A writeup of all of our research on the sdi-12 system on the data recorder as part of our evaluation

## Script for querying addresses of devices on line

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

Once that function has been defined in the repl loop, can run address query command

```python
from drivers import sdi12
sdi=sdi12.init_sdi()
sdi12.turn_on_sensors(sdi)
r=send_cmd(sdi, "?!")
```

r will contain the returned addresses in the second return value

---
