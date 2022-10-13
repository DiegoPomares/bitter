import time

import network
from machine import Pin

from vendor.microdot import Microdot, Request

from config import CONFIG
from secrets import SECRETS


app = Microdot()


def main() -> None:
    setup_wifi()
    setup_io()
    app.run(port=80, debug=True)


def setup_io() -> None:
    Pin(CONFIG["output_pin"], Pin.OUT)


def setup_wifi() -> None:
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(SECRETS["ssid"], SECRETS["key"])


def send_pulse() -> None:
    pin = Pin(CONFIG["output_pin"])
    pin.on()
    time.sleep(CONFIG["pulse_duration"])
    pin.off()


@app.post("/pulse")
def index(request:Request):
    send_pulse()
