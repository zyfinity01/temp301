# Transient Protection Docs

## Subheading

Added transient protection circuit from  SDI-12 Protocol docs https://www.sdi-12.org/current_specification/SDI-12_version-1_4-Jan-30-2021.pdf
Included the circuit reguarding "sensor or data recorder interface with transient protection", created the spark gap symbol in KiCad and saved to the repo schemcatic library. All value of components taken
from the given example schematic.

Th arrangment of the transient protection on the PB will be difficult as the protection needs to be between the CMOS 3-State Buufer and the SDI-12 data line, potentially requiring a rearrange of the pcb itself.

---
