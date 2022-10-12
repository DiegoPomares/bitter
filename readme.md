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

- IntelliSense [setup](https://lemariva.com/blog/2019/08/micropython-vsc-ide-intellisense)
- The `MarkupSafe` dev dependency is pinned to version `2.0.1` as `micropy-cli` wouldn't work otherwise.
