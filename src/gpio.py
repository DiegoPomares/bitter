from typing import Any, Dict, Optional

from pinplus import PinPlus

pin_names:Dict[str, int] = {}
pin_config:Dict[int, PinPlus] = {}


def setup(names:Dict[str, int], config:Dict[str, Any]) -> None:
    pin_names.update(names)
    _initialize_pins()
    _configure_pins(config)


def _initialize_pins() -> None:
    for pin_id in set(pin_names.values()):
        pin_config[pin_id] = PinPlus(pin_id)


def _configure_pins(config:Dict[str, Any]) -> None:
    for pin_name, pin_config in config.items():
        pin(pin_name).easy_config(**pin_config)


def pin(pin_id_or_alias:str) -> Optional[PinPlus]:
    pin_id = pin_names.get(pin_id_or_alias)
    if not pin_id:
        try:
            pin_id = int(pin_id_or_alias)
        except ValueError:
            pass

    return pin_config.get(pin_id)
