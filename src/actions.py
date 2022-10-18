from typing import Any, Dict

from exceptions import PinNotFound
from gpio import pin


async def gpio_state(pin_id_or_alias:str) -> Dict[str, Any]:
    gpio_pin = pin(pin_id_or_alias)
    if not gpio_pin:
        raise PinNotFound(f"Pin not found: {pin_id_or_alias}")

    return gpio_pin.state()


async def gpio_modulate(pin_id_or_alias:str, *actions:str, times:int) -> None:
    gpio_pin = pin(pin_id_or_alias)

    for _ in range(times):
        for action in actions:
            if action == "":
                pass
