from typing import Any, Callable, Optional

import machine


class PinPlus:
    Pin = machine.Pin

    def __init__(self, *args:Any, **kwargs:Any):
        self.invert = kwargs.pop("invert", False)
        # Calling super().__init__ with **kwargs doesn't work when Pin is the parent class ¯\_(ツ)_/¯
        self._pin = self.Pin(*args, **kwargs)

    def init(self, *args:Any, **kwargs:Any) -> None:
        if self.invert and "value" in kwargs:
            kwargs["value"] = not bool(kwargs["value"])

        self._pin.init(*args, **kwargs)

    def value(self, x:Optional[Any]=None) -> Optional[int]:
        if x is None:
            pin_value = self._pin.value()
            if self.invert:
                pin_value = pin_value ^ 1

            return pin_value

        if self.invert:
            x = not bool(x)

        return self._pin.value(x)

    def __call__(self, x:Optional[Any]=None) -> Optional[int]:
        return self.value(x)

    def on(self) -> None:
        self.value(1)

    def off(self) -> None:
        self.value(0)

    def irq(self, handler:Callable[["PinPlus"], None],
            *args:Any, **kwargs:Any) -> Callable[["PinPlus"], None]:

        def callback(_pin:self.Pin) -> None:
            handler(self)

        self._pin.irq(callback, *args, **kwargs)
