from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SearchStep:
    action: str
    current_state: Any
    generated_states: List[Any]
    frontier: List[Any]
    visited: List[Any]
    found: bool
    path: Optional[List[Any]]
    message: str


def build_path(parent: Dict[Any, Any], goal_state: Any) -> List[Any]:
    path = []
    state = goal_state

    while state is not None:
        path.append(state)
        state = parent[state]

    path.reverse()
    return path
