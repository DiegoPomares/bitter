# Fermax PLUS

## Board setup

Download MicroPython [firmware](https://micropython.org/download/esp8266/) and flash with:

```bash
SERIAL_DEVICE="/dev/ttyUSB0"
FIRMWARE="esp8266-20220618-v1.19.1.bin"

# Wipe flash memory
esptool.py --port "$SERIAL_DEVICE" erase_flash
esptool.py --port "$SERIAL_DEVICE" --baud 460800 write_flash --flash_size=detect 0 "$FIRMWARE"
```

## Notes

- IntelliSense setup [instructions](https://lemariva.com/blog/2019/08/micropython-vsc-ide-intellisense).
- The `MarkupSafe` dev dependency is pinned to version `2.0.1` as `micropy-cli` wouldn't work otherwise.
- The [microdot](https://github.com/miguelgrinberg/microdot) framework was cross-compiled into an .mpy module using `mpy-cross`, otherwise the esp8266 would run out of memory when compiling it itself.
- The `mpy-cross` version has to match the MicroPython firmware version, so in this project the tool was compiled from a tag instead of the master branch.
- Tips on how to work around memory [constrains](http://hinch.me.uk/html/reference/constrained.html)
- Additional [reference](https://github.com/peterhinch/micropython-samples/blob/master/README.md)
