# Open Data Recorder for Environmental Monitoring

An open source and open hardware IoT-connected SDI-12-enabled remote data recorder capable of deployment for environmental monitoring by New Zealand Regional Councils.

## Quick Links

- [Project Charter](docs/charter.md)
- [Meetings](https://gitlab.ecs.vuw.ac.nz/engr489-environment-monitoring/engr489-project/issues?scope=all&utf8=%E2%9C%93&state=all&label_name%5B%5D=Meeting)
- [Development Guide](docs/technical/README.md)

## Project Description

Regional Councils maintain large environmental monitoring networks with real-time data recorded by data recorders being reported via telemetry to virtual servers at a data centre.

This project arose from the desire of the Hydrology Team at Greater Wellington Council to explore the benefits that IoT technologies could offer &mdash; low-cost hardware, low power consumption, future-proof communication technologies and the ability of Council staff to extend the capabilities of the data recorder &mdash; whilst maintaining the sensor accuracy required for scientific studies and regulatory functions. In collaboration with staff and students at the School of Engineering and Computer Science at Victoria University of Wellington, a prototype data recorder has been developed to meet the environmental monitoring requirements of they Hydrology Team.

## Project Requirements

Overarching project requirements are listed in [docs/requirements/requirements.md](docs/requirements/requirements.md).

- Revision 3 requirements are listed in [docs/requirements/requirements_for_Rev 3.0](docs/requirements/requirements_for_Rev 3.0).
- Revision 4 requirements are the same as Revision 3.

## Overall Objectives

- Develop a system to enable more cost effective collection of data to serve the Region's environmental data needs.
- Deliver an 'Open-Source' system that is fully documented which will allow GWRC staff to up-skill and understand IoT concepts and provide GWRC IT department the ability to support the server and data transfer components in the future. Hardware construction would need to be well documented to allow future production of devices post-project.
- Enable future development of the system in collaboration with VUW.
- Develop a system that could be offered to other Regional Councils around New Zealand if successful.

The project can be as big or as small as the project team decides. The main thing is to ensure we end up with a robust, accurate system that can be evaluated against our current systems. GWRC will be able to provide test sites locations and VUW project team will be able exposed to the work the council undertakes - Field trip(s)?

GWRC doesn't have any set funding for the project and monetary contributions can be discussed if the project is of interest to VUW. I should imagine GWRC would be able to pay for the virtual server chargers, software licences and hardware but that is to be confirmed with management.

## Repository Directory Structure

### High level overview

```text
Environmental-Monitoring-2020/engr489-project/
├── docs
├── software
    ├── device
        ├── embedded
        └── webapp
    ├── server
    └── simulator
├── hardware
├── util
└── venv
```

### `software`: Embedded Software and Device Simulators

#### `device`: Embedded Software, Web-App Code

```text
device
├── build
├── embedded
└── webapp
```

- `build`: automatically created by the software build script, `build.sh`.
- `embedded`: Micropython device code &mdash; development takes place here.
- `webapp`: preact web app code &mdash; development takes place here.

#### `server`: scripts for communication with remote servers

```text
server/
[no subdirectories]
```

Python scripts for publishing to an MQTT broker and subscribing to topics. Also contains a Python script for publishing to Microsoft Power BI <https://powerbi.microsoft.com/>. Used during exploration of different protocols for transmitting data from the data recorder.

#### `simulator`: Simulation Scripts

```text
simulator/
[no subdirectories]
```

Various scripts for simulating different parts of the project.

### `docs`: Documents and Documentation

```text
docs
├── bom
├── datasheets
├── development
├── literature
├── meetings
├── presentations
├── reports
├── requirements
├── research
└── technical
```

- `bom`: Bill of Materials (BoM) documents sent for PCB manufacture.
- `technical`: technical documentation, including documentation of the tinyweb server implementation which runs on the ESP32 to provide a web interface to the data recorder.
- `literature`: A flat folder containing PDF copies of anything that will or could be cited in the reports: journal articles, tech notes, etc.  There should be a BibTeX .bib bibliography file at the same level as the PDF files, for use with the JabRef open source bibliography and reference manager.
- `meetings`: saved emails from the 2021 Honours project.
- `presentations`: The files used in any presentations, including the ENGR 489 course final presentation.
- `reports`: Contains the ENGR 489 course reports. There are two reports required this year, a Preliminary Report and a Final Report. LaTeX source files. R, Matlab, etc. files, containing only the figures used in the report at this level. One sub-folder "Figures" to keep figures organised.
- `requirements`: documentation provided by the clients for project requirements.
- `research`: Embedded software, Web App, Hardware Design and PCB development notes.

### `hardware`: Data Recorder Hardware

```text
hardware/
├── reviews
└── schematics
```

- `reviews`: documentation of schematics and PCB reviews.
- `schematics`: electronic schematics and PCB designs of the current revision.

### `util`: utility scripts

```text
util/
├── Docker
├── ansible
├── micropython-hitl
├── micropython-software
├── scripts
└── vagrant
```

Build and test scripts, including development and test environment provisioning and configuration scripts, for performing utility functions separate from the software running on the data recorder.

- `Docker`: Dockerfiles to create images used in jobs in the GitLab CI pipeline.
- `ansible`: Ansible playbooks for provisioning development, build and test environments.
- `micropython-hitl`: hardware-in-the-loop (HTL) testing scripts.
- `micropython-software`: Dockerfile for running MicroPython in a Docker container for development and test purposes.
- `scripts`: build and test scripts mostly intended to be run in the CI pipeline.
- `vagrant`: Vagrantfile for testing of provisioning and configuration of HTL build and test servers in a VirtualBox VM.

### `venv`: Python Virtual Environment

Python virtual environment created when the instructions in the _Development Environment_ section of the [Technical Documentation](docs/technical/README.md) are followed.

---
