from itertools import count
from typing import Any, Callable, Dict, Optional, Tuple

import machine
import uasyncio


class PinPlus:
    # machine.Pin is wrapped because inheriting from it causes super() to misbehave ¯\_(ツ)_/¯
    Pin = machine.Pin

    defaults = {
        "mode": "IN",
        "pull": None,
        "drive": None,
        "alt": None,
    }

    def __init__(self, pin_id:int, mode:int=..., pull:int=..., *, value:Any=..., drive:int=..., alt:int=...,
                 invert:bool=False):
        self._pin_id = pin_id
        self._run_script = False
        self._pin_state = self.defaults.copy()
        self.invert = invert
        if self.invert and value is not ...:
            value = not bool(value)

        args, kwargs = self._filter_ellipsis(pin_id, mode, pull, value=value, drive=drive, alt=alt)
        self._pin = self.Pin(*args, **kwargs)

    @classmethod
    def _pinattr(cls, attr_name:str) -> Any:
        if attr_name is ...:
            return ...
        return getattr(cls.Pin, attr_name)

    @staticmethod
    def _filter_ellipsis(*args:Any, **kwargs:Any) -> Tuple(Tuple(Any), Dict[str, Any]):
        fargs = tuple(i for i in args if i is not ...)
        fkwargs = {k: v for k, v in kwargs.items() if v is not ...}
        return fargs, fkwargs

    def init(self, mode:int=..., pull:int=..., *, value:Any=..., drive:int=..., alt:int=...,
             invert:bool=...) -> None:
        self._run_script = False

        if invert is not ...:
            self.invert = invert

        if self.invert and value is not None:
            value = not bool(value)

        args, kwargs = self._filter_ellipsis(mode, pull, value=value, drive=drive, alt=alt)
        self._pin.init(*args, **kwargs)

    def value(self, x:Any=..., *, stop_script:bool=True) -> Optional[int]:
        if stop_script:
            self._run_script = False

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

    def _save_pin_state(self, mode:str=..., pull:str=..., drive:str=..., alt:str=...) -> None:
        _, kwargs = self._filter_ellipsis(mode=mode, pull=pull, drive=drive, alt=alt)
        self._pin_state.update(kwargs)

    def state(self) -> Dict[str, Any]:
        pin_state = {
            "value": bool(self.value()),
            "config": {
                "id": self._pin_id,
                "inverted": self.invert,
            },
        }

        pin_state["config"].update(self._pin_state)
        return pin_state

    def easy_config(self, *, mode:str=..., pull:str=..., value:Any=..., drive:str=..., alt:str=...,
                    invert:bool=...) -> None:
        args, kwargs = self._filter_ellipsis(
            self._pinattr(mode), self._pinattr(pull),
            value=value, drive=self._pinattr(drive), alt=self._pinattr(alt), invert=invert
        )
        self.init(*args, **kwargs)
        self._save_pin_state(mode=mode, pull=pull, drive=drive, alt=alt)

    async def modulate(self, *actions:str, **_kwargs) -> None:
        self._run_script = True
        pointer = 0
        script = [Action.from_str(self, i) for i in actions]

        while self._run_script and pointer < len(script):
            new_pointer = await script[pointer].run()
            if new_pointer is not None:
                pointer = new_pointer
            else:
                pointer += 1


class Action:
    def __init__(self, pin:PinPlus, *args:Any):
        self.pin = pin
        self.args = args
        self.init()

    @staticmethod
    def from_str(pin:PinPlus, action_str:str) -> "Action":
        args = action_str.split(" ")[1:]

        if action_str == "on":
            action = OnAction
        elif action_str == "off":
            action = OffAction
        elif action_str.startswith("delay "):
            action = DelayAction
        elif action_str.startswith("repeat "):
            action = RepeatAction
        else:
            raise TypeError(f"Action '{action_str}' is not supported")

        try:
            return action(pin, *args)
        except Exception as ex:
            raise TypeError(f"Error with action '{action_str}': {str(ex)}")

    def init(self) -> None:
        pass

    async def run(self) -> Optional[int]:
        raise NotImplementedError()


class OnAction(Action):
    async def run(self) -> None:
        self.pin.value(True, stop_script=False)


class OffAction(Action):
    async def run(self) -> None:
        self.pin.value(False, stop_script=False)


class DelayAction(Action):
    def init(self) -> None:
        self.ms = int(self.args[0])
    async def run(self) -> None:
        await uasyncio.sleep_ms(self.ms)


class RepeatAction(Action):
    def init(self) -> None:
        self.times = int(self.args[0]) - 1
        self.left = self.times
        self.jump = 0 if len(self.args) == 1 else int(self.args[1])
    async def run(self) -> Optional[int]:
        if self.left == 0:
            self.left = self.times
            return None
        self.left -= 1
        return 0
