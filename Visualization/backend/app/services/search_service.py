import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from thuat_toan.search_adapters import (  # noqa: E402
    grid_to_point,
    run_puzzle_search,
    run_vacuum_search,
)
from thuat_toan.tree_builder import build_search_tree  # noqa: E402

from ..serializers import steps_response  # noqa: E402


def run_puzzle(algorithm: str, board: List[int]) -> Dict[str, Any]:
    started = time.perf_counter()
    steps = run_puzzle_search(algorithm, board)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    final = steps[-1] if steps else None
    return _pack_result("puzzle", algorithm, steps, final, elapsed_ms, list(board))


def run_vacuum(
    algorithm: str,
    robot_x: float,
    robot_y: float,
    dirt: List[Dict[str, Any]],
    room_x: float,
    room_y: float,
    room_w: float,
    room_h: float,
    cell_size: float,
    timeout_sec: Optional[int] = 60,
) -> Dict[str, Any]:
    started = time.perf_counter()
    steps = _run_vacuum_with_timeout(
        algorithm,
        robot_x,
        robot_y,
        dirt,
        room_x,
        room_y,
        room_w,
        room_h,
        cell_size,
        timeout_sec,
    )
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    final = steps[-1] if steps else None
    timed_out = final and getattr(final, "timed_out", False)

    payload = _pack_result("vacuum", algorithm, steps, final, elapsed_ms, None)
    payload["timed_out"] = timed_out

    if final and final.found and final.path:
        payload["path_points"] = [
            grid_to_point(cell, room_x, room_y, cell_size) for cell in final.path
        ]
    else:
        payload["path_points"] = []

    return payload


def _run_vacuum_with_timeout(
    algorithm_name,
    robot_x,
    robot_y,
    dirt,
    room_x,
    room_y,
    room_w,
    room_h,
    cell_size,
    timeout_sec,
):
    result_holder = [None]
    exception_holder = [None]

    def worker():
        try:
            result_holder[0] = run_vacuum_search(
                algorithm_name,
                robot_x,
                robot_y,
                dirt,
                room_x,
                room_y,
                room_w,
                room_h,
                cell_size,
            )
        except Exception as exc:
            exception_holder[0] = exc

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    t.join(timeout=timeout_sec)

    if exception_holder[0]:
        raise exception_holder[0]

    if result_holder[0] is not None:
        return result_holder[0]

    class _TimeoutStep:
        def __init__(self):
            self.action = "timeout"
            self.found = False
            self.path = None
            self.current_state = None
            self.frontier = []
            self.visited = []
            self.generated_states = []
            self.message = f"Timeout sau {timeout_sec}s"
            self.timed_out = True

    return [_TimeoutStep()]


def _pack_result(mode, algorithm, steps, final, elapsed_ms, start_state):
    found = bool(final and final.found)
    path = list(final.path) if final and final.path else None
    if path:
        path = [_json_tuple(p) for p in path]

    return {
        "mode": mode,
        "algorithm": algorithm,
        "found": found,
        "message": final.message if final else "Khong co ket qua",
        "elapsed_ms": elapsed_ms,
        "steps_count": len(steps),
        "steps": steps_response(steps),
        "path": path,
        "tree": build_search_tree(steps),
        "start_state": start_state,
        "goal_state": None,
    }


def _json_tuple(state):
    if isinstance(state, tuple):
        return list(state)
    return state
