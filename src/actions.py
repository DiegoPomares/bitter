from typing import Any, Dict

from exceptions import ActionError, PinNotFound
from gpio import pin
from pinplus import PinPlus


def _get_pin(pin_id_or_alias:str) -> PinPlus:
    if not (gpio_pin := pin(pin_id_or_alias)):
        raise PinNotFound(f"Pin not found: {pin_id_or_alias}")
    return gpio_pin


async def gpio_state(pin_id_or_alias:str) -> Dict[str, Any]:
    gpio_pin = _get_pin(pin_id_or_alias)
    return gpio_pin.state()


async def gpio_config(pin_id_or_alias:str, config:Dict[str, Any]) -> None:
    gpio_pin = _get_pin(pin_id_or_alias)
    return gpio_pin.easy_config(**config)


async def gpio_on(pin_id_or_alias:str) -> None:
    gpio_pin = _get_pin(pin_id_or_alias)
    gpio_pin.on()


async def gpio_off(pin_id_or_alias:str) -> None:
    gpio_pin = _get_pin(pin_id_or_alias)
    gpio_pin.off()


async def gpio_blink(pin_id_or_alias:str) -> None:
    await gpio_modulate(pin_id_or_alias, "on", "delay 96", "off", "delay 96", "repeat 12")


async def gpio_modulate(pin_id_or_alias:str, *actions:str) -> None:
    gpio_pin = _get_pin(pin_id_or_alias)
    try:
        await gpio_pin.modulate(*actions)
    except TypeError as ex:
        raise ActionError(str(ex))
