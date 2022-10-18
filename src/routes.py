from typing import Any, Dict, Optional

import exceptions
from actions import gpio_state, gpio_modulate
from microdot_asyncio import Microdot, Request, Response

Response.default_content_type = 'application/json'
app = Microdot()


def start() -> None:
    app.run(port=80, debug=True)


@app.get("/gpio/<pin_id_or_alias>")
async def get_gpio(_request:Request, pin_id_or_alias:str) -> None:
    state = await gpio_state(pin_id_or_alias)
    return {
        "pin": pin_id_or_alias,
        "state": bool(state),
    }


@app.post("/gpio/<pin_id_or_alias>")
async def post_gpio(request:Request, pin_id_or_alias:str) -> None:
    body:Optional[Dict[str, Any]]
    if not (body := request.json):
        return None, 400

    cmd = body["cmd"]
    if cmd == "modulate":
        script = body["script"]
        times = body.pop("times", 1)
        await gpio_modulate(pin_id_or_alias, *script, times=times)

    return {"error": f"Unknown command {cmd}"}, 400


@app.errorhandler(exceptions.NotFound)
async def not_found(request:Request, ex:exceptions.NotFound):
    return {"error": str(ex)}, 404

