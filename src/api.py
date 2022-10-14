from typing import NoReturn

from vendor.microdot_asyncio import Microdot, Request

app = Microdot()


def start() -> NoReturn:
    app.run(port=80, debug=True)


import uasyncio
from gpio import pin
async def send_pulse(pin_alias:str) -> None:
    pin(pin_alias).on()
    await uasyncio.sleep(3)
    pin(pin_alias).off()


@app.post("/pins/<pin_alias>")
async def index(request:Request, pin_alias:str) -> None:
    await send_pulse(pin_alias)
