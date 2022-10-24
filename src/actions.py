from typing import Any, Dict

from exceptions import PinNotFound
from gpio import pin


async def gpio_state(pin_id_or_alias:str) -> Dict[str, Any]:
    if not (gpio_pin := pin(pin_id_or_alias)):
        raise PinNotFound(f"Pin not found: {pin_id_or_alias}")

    return gpio_pin.state()


async def gpio_modulate(pin_id_or_alias:str, *actions:str, times:int) -> None:
    if not (gpio_pin := pin(pin_id_or_alias)):
        raise PinNotFound(f"Pin not found: {pin_id_or_alias}")

    await gpio_pin.modulate(*actions, times=times)


async def gpio_on(pin_id_or_alias:str) -> None:
    if not (gpio_pin := pin(pin_id_or_alias)):
        raise PinNotFound(f"Pin not found: {pin_id_or_alias}")

    gpio_pin.on()


async def gpio_off(pin_id_or_alias:str) -> None:
    if not (gpio_pin := pin(pin_id_or_alias)):
        raise PinNotFound(f"Pin not found: {pin_id_or_alias}")

    gpio_pin.off()
