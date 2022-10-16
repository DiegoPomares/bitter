import config
import gpio
import routes
import wifi

from vendor.microdot_asyncio import Microdot


def main() -> None:
    wifi_config = config.read_config("/config/wifi.secret.json")
    wifi.setup(wifi_config)

    pin_names = config.read_config("/config/pin_names.json")
    gpio_config = config.read_config("/config/gpio_config.json")
    gpio.setup(pin_names["gpio"], gpio_config)

    app = Microdot()
    routes.setup(app)
    app.run(port=80, debug=True)

