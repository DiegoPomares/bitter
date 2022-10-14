from typing import Any, Dict

import json


def read_config(path:str) -> Dict[str, Any]:
    with open(path) as fh:
        return json.load(fh)
