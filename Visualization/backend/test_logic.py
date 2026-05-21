"""Smoke tests cho logic tim kiem — chay: python test_logic.py (tu thu muc backend)"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from thuat_toan.search_adapters import run_puzzle_search, run_vacuum_search  # noqa: E402
from backend.app.services.search_service import run_puzzle, run_vacuum  # noqa: E402
from thuat_toan.tree_builder import build_search_tree  # noqa: E402

GOAL = [1, 2, 3, 4, 5, 6, 7, 8, 0]
ALGORITHMS = ["bfs1", "bfs2", "dfs1", "dfs2"]


def ok(msg):
    print(f"  [OK] {msg}")


def fail(msg):
    print(f"  [FAIL] {msg}")
    return False


def test_puzzle_goal_state():
    print("\n=== 8-Puzzle: start = goal ===")
    passed = True
    for algo in ALGORITHMS:
        steps = run_puzzle_search(algo, GOAL)
        final = steps[-1] if steps else None
        if final and final.found and final.path:
            ok(f"{algo}: found, path len={len(final.path)}")
        else:
            passed = fail(f"{algo}: expected found on solved board")
    return passed


def test_puzzle_solvable():
    print("\n=== 8-Puzzle: trang thai giai duoc (1 buoc) ===")
    board = [1, 2, 3, 4, 5, 6, 0, 7, 8]  # empty o 6, 1 buoc den goal
    passed = True
    for algo in ALGORITHMS:
        steps = run_puzzle_search(algo, board)
        final = steps[-1] if steps else None
        if final and final.found:
            ok(f"{algo}: found in {len(steps)} steps")
        else:
            passed = fail(f"{algo}: should find goal — {final.message if final else 'no steps'}")
    return passed


def test_puzzle_api_service():
    print("\n=== API service: run_puzzle ===")
    board = [1, 2, 3, 4, 5, 6, 0, 7, 8]
    r = run_puzzle("bfs1", board)
    checks = [
        r.get("mode") == "puzzle",
        r.get("found") is True,
        len(r.get("steps", [])) > 0,
        len(r.get("tree", {}).get("nodes", [])) > 0,
        r.get("path") is not None,
    ]
    if all(checks):
        ok(f"found={r['found']}, steps={r['steps_count']}, tree_nodes={len(r['tree']['nodes'])}")
        return True
    return fail(f"checks failed: {checks}")


def test_vacuum_no_dirt():
    print("\n=== Vacuum: khong con bui ===")
    steps = run_vacuum_search("bfs1", 100, 100, [], 0, 0, 400, 400, 34)
    if steps == []:
        ok("tra ve [] khi het bui")
        return True
    return fail(f"expected [], got {len(steps)} steps")


def test_vacuum_with_dirt():
    print("\n=== Vacuum: co bui, goal gan ===")
    dirt = [
        {"x": 120, "y": 120, "size": 6, "clean": False},
        {"x": 300, "y": 300, "size": 6, "clean": False},
    ]
    robot_x, robot_y = 200.0, 200.0
    passed = True
    for algo in ALGORITHMS:
        steps = run_vacuum_search(algo, robot_x, robot_y, dirt, 0, 0, 400, 400, 34)
        final = steps[-1] if steps else None
        if final and final.found and final.path:
            ok(f"{algo}: path len={len(final.path)}, msg={final.message[:40]}...")
        else:
            passed = fail(f"{algo}: {final.message if final else 'no result'}")
    return passed


def test_vacuum_api_timeout_shape():
    print("\n=== API service: run_vacuum (timeout wrapper) ===")
    dirt = [{"x": 50, "y": 50, "size": 6, "clean": False}]
    r = run_vacuum("bfs1", 200, 200, dirt, 0, 0, 400, 400, 34, timeout_sec=30)
    if "steps" in r and "tree" in r and "timed_out" in r:
        ok(f"found={r['found']}, timed_out={r['timed_out']}, elapsed={r['elapsed_ms']}ms")
        return True
    return fail("missing keys in response")


def test_tree_builder():
    print("\n=== Tree builder ===")
    board = [1, 2, 3, 4, 5, 6, 0, 7, 8]
    steps = run_puzzle_search("bfs1", board)
    tree = build_search_tree(steps)
    if tree["nodes"] and tree["edges"]:
        ok(f"nodes={len(tree['nodes'])}, edges={len(tree['edges'])}")
        return True
    return fail("empty tree")


def main():
    print("Backend logic tests")
    print("=" * 50)
    results = [
        test_puzzle_goal_state(),
        test_puzzle_solvable(),
        test_puzzle_api_service(),
        test_vacuum_no_dirt(),
        test_vacuum_with_dirt(),
        test_vacuum_api_timeout_shape(),
        test_tree_builder(),
    ]
    passed = sum(results)
    total = len(results)
    print("\n" + "=" * 50)
    print(f"Tong: {passed}/{total} nhom test PASS")
    if passed < total:
        sys.exit(1)
    print("Tat ca test logic backend: OK")


if __name__ == "__main__":
    main()
