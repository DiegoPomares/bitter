from typing import Any, Dict, Optional

from actions import gpio_state, gpio_modulate
import exceptions
from vendor.microdot_asyncio import Microdot, Request, Response


def setup(app:Microdot) -> None:
    Response.default_content_type = 'application/json'


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

        actions = body["actions"]
        repeat = body.pop("repeat", 0)
        await gpio_modulate(pin_id_or_alias, *actions, repeat=repeat)


    @app.errorhandler(exceptions.NotFound)
    def not_found(request:Request, ex:exceptions.NotFound):
        return {"error": str(ex)}, 404
