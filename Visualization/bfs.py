from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


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


def bfs(
    start_state: Any,
    goal_state: Any,
    get_next_states: Callable[[Any], List[Any]],
    max_steps: Optional[int] = None,
) -> List[SearchStep]:
    """
    BFS binh thuong:
    - Lay state ra khoi queue.
    - Neu state duoc lay ra giong goal thi moi hoan thanh.
    - Khi sinh ra state moi, chi dua vao queue, chua ket thuc ngay.
    """
    queue = [start_state]
    visited = {start_state}
    visited_order = [start_state]
    parent = {start_state: None}
    steps: List[SearchStep] = []
    expanded_count = 0

    while queue:
        if max_steps is not None and expanded_count >= max_steps:
            steps.append(
                SearchStep(
                    action="limited",
                    current_state=None,
                    generated_states=[],
                    frontier=queue.copy(),
                    visited=visited_order.copy(),
                    found=False,
                    path=None,
                    message="Dung lai vi dat gioi han so buoc mo rong.",
                )
            )
            return steps

        current_state = queue.pop(0)

        if current_state == goal_state:
            path = build_path(parent, goal_state)
            steps.append(
                SearchStep(
                    action="finish",
                    current_state=current_state,
                    generated_states=[],
                    frontier=queue.copy(),
                    visited=visited_order.copy(),
                    found=True,
                    path=path,
                    message="BFS ket thuc vi state duoc lay ra khoi queue la goal.",
                )
            )
            return steps

        generated_states = []

        # CHO SINH RA CAC STATE MOI CUA MOI TRUONG:
        # UI co the highlight cac state nam trong generated_states.
        for next_state in get_next_states(current_state):
            if next_state not in visited:
                visited.add(next_state)
                visited_order.append(next_state)
                parent[next_state] = current_state
                queue.append(next_state)
                generated_states.append(next_state)

        steps.append(
            SearchStep(
                action="expand",
                current_state=current_state,
                generated_states=generated_states,
                frontier=queue.copy(),
                visited=visited_order.copy(),
                found=False,
                path=None,
                message="Sinh state moi va dua vao queue. BFS binh thuong chua ket thuc tai luc sinh.",
            )
        )
        expanded_count += 1

    steps.append(
        SearchStep(
            action="not_found",
            current_state=None,
            generated_states=[],
            frontier=[],
            visited=visited_order.copy(),
            found=False,
            path=None,
            message="Khong tim thay goal.",
        )
    )
    return steps


if __name__ == "__main__":
    graph = {
        "A": ["B", "C"],
        "B": ["D", "E"],
        "C": ["F"],
        "D": [],
        "E": ["G"],
        "F": [],
        "G": [],
    }

    result = bfs("A", "G", lambda state: graph[state])
    for step in result:
        print(step)
