# SDI12 Evaluation

All standards and protocols are taken from [SDI12 Documentation](https://www.sdi-12.org/current_specification/SDI-12_version-1_4-Jan-30-2021.pdf)

## Electrical Interface

The SDI-12 electrical interface requires 3 main lines:

- Serial Data Line: To read and write data to and from sensors and the data recorder.
- The Ground Line
- The 12V Voltage Line

The data recorder has these 3 lines implemented as a header on the PCB labeled as SDI_Pow for the 12V line, SDI12 for the data line and GND for the ground line.

### Serial Data Line

The serial data line is required to be bidirectional and three-state. During the investigation of the reading and writing capabilities of the SDI12 line, we were able to write to any sensor along the data line asking for their address and we could then read each address of each sensor. This confirmed the bidirectional functionality of the data line. The three-state functionality was already implemented with the 3-stage CMOS buffer in hardware/schematics/sdi-12.kicad_sch. The 3-stage CMOS buffer allows the data recorder, in the first stage, to receive data, in the second stage, amplify the signal and read it and finally in the third stage write back to the sensors. We can therefore conclude the current serial data line is SDI12 compliant.

#### Voltage Transitions

We did not test the data line voltage slew rate, to be compliant it must not be greater than 1.5V per microsecond.

#### Impedance

During our testing, we saw no reason why the sensors on the SDI12 bus would ever need to be turned off. By doing this, we assume that if the sensor wants to be turned off it is fully removed and, if the sensor is connected to the data line, it is on and transmitting. To meet SDI12 impedance protocols, the variable transistor between the data line and the 3-stage CMOS buffer must be between 500 and 1500 ohms when the transmitter is on. With the added transient protection during our testing, found in hardware/schematics/sdi-12-transient-protection_.kicad_sch, the additional resistor is 510 ohms between the 3-stage CMOS buffer and the serial data line. As we are assuming the sensors are always on and transmitting, this falls within the 500-1500 ohm range and, therefore, makes the data recorder SDI12 compliant for impedance.

### Ground Line

The ground line must be connected to both circuit ground and earth ground at the data recorder. As we were not deploying the device for any testing this was confirmed as outside of the scope of this project.

#### Transient Protection

The suggested transient protection circuit in Appendix A of the docs was added to hardware/schematics/sdi-12-transient-protection_.kicad_sch. The addition involved the breaking of the connection between the 3-stage CMOS buffer and the output header on the PCB, the transient protection is placed inbetween these connections. Additional circuitry was added to the schematics and any parts that were not in the symbol library were created and added to the library. The additional circuitry is compliant with SDI12 protocols and makes the data recorder compliant with SDI12 transient protection.

### 12-Volt Line

The 12V voltage line is required to provide between 9.6 and 16 volts, with respect to ground, at all times. The voltage supply does not have to be supplied by the data recorder itself and can be supplied by an external power supply. In our testing, we found that with multiple sensors connected along the 12V line, 12V was still being supplied to each sensor. Therefore, we can assume we can use the data recorder as our 12V supply and an external power supply is not necessary. While measuring the voltage in each configuration of the data recorder we noticed the 12V would dip just after initialization. An edit to the code was made to amend this and the 12V line now outputs 12V at all times regardless of the state of the data recorder. We did not test the maximum sensor load. We can conclude the 12V Voltage Line is compliant with the tested SDI12 protocols.

### Connectors

There is no specified connector for SDI12 compliance, the current header we are using on the PCB allows for easy switching of sensors connected to the heading and is easy to extend to allow multiple sensor connections.

## Communications Protocol
