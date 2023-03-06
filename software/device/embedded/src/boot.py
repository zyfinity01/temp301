# This file is executed on every boot (including wake-boot from deepsleep)
# esp.osdebug(None)
# import webrepl
# webrepl.start()

import machine

# Core frequency in Hz
CPU_FREQ = 240_000_000
machine.freq(CPU_FREQ)
