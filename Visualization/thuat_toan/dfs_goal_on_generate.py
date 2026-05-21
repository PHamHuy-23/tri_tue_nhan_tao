from typing import Any, Callable, List, Optional

from .search_step import SearchStep, build_path


def dfs_goal_on_generate(
    start_state: Any,
    goal_state: Any,
    get_next_states: Callable[[Any], List[Any]],
    max_steps: Optional[int] = None,
) -> List[SearchStep]:
    stack = [start_state]
    visited = {start_state}
    visited_order = [start_state]
    parent = {start_state: None}
    steps: List[SearchStep] = []
    expanded_count = 0

    if start_state == goal_state:
        return [
            SearchStep(
                action="finish",
                current_state=start_state,
                generated_states=[],
                frontier=[],
                visited=visited_order.copy(),
                found=True,
                path=[start_state],
                message="Start state da la goal.",
            )
        ]

    while stack:
        if max_steps is not None and expanded_count >= max_steps:
            steps.append(
                SearchStep(
                    action="limited",
                    current_state=None,
                    generated_states=[],
                    frontier=stack.copy(),
                    visited=visited_order.copy(),
                    found=False,
                    path=None,
                    message="Dung lai vi dat gioi han so buoc mo rong.",
                )
            )
            return steps

        current_state = stack.pop()
        generated_states = []

        for next_state in get_next_states(current_state):
            if next_state not in visited:
                visited.add(next_state)
                visited_order.append(next_state)
                parent[next_state] = current_state
                generated_states.append(next_state)

                if next_state == goal_state:
                    path = build_path(parent, goal_state)
                    steps.append(
                        SearchStep(
                            action="finish_on_generate",
                            current_state=current_state,
                            generated_states=generated_states.copy(),
                            frontier=stack.copy(),
                            visited=visited_order.copy(),
                            found=True,
                            path=path,
                            message="DFS ket thuc ngay khi sinh ra state moi la goal.",
                        )
                    )
                    return steps

                stack.append(next_state)

        steps.append(
            SearchStep(
                action="expand",
                current_state=current_state,
                generated_states=generated_states,
                frontier=stack.copy(),
                visited=visited_order.copy(),
                found=False,
                path=None,
                message="Sinh state moi va dua vao stack vi chua gap goal.",
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
