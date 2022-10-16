from typing import Any, Callable, Dict, Optional, Tuple

import machine


class PinPlus:
    # machine.Pin is wrapped because inheriting from it causes super() to misbehave ¯\_(ツ)_/¯
    Pin = machine.Pin

    def __init__(self, pin_id:int, mode:int=..., pull:int=..., *, value:Any=..., drive:int=..., alt:int=...,
                 invert:bool=False):
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
        if invert is not None:
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
