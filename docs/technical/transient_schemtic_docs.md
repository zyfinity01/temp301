# Transient Protection Docs

## Explanation

Added transient protection circuit from SDI-12 Protocol [docs]( https://www.sdi-12.org/current_specification/SDI-12_version-1_4-Jan-30-2021.pdf).
Included the circuit regarding "sensor or data recorder interface with transient protection", created the spark gap symbol in KiCad and saved it to the repo schematic library. All values of components are taken from the given example schematic.
The arrangement of the transient protection on the PCB will be difficult as the protection needs to be between the CMOS 3-State Buufer and the SDI-12 data line, potentially requiring a rearrangement of the PCB itself.

For any more information, refer to the docs linked above.

---
