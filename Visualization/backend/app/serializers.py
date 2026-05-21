from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List


def step_to_dict(step: Any) -> Dict[str, Any]:
    if is_dataclass(step):
        data = asdict(step)
    else:
        data = dict(step)
    for key in ("current_state", "frontier", "visited", "generated_states", "path"):
        if key in data and data[key] is not None:
            data[key] = _jsonable(data[key])
    return data


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    return value


def steps_response(steps: List[Any]) -> List[Dict[str, Any]]:
    return [step_to_dict(s) for s in steps]
