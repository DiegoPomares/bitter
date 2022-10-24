from typing import Any, Dict, Optional

import uasyncio

from actions import gpio_config, gpio_modulate, gpio_on, gpio_off, gpio_state
from exceptions import MissingField, NotFound, SchemaError
from microdot_asyncio import Microdot, Request, Response

Response.default_content_type = "application/json"
app = Microdot()


def start() -> None:
    app.run(port=80, debug=True)


@app.get("/mem")
async def get_mem(_request:Request) -> None:
    import micropython
    micropython.mem_info(True)
    micropython.qstr_info(True)


@app.get("/gpio/<pin_id_or_alias>")
async def get_gpio(_request:Request, pin_id_or_alias:str) -> None:
    return await gpio_state(pin_id_or_alias)


@app.post("/gpio/<pin_id_or_alias>")
async def post_gpio(request:Request, pin_id_or_alias:str) -> None:
    body:Optional[Dict[str, Any]]
    if not (body := request.json):
        return None, 400

    dispatcher = None
    cmd = get_field(body, "cmd")
    if cmd == "on":
        dispatcher = gpio_on(pin_id_or_alias)

    elif cmd == "off":
        dispatcher = gpio_off(pin_id_or_alias)

    elif cmd == "modulate":
        script = get_field(body, "script")
        times = body.pop("times", 1)
        dispatcher = gpio_modulate(pin_id_or_alias, *script, times=times)

    else:
        raise SchemaError(f"Unknown command '{cmd}'")

    if request.args.get("wait", "") in ("true", "yes"):
        await dispatcher
    else:
        uasyncio.create_task(dispatcher)


@app.put("/gpio/<pin_id_or_alias>")
async def put_gpio(request:Request, pin_id_or_alias:str) -> None:
    body:Optional[Dict[str, Any]]
    if not (body := request.json):
        return None, 400

    return await gpio_config(pin_id_or_alias, body)


@app.errorhandler(NotFound)
async def not_found(request:Request, ex:NotFound):
    return {"error": str(ex)}, 404


@app.errorhandler(SchemaError)
async def schema_error(request:Request, ex:SchemaError):
    return {"error": str(ex)}, 400


def get_field(d:Dict, key:str) -> Any:
    if key not in d:
        raise MissingField(f"Missing field: {key}")

    return d[key]
