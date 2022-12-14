# Bitter

Bitter is a MicroPython application that provides an HTTP API to control GPIO ports remotely.

## Requirements

- **WeMos D1 Mini board:** the application works with other esp8266 boards but the pins are labeled for this one by default:

![Board pinout](doc/wemosd1.webp)

- **Docker:** Everything is compiled and executed using Docker containers for consistency, and to avoid cluttering the system (see [installation instructions](https://docs.docker.com/get-docker/)).

## Quickstart

### TL;DR

```bash
BOARD_SERIAL_DEVICE=/dev/... make all show-ip
curl "http://<BOARD IP ADDRESS>/gpio/led"
```

### Step by step

```bash
## 1. Connect the esp board and find the serial device associated to it, the
## default is /dev/ttyUSB0 but if it's not specify the correct one
# export BOARD_SERIAL_DEVICE=/dev/...

## 2. Configure wifi credentials
make setup-wifi

## 3. Build the MicroPython firmware and flash it to the board
make flash

## 4. Push the application code, it will be written to the board's filesystem
make push

## 5. Restart the board
make restart

## 6. Show the IP address
make show-ip

## 7. Test the API
# Get onboard led status
curl "http://<BOARD IP ADDRESS>/gpio/led"
# Turn on the onboard led
curl -X POST -H "Content-Type: application/json" -d '{"cmd": "on"}' "http://<BOARD IP ADDRESS>/gpio/led"
# Make the led blink
curl -X POST -H "Content-Type: application/json" -d '{"cmd": "modulate", "times": 10, "script": ["on", "delay 100", "off", "delay 100"]}' "http://<BOARD IP ADDRESS>/gpio/led"
```

### HTTP API spec

All payloads are sent in json format (use the `Content-Type: application/json` header).

#### GET /gpio/<pin_id_or_alias>

Get the current state of the gpio pin.

#### POST /gpio/<pin_id_or_alias>

Payloads:

```yaml
## Turn a pin on/off
{
  "cmd": "on" | "off",
}

## Execute a set of actions in the given gpio pin
{
  "cmd": "modulate",

  # [Optional] Number of times the script will be repeated (default: 1)
  # If times is <=0 the script will be repeated indefinitely
  "times": INT,

  # The list of actions to execute, must be one of:
  # "on": turn the pin on
  # "off": turn the pin off
  # "delay INT": wait for INT millisecs before the next action
  "script": [COMMAND, ...]
}
```

## Development

### Dev requirements

- Python 3.9: The version implemented by MicroPython.
- [Poetry](https://python-poetry.org/docs/#installation): dependency management tool.
- curl: Or the HTTP client of your choice.

Setup the dev environment with `poetry install`, this will create a virtualenv with all necessary dependencies installed. Make sure to point your IDE to this virtualenv to make use of the MicroPython stubs.

See [pyenv](https://github.com/pyenv/pyenv) if you need a Python version management tool.

### Tools

```bash
# See available commands
make

# Open rshell, useful to check the board's filesystem under /pyboard
make rshell

# Open a Python interpreter in the board
make repl

# Push code changes to the board, it uses rshell's rsync to modify only
# the files that need an update
make push

# Attach to the Python interpreter and start the application, useful to see logs
make attach

# Run this after making changes to deploy, run, and see the logs, useful for debugging
make push reset attach
```

### Project structure

The project has a very simple structure:

- **`etc/`**: This directory contains the application configuration in json files, it's copied as-is into the root directory of the board.
- **`skel/`**: Scaffold used to launch the application automatically when the board boots up and to setup low level base board configuration. The contents of this directory are copied as-is into the root directory of the board.
- **`frozen/`**: The modules that are compiled into the MicroPython firmware (see [Notes](#notes) for more info).
- **`src/`**: The application source code, the contents of this directory copied into `/app` in the board with rsync.
- **`docker/`**: The files for building the Docker image used to interact with the board via serial device.

## Notes

- Memory [constrains](http://hinch.me.uk/html/reference/constrained.html) and how to work around them.
  - It is necessary to freeze some of the modules, in other words compiling them together with the firmware, because otherwise the board runs out of memory quite easily. When a `.py` module is imported it is compiled into bytecode in the board, and then the bytecode remains in the RAM, so it is a huge waste of memory.
  - The `mpy-cross` tool can be used to pre-compile modules into bytecode before pushing them to the board (the `.mpy` files). They are still loaded into the RAM at runtime, but at least the board doesn't have to compile them which avoids out-of-memory errors.
  - Compiling **everything** into the firmware maximizes the available RAM and it's the most optimal approach, but slows down the development as it takes longer than just copying the files.
- If you disable [UART0](https://docs.micropython.org/en/latest/esp8266/quickref.html#uart-serial-bus) you won't be able to connect to the board with the USB interface, you'll have to flash the firmware again do to so
- Link to Python standard library [ports](https://github.com/micropython/micropython-lib/tree/master/python-stdlib) that are not included in MicroPython by default.
- Link to MicroPython [compilation instructions](https://github.com/micropython/micropython/tree/master/ports/esp8266#build-instructions) for the esp8266 board.
  - Modules that are to be frozen have to be placed into the [modules](https://github.com/micropython/micropython/tree/master/ports/esp8266/modules) directory, I didn't really find this anywhere in the docs but only looking at forums.
- Link to additional [resources](https://github.com/peterhinch/micropython-samples/blob/master/README.md).
