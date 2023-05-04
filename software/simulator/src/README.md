# Simulators

This directory contains two scripts:

- `device.py` - A device simulator, used for generating random data for testing the cloud components of this project
- `webserver.py` - A [flask](https://flask.palletsprojects.com/en/2.1.x/)-based script intended to be an API-compatible simulator for the device web-backend. It's used to test the web-app frontend.

Note: Ensure you have your virtual environment initialised and dependendencies from the top-level `requirements.txt` installed.

## Device Simulator

<!-- Refer to #548 -->

### Device Simulator Setup and Execution

1. Copy `device.example.conf` to `device.conf` and edit the defaults (if required)
1. run `python simulator.py [--help]`

### Configuration

| config option | default | description                                                                          |
|---------------|---------|--------------------------------------------------------------------------------------|
| port          | 1883    | broker port                                                                          |
| wait-time     | 3       | number of seconds to wait between attempting to send each message                    |
| device-type   | sdi-12  | type of device (can either be `sdi-12` or `rainfall`                                 |
| verbose       | False   | verbose logging                                                                      |
| format        | json    | Message format (json or csv)                                                         |

## Webserver Simulator

No setup is required to run the `webserver.py` script. Note, however, that paths to the webapp and configuration files are hard-coded into the script.

The simulator can be run from the command line, while at the repository top-level, by executing the command `python software/simulator/src/webserver.py` which will produce the following output (example):

```shell
$ python software/simulator/src/webserver.py
 * Loading JSON from software/device/embedded/src/services/config.example.json
 * Loading JSON from software/device/embedded/src/services/data.example.json
 * Serving Flask app 'webserver' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
 * Restarting with stat
 * Loading JSON from software/device/embedded/src/services/config.example.json
 * Loading JSON from software/device/embedded/src/services/data.example.json
 * Debugger is active!
 * Debugger PIN: xxx-yyy-zzz
```

As indicated in the Flask output, the webapp can be viewed by visiting <http://127.0.0.1:5000> in a web browser. Web server activity will be logged to the terminal (example):

```shell
127.0.0.1 - - [10/Oct/2022 15:07:14] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [10/Oct/2022 15:07:15] "GET /bundle.b5e19.css HTTP/1.1" 200 -
127.0.0.1 - - [10/Oct/2022 15:07:15] "GET /bundle.2dea9.esm.js HTTP/1.1" 200 -
127.0.0.1 - - [10/Oct/2022 15:07:15] "GET /data HTTP/1.1" 200 -
127.0.0.1 - - [10/Oct/2022 15:07:15] "GET /config HTTP/1.1" 200 -
127.0.0.1 - - [10/Oct/2022 15:07:15] "GET /favicon.ico HTTP/1.1" 200 -
127.0.0.1 - - [10/Oct/2022 15:07:15] "GET /assets/icons/apple-touch-icon.png HTTP/1.1" 200 -
```

The `webserver.py` simulator may be exited by pressing `Ctrl-C`.

---
