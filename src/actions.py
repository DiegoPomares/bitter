import uasyncio

from exceptions import PinNotFound
from gpio import pin


async def send_pulse(pin_alias:str) -> None:
    pin(pin_alias).on()
    await uasyncio.sleep(3)
    pin(pin_alias).off()


async def gpio_state(pin_id_or_alias:str) -> bool:
    gpio_pin = pin(pin_id_or_alias)
    if not gpio_pin:
        raise PinNotFound(f"Pin not found: {pin_id_or_alias}")

    value = gpio_pin.value()
    return bool(value)


async def gpio_modulate(pin_id_or_alias:str) -> None:
    pass
