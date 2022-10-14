import api
import gpio
import wifi

from config import read_config


def main() -> None:
    wifi_config = read_config("/config/wifi.secret.json")
    wifi.setup_wifi(wifi_config)

    pin_aliases = read_config("/config/pin_aliases.json")
    gpio.setup(pin_aliases)

    api.start()
