import time
from typing import NoReturn

import machine
import network


def wlan_status_to_text(status:int) -> str:
    statuses = (i for i in dir(network) if i.startswith("STAT_"))
    for attr in statuses:
        if getattr(network, attr) == status:
            return attr


def show_ip() -> None:
    tick_freq = 5
    wlan = network.WLAN(network.STA_IF)

    print("Checking wlan interface status")
    for _ in range(60 * tick_freq):
        if wlan.status() != network.STAT_CONNECTING:
            break
        print(".", end="")
        time.sleep(1/tick_freq)

    print("\nWlan status:", wlan_status_to_text(wlan.status()))
    ip = wlan.ifconfig()[0]
    print("IP Address:", ip)


def reset(soft:bool=False) -> NoReturn:
    if soft:
        machine.soft_reset()

    machine.reset()
