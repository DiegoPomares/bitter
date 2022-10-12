import time

import network
import usocket as socket
from machine import Pin

from config import CONFIG
from secrets import SECRETS


def start() -> None:
    setup_wifi()
    setup_io()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)

    while True:
        conn, addr = s.accept()

        request = conn.recv(1024)
        request = str(request)

        if request.find('/pulse'):
            send_pulse()

        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.close()


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
