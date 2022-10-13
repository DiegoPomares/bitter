# Fermax PLUS

This is a simple MicroPython application for an esp8622 board. It sends a pulse on a GPIO pin when a request is received.

It's meant to be interfaced with the button that opens the door in Fermax intercoms.

## Setup

Requires Python 3.9.*

```bash
# Optional: Setup Python version with pyenv
pyenv local 3.9.*

# Optional: Configure MicroPython stubs for VSCode
make vscode

# Flash MicroPython into the esp board, just needed once
make flash-board

# Bundle application and push it to the esp board
make all

# Open rshell
make rshell

# Open a Python interpreter in the esp board
make repl
```

By default all the tools use `/dev/ttyUSB0` to connect to the esp board with a serial console. To use a different device set the `ESP_DEVICE` environment variable.

## Notes

- IntelliSense setup [instructions](https://lemariva.com/blog/2019/08/micropython-vsc-ide-intellisense)
- The `MarkupSafe` dev dependency is pinned to version `2.0.1` as `micropy-cli` wouldn't work otherwise
- The [microdot](https://github.com/miguelgrinberg/microdot) framework was cross-compiled into an .mpy module using `mpy-cross`, otherwise the esp8266 would run out of memory when compiling it itself
- The `mpy-cross` version has to match the MicroPython firmware version, so the tool has to be compiled from a tag instead of the master branch
- Tips on how to work around memory [constrains](http://hinch.me.uk/html/reference/constrained.html)
- Additional [resources](https://github.com/peterhinch/micropython-samples/blob/master/README.md)
