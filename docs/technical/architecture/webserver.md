# Web Server Documentation/REST API

This page documents the web server used in the configuration mode of the application.

## REST API Endpoints

### Device Data

Endpoint for data visualisation.

#### GET `/data`

Returns the device data JSON file. [Response Content](configuration.md#device-data)

### Device Config

#### GET `/config`

Returns the device configuration JSON. [Response Content](configuration.md#device-configuration)

#### POST `/config`

Update device common configuration.
This endpoint accepts any data aside from the sdi-12 sensor specific data defined in the [Configuration schema](configuration.md) (see [below](#sdi-12-sensor-config))

### SDI-12 Sensor Config

Tinyweb doesn't seem to support nested endpoints after a parameter, so things like `/test/<name>/nested` won't work.
As a result, the API isn't completely "restful".

#### POST `/config/sdi12/update/<name>`

Update a specific SDI-12 sensor. `<name>` should not contain spaces.
If `<name>` does not exist, it will create a new SDI-12 sensor.

#### POST `/config/sdi12/rename/<name>`

Rename the SDI-12 sensor. Request body must be json-encoded and contain `"name":"new_name"`

#### POST `/config/sdi12/delete/<name>`

Delete the SDI-12 sensor.

#### GET `/config/sdi12/test/<name>`

Test a specific SDI-12 sensor.
The device must be in `configure` mode (ie, the configuration file must have `configure-mode` enabled).
returns:

```json
{
    "response": "" // the response from the test
    "error"?: "" // optional error response
}
```

### SDI-12 Monitor

Allows raw SDI-12 commands to be sent to the device, and the untransformed output to be interpreted by the user.

#### GET `/monitor?command=!?`

Where the value of `command` is the SDI-12 command to send to the device (such as `?!`)

returns the following response as json:

```json
{
    "response": "", // response string from the command output
    "command": "",  // the command that was sent to the device
    "error"?: ""    // optional: an error string
}
```

query parameters don't seem to be supported by the REST API "resource" class in the tinyweb implementation.

### Time

Allows updating the device time.

#### POST `/time`

force time sync with NTP servers. (not implemented yet)

## Design

Unlike the functionally-programmed "regular-mode", the configure-mode is object oriented, built around the [tinyweb](https://github.com/belyalov/tinyweb/) library.

Each REST API endpoint is represented by a class which implements the HTTP methods as a function.
This class is meant to be stateless, and the functions have a 'callback method' parameter for saving the data.
The function is responsible for checking the incoming data, calling the callback method, and then returning a response to the user.

Some methods can be coroutines, but they must be decorated in a `@staticmethod` so that tinyweb knows what is (see !152).

The webserver itself is wrapped in an outer class called TimedWebServer which implements a watchdog timer, responsible for shutting down the server
if it times out.
This is used to prevent the power-hungry webserver from draining all the device's batteries if the user accidentally leaves the webserver running.
Once it has timed out, the device returns to "regular-mode".

Refer to the Tinyweb documentation for more details.

## Other Notes

sending an empty POST request with the header `Content-Type: 0` will throw a 400 error in the `read_parse_form_data()` method.

---
