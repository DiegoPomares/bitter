from typing import Dict, Union

from pinplus import PinPlus

pin_aliases:Dict[str, int] = {}
pin_config:Dict[str, PinPlus] = {}


def setup(aliases:Dict[str, int]) -> None:
    pin_aliases.update(aliases)
    configure_pins()


def configure_pins() -> None:
    pin_id = pin_aliases["led"]
    pin_config[pin_id] = PinPlus(pin_id, PinPlus.Pin.OUT, value=1, invert=True)


def pin(pin_id_alias:Union[str, int]) -> PinPlus:
    if isinstance(pin_id_alias, str):
        pin_id_alias = pin_aliases[pin_id_alias]

    return pin_config[pin_id_alias]
