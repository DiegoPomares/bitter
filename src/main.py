import config
import gpio
import routes
import wifi


def main() -> None:
    wifi_config = config.read_config("/etc/wifi.secret.json")
    wifi.setup(wifi_config)

    pin_names = config.read_config("/etc/pin_names.json")
    gpio_config = config.read_config("/etc/gpio_config.json")
    gpio.setup(pin_names["gpio"], gpio_config)


    routes.start()


