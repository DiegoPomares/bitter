import uasyncio

import network
from machine import Pin

from vendor.microdot_asyncio import Microdot, Request

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


async def send_pulse() -> None:
    pin = Pin(CONFIG["output_pin"])
    pin.on()
    await uasyncio.sleep(CONFIG["pulse_duration"])
    pin.off()


@app.post("/pulse")
async def index(request:Request):
    await send_pulse()
