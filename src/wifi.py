from typing import Dict

import network


def setup_wifi(configuration:Dict[str, str]) -> None:
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(configuration["ssid"], configuration["key"])

    if not configuration.get("dhcp"):
        pass
