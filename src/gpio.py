from typing import Dict, Optional, Union

from pinplus import PinPlus

pin_aliases:Dict[str, int] = {}
pin_config:Dict[int, PinPlus] = {}


def setup(aliases:Dict[str, int]) -> None:
    pin_aliases.update(aliases)
    _initialize_pins()


def _initialize_pins() -> None:
    for pin_id in set(pin_aliases.values()):
        pin_config[pin_id] = PinPlus(pin_id)


def pin(pin_id_or_alias:str) -> Optional[PinPlus]:
    pin_id = pin_aliases.get(pin_id_or_alias)
    if not pin_id:
        try:
            pin_id = int(pin_id_or_alias)
        except ValueError:
            pass

    return pin_config.get(pin_id)
