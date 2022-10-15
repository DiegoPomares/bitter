import config
import gpio
import routes
import wifi

from vendor.microdot_asyncio import Microdot


def main() -> None:
    wifi_config = config.read_config("/config/wifi.secret.json")
    wifi.setup(wifi_config)

    pin_aliases = config.read_config("/config/pin_aliases.json")
    gpio.setup(pin_aliases)

    app = Microdot()
    routes.setup(app)
    app.run(port=80, debug=True)

