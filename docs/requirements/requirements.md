# Requirements

## Device Requirements

- Low powered
- Accurate timekeeping
  - Synced with time server
  - Timestamped to NZST (UTC+12)
  - Timestamp to nearest second
- Connected to 12V battery (lead acid, gel, AGM SLA)
  - Battery connected by screw/push terminal
  - Device should retain settings when powered down
  - Possibility of connecting solar panel or 12V AC adapter, so device should be capable of handling any voltage fluctuations
  - Overvoltage and reverse polarity protection
  - Lifetime of 3-6 months
- Wireless comms to mobile device for configuring
  - Bluetooth or WiFi
  - Activated by switch
- USB port for programming device (and maybe diagnostics)
- Wireless data transmission via Vodafone NB-IoT
  - Band 28
  - External antenna connection (SMA)
  - Data transfer protocol to ensure no data loss
- Appropriate size for fitting in raingauge or a galvanised pipe
- Consider ability to add Glyn pulse coherent radar
- Nice to have offline mode where device is out of range of NB-IoT
  - Removable modems to reduce cost of offline devices
  - Physical or in-app switch to toggle modem on/off.
  - Needs to have accurate timekeeping
- Data saved to device on SD card
  - Readings for each unique parameter will have an ID
  - Should contain ID, timestamp, reading
  - Needs accurate timekeeping
  - Need to be able to measure used/free space
- Cost between $200-$300 per device

### SDI-12

- Use SDI-12 communications protocol
- Relay to power up SDI-12 sensor
- User can schedule sensor readings manually
  - Device needs to automatically schedule readings to account for the time to start the sensor and take the reading

### Raingauge

- Ability to monitor 1 (preferably 2) inputs from reed switch triggering
  - With switch debounce
- Up to 1 reading per second
  - Timestamp to nearest second
- Send data every 5 minutes during rain, reduce to hourly (or 6-hourly) transmission when not raining

## Cloud Requirements

- Hosted on a virtual server
- Flexible data storage format to allow future integration with GWRC databases
- Explore possibility of enabling data transfer to FTP server using existing supplier's XML format
- View data in tabular and graph format
  - Identify missing data
  - Identify comms failure
- Send email/SMS for specific data
  - send for missing data, comms failure, system issues
- Daily transmission of SD card capacity

## App Requirements

### Configuration (App -> Device)

- Sensor Settings
  - Recording interval
  - Calibration multiplier (span)
  - Calibration offset (zero)
- Data transmission interval
- Physical location (use phone GPS) - optional
- Device ID and Name
- ability to put the device into "test mode" - temporarily disabling sending data to the cloud backend while calibrating the sensors
- send test message to cloud button
- Synchronise clock to cellphone clock. Useful for sites out of range of NB-IoT
- Set the SDI-12 sensor address on the app and specify ID of the variable being recorded - have a text name and the ability to specify units for measurement variables
- Some SDI-12 sensors take some time to boot up, so allow this time to be configured
- Assign units - mm/h for example

### Visualisation (Device -> App)

- No need to display graphs on the app, but do want live values
- Downloading device data from a specified interval
- number of sent/failed transmissions
- "Download all data" button
- most recent transmission
- most recent reading (for calibration)
- Device battery level
- Network reception level - Signal strength test (in -dBm) - only update this reading on request, no need to constantly poll
- Rainfall totals - because they visit every 2-3 months, they want to calibrate the total recorded rainfall against a level in a collection tank for QA purposes
- Used/free space on SD card

---
