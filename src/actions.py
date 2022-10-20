from itertools import count
from typing import Any, Dict

import uasyncio

from exceptions import PinNotFound
from gpio import pin


async def gpio_state(pin_id_or_alias:str) -> Dict[str, Any]:
    gpio_pin = pin(pin_id_or_alias)
    if not gpio_pin:
        raise PinNotFound(f"Pin not found: {pin_id_or_alias}")

    return gpio_pin.state()


async def gpio_modulate(pin_id_or_alias:str, *actions:str, times:int) -> None:
    gpio_pin = pin(pin_id_or_alias)

    iterator = range(times)
    if times < 1:
        iterator = count()

    print(actions, times, iterator)
    for _ in iterator:
        for action in actions:
            if action == "high":
                gpio_pin.on()
                uasyncio.sleep_ms(1)

            elif action == "low":
                gpio_pin.off()
                uasyncio.sleep_ms(1)

            elif action.startswith("delay "):
                _, ms_str = action.split(" ", 1)
                try:
                    ms = int(ms_str)
                except ValueError:
                    raise

                await uasyncio.sleep_ms(ms)

            else:
                pass  # TODO: think how to handle faulty actions
