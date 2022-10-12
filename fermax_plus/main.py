import time

from machine import Pin
import network

from config import CONFIG
from secrets import SECRETS


def start() -> None:
    setup_wifi()
    setup_io()

    while True:
        print("Pulse!")
        send_pulse()
        time.sleep(1)


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


if __name__ == "__main__":
    start()
