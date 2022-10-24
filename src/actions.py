from typing import Any, Dict

from exceptions import PinNotFound
from gpio import pin
from pinplus import PinPlus


def get_pin(pin_id_or_alias:str) -> PinPlus:
    if not (gpio_pin := pin(pin_id_or_alias)):
        raise PinNotFound(f"Pin not found: {pin_id_or_alias}")
    return gpio_pin


async def gpio_state(pin_id_or_alias:str) -> Dict[str, Any]:
    gpio_pin = get_pin(pin_id_or_alias)
    return gpio_pin.state()


async def gpio_config(pin_id_or_alias:str, config:Dict[str, Any]) -> None:
    gpio_pin = get_pin(pin_id_or_alias)
    return gpio_pin.easy_config(**config)


async def gpio_modulate(pin_id_or_alias:str, *actions:str, times:int) -> None:
    gpio_pin = get_pin(pin_id_or_alias)
    await gpio_pin.modulate(*actions, times=times)


async def gpio_on(pin_id_or_alias:str) -> None:
    gpio_pin = get_pin(pin_id_or_alias)
    gpio_pin.on()


async def gpio_off(pin_id_or_alias:str) -> None:
    gpio_pin = get_pin(pin_id_or_alias)
    gpio_pin.off()
