from itertools import count
from typing import Any, Callable, Dict, Optional, Tuple

import machine
import uasyncio


class PinPlus:
    # machine.Pin is wrapped because inheriting from it causes super() to misbehave ¯\_(ツ)_/¯
    Pin = machine.Pin

    defaults = {
        "mode": 0,
        "pull": None,
        "drive": 0,
        "alt": None,
    }

    consts = {
        ...: ...,
        "IN": 0,
        "OUT": 1,
        "OPEN_DRAIN": 2,
        "PULL_UP": 1,
        "IRQ_RISING": 1,
        "IRQ_FALLING": 2,
        # Consts below this point HAVE NOT BEING VALIDATED
        "ALT": 3,
        "ALT_OPEN_DRAIN": 4,
        "ANALOG": 5,
        "PULL_DOWN": 0,
        "PULL_HOLD": 2,
        "DRIVE_0": 0,
        "DRIVE_1": 1,
        "DRIVE_2": 2,
        "IRQ_HIGH_LEVEL": 4,
        "IRQ_LOW_LEVEL": 8,
    }

    def __init__(self, pin_id:int, mode:int=..., pull:int=..., *, value:Any=..., drive:int=..., alt:int=...,
                 invert:bool=False):
        self._pin_id = pin_id
        self.invert = invert
        if self.invert and value is not ...:
            value = not bool(value)

        args, kwargs = self._filter_ellipsis(pin_id, mode, pull, value=value, drive=drive, alt=alt)
        self._pin = self.Pin(*args, **kwargs)

    @staticmethod
    def _filter_ellipsis(*args:Any, **kwargs:Any) -> Tuple(Tuple(Any), Dict[str, Any]):
        fargs = tuple(i for i in args if i is not ...)
        fkwargs = {k: v for k, v in kwargs.items() if v is not ...}
        return fargs, fkwargs

    def init(self, mode:int=..., pull:int=..., *, value:Any=..., drive:int=..., alt:int=...,
             invert:bool=...) -> None:
        if invert is not ...:
            self.invert = invert

        if self.invert and value is not None:
            value = not bool(value)

        args, kwargs = self._filter_ellipsis(mode, pull, value=value, drive=drive, alt=alt)
        self._pin.init(*args, **kwargs)

    def value(self, x:Any=...) -> Optional[int]:
        if x is ...:
            pin_value = self._pin.value()
            if self.invert:
                pin_value = pin_value ^ 1

            return pin_value

        if self.invert:
            x = not bool(x)

        return self._pin.value(x)

    def __call__(self, x:Any=...) -> Optional[int]:
        return self.value(x)

    def on(self) -> None:
        self.value(1)

    def off(self) -> None:
        self.value(0)

    def irq(self, handler:Callable[["PinPlus"], None], trigger:int, *,
            priority:int=..., wake:int=..., hard:bool=...) -> Callable[["PinPlus"], None]:

        def callback(_pin:self.Pin) -> None:
            handler(self)

        args, kwargs = self._filter_ellipsis(priority=priority, wake=wake, hard=hard)
        self._pin.irq(callback, trigger, *args, **kwargs)

    def state(self) -> Dict[str, Any]:
        pass

    def easy_config(self, *, mode:str=..., pull:str=..., value:Any=..., drive:str=..., alt:str=...,
                    invert:bool=...) -> None:
        args = (
            self.consts[mode],
            self.consts[pull],
        )
        kwargs = {
            "value": value,
            "drive": self.consts[drive],
            "alt": self.consts[alt],
            "invert": invert,
        }
        args, kwargs = self._filter_ellipsis(*args, **kwargs)
        self.init(*args, **kwargs)

    async def modulate(self, *actions:str, times:int=1) -> Callable[[], None]:
        iterator = range(times)
        if times < 1:
            iterator = count()

        for _ in iterator:
            for action in actions:
                if action == "on":
                    self.on()
                    uasyncio.sleep_ms(1)

                elif action == "off":
                    self.off()
                    uasyncio.sleep_ms(1)

                elif action.startswith("delay "):
                    _, ms_str = action.split(" ", 1)
                    try:
                        ms = int(ms_str)
                        await uasyncio.sleep_ms(ms)
                    except ValueError:
                        pass  # TODO: think how to handle faulty delays

                else:
                    pass  # TODO: think how to handle faulty actions
