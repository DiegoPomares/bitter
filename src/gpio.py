from typing import Dict, Optional, Union

from pinplus import PinPlus

pin_aliases:Dict[str, int] = {}
pin_config:Dict[int, PinPlus] = {}


def setup(aliases:Dict[str, int]) -> None:
    pin_aliases.update(aliases)
    _initialize_pins()
    # TODO remove
    pin_config["led"].init(PinPlus.Pin.OUT, value=0, invert=True)
    pin_config["d1"].init(PinPlus.Pin.OUT, value=0)


def _initialize_pins() -> None:
    for pin_id in set(pin_aliases.values()):
        pin_config[pin_id] = PinPlus(pin_id)


def pin(pin_id_or_alias:Union[str, int]) -> Optional[PinPlus]:
    if isinstance(pin_id_or_alias, str):
        pin_id = pin_aliases.get(pin_id_or_alias)
    else:
        pin_id = pin_id_or_alias

    return pin_config.get(pin_id)
