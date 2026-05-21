"""Xay dung cay tim kiem tu cac buoc expand de hien thi tren UI."""

from typing import Any, Dict, List


def state_key(state: Any) -> str:
    if state is None:
        return "_none_"
    if isinstance(state, tuple) and len(state) == 9:
        rows = (state[0:3], state[3:6], state[6:9])
        return "/".join("".join("_" if v == 0 else str(v) for v in row) for row in rows)
    if isinstance(state, (tuple, list)) and len(state) == 2:
        return f"{state[0]},{state[1]}"
    return str(state)


def build_search_tree(steps: List[Any], max_nodes: int = 80) -> Dict[str, Any]:
    nodes: Dict[str, Dict[str, Any]] = {}
    edges: List[Dict[str, str]] = []
    seen_edges: set = set()

    for step in steps:
        if getattr(step, "action", None) in ("limited", "not_found"):
            continue
        parent = step.current_state
        if parent is None:
            continue
        pid = state_key(parent)
        if pid not in nodes:
            nodes[pid] = {"id": pid, "label": _short_label(parent), "depth": len(edges)}
        for child in step.generated_states or []:
            cid = state_key(child)
            if cid not in nodes and len(nodes) < max_nodes:
                nodes[cid] = {"id": cid, "label": _short_label(child)}
            edge_key = (pid, cid)
            if edge_key not in seen_edges and len(edges) < max_nodes:
                seen_edges.add(edge_key)
                edges.append({"from": pid, "to": cid})

    if not nodes and steps:
        start = steps[0].current_state
        if start is not None:
            sid = state_key(start)
            nodes[sid] = {"id": sid, "label": _short_label(start)}

    return {
        "nodes": list(nodes.values())[:max_nodes],
        "edges": edges[:max_nodes],
    }


def _short_label(state: Any) -> str:
    if isinstance(state, tuple) and len(state) == 9:
        parts = []
        for row in (state[0:3], state[3:6], state[6:9]):
            parts.append("".join("_" if v == 0 else str(v) for v in row))
        return "|".join(parts)
    if isinstance(state, (tuple, list)) and len(state) == 2:
        return f"({state[0]},{state[1]})"
    return str(state)[:12]
