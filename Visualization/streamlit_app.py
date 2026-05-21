import random
from html import escape

import streamlit as st

from search_adapters import (
    get_vacuum_next_states,
    grid_to_point,
    run_algorithm,
    run_puzzle_search,
)


ALGORITHMS = ["bfs1", "bfs2", "dfs1", "dfs2"]
GOAL_PUZZLE = [1, 2, 3, 4, 5, 6, 7, 8, 0]
VACUUM_COLS = 8
VACUUM_ROWS = 8


st.set_page_config(
    page_title="AI Agent Visualizer",
    page_icon="AI",
    layout="wide",
)


st.markdown(
    """
    <style>
      :root {
        --bg: #181425;
        --panel: #262b44;
        --panel-dark: #1f2235;
        --line: #3a4466;
        --text: #f4f4f4;
        --muted: #a7b0d8;
        --accent: #f4b860;
        --green: #63c74d;
        --red: #e43b44;
        --blue: #4fa4b8;
        --floor-a: #755f4a;
        --floor-b: #6a5545;
        --dirt: #2f251d;
      }

      .stApp {
        background:
          linear-gradient(#1f1a31 1px, transparent 1px),
          linear-gradient(90deg, #1f1a31 1px, transparent 1px),
          var(--bg);
        background-size: 22px 22px;
        color: var(--text);
      }

      h1, h2, h3, p, div, button {
        font-family: Consolas, "Courier New", monospace !important;
      }

      .pixel-panel {
        background: var(--panel);
        border: 4px solid var(--line);
        padding: 18px;
        box-shadow: 5px 6px 0 #1f2235;
      }

      .puzzle-board {
        display: grid;
        grid-template-columns: repeat(3, 128px);
        grid-template-rows: repeat(3, 128px);
        gap: 8px;
        width: max-content;
        padding: 18px;
        background: var(--panel-dark);
        border: 4px solid var(--line);
      }

      .tile {
        display: grid;
        place-items: center;
        height: 128px;
        background: var(--accent);
        color: var(--bg);
        border: 4px solid #ffd98a;
        box-shadow: 5px 6px 0 #c9822b;
        font-size: 46px;
        font-weight: 800;
        text-decoration: none;
        cursor: default;
      }

      a.tile {
        cursor: pointer;
      }

      a.tile:hover {
        transform: translate(2px, 2px);
        box-shadow: 3px 4px 0 #c9822b;
      }

      .empty-tile {
        background: var(--bg);
        border: 4px solid var(--line);
        box-shadow: none;
      }

      .trace-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
      }

      .trace-col {
        min-height: 330px;
        background: var(--panel-dark);
        border: 3px solid var(--line);
        padding: 10px;
      }

      .trace-title {
        color: var(--accent);
        text-align: center;
        font-weight: 800;
        font-size: 13px;
        margin-bottom: 12px;
      }

      .trace-item {
        color: var(--text);
        font-size: 12px;
        line-height: 1.8;
        white-space: nowrap;
      }

      .vacuum-room {
        display: grid;
        grid-template-columns: repeat(8, 54px);
        grid-template-rows: repeat(8, 54px);
        width: max-content;
        padding: 16px;
        background: #3e3546;
        border: 6px solid #54475e;
      }

      .cell {
        position: relative;
        width: 54px;
        height: 54px;
        border: 1px solid #5f4a3e;
      }

      .floor-a { background: var(--floor-a); }
      .floor-b { background: var(--floor-b); }
      .reached { outline: 4px solid var(--line); outline-offset: -8px; }
      .frontier { outline: 4px solid var(--accent); outline-offset: -8px; }
      .current { outline: 5px solid var(--green); outline-offset: -7px; }
      .path { box-shadow: inset 0 0 0 5px rgba(99, 199, 77, 0.75); }

      .robot {
        position: absolute;
        width: 34px;
        height: 34px;
        left: 10px;
        top: 10px;
        border-radius: 50%;
        background: var(--blue);
        border: 4px solid #d7f6ff;
      }

      .dirt {
        position: absolute;
        width: 14px;
        height: 14px;
        left: 20px;
        top: 20px;
        background: var(--dirt);
      }

      .status {
        color: var(--muted);
        font-size: 14px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def compact_state(state):
    if state is None:
        return "-"
    if isinstance(state, tuple) and len(state) == 9:
        values = ["_" if value == 0 else str(value) for value in state]
        return "/".join(["".join(values[0:3]), "".join(values[3:6]), "".join(values[6:9])])
    return str(state)


def puzzle_neighbors(index):
    row = index // 3
    col = index % 3
    result = []
    if row > 0:
        result.append(index - 3)
    if row < 2:
        result.append(index + 3)
    if col > 0:
        result.append(index - 1)
    if col < 2:
        result.append(index + 1)
    return result


def shuffle_puzzle():
    board = GOAL_PUZZLE.copy()
    empty = 8
    previous = None
    for _ in range(8):
        choices = puzzle_neighbors(empty)
        if previous in choices and len(choices) > 1:
            choices.remove(previous)
        next_empty = random.choice(choices)
        board[empty], board[next_empty] = board[next_empty], board[empty]
        previous = empty
        empty = next_empty
    return board


def ensure_state():
    if "screen" not in st.session_state:
        st.session_state.screen = "8-puzzle"
    if "algorithm" not in st.session_state:
        st.session_state.algorithm = "bfs1"
    if "puzzle_board" not in st.session_state:
        st.session_state.puzzle_board = shuffle_puzzle()
    if "puzzle_steps" not in st.session_state:
        st.session_state.puzzle_steps = []
    if "puzzle_step_index" not in st.session_state:
        st.session_state.puzzle_step_index = 0
    if "puzzle_solution" not in st.session_state:
        st.session_state.puzzle_solution = []
    if "vacuum_robot" not in st.session_state:
        st.session_state.vacuum_robot = (VACUUM_COLS // 2, VACUUM_ROWS // 2)
    if "vacuum_dirt" not in st.session_state:
        st.session_state.vacuum_dirt = make_dirt_cells()
    if "vacuum_steps" not in st.session_state:
        st.session_state.vacuum_steps = []
    if "vacuum_step_index" not in st.session_state:
        st.session_state.vacuum_step_index = 0
    if "vacuum_path" not in st.session_state:
        st.session_state.vacuum_path = []
    if "vacuum_message" not in st.session_state:
        st.session_state.vacuum_message = "Chon thuat toan roi bam Apply."


def make_dirt_cells():
    cells = set()
    while len(cells) < 14:
        cells.add((random.randrange(VACUUM_COLS), random.randrange(VACUUM_ROWS)))
    return cells


def draw_puzzle_board(board):
    empty = board.index(0)
    movable_tiles = set(puzzle_neighbors(empty))
    html = ['<div class="puzzle-board">']
    for index, value in enumerate(board):
        if value == 0:
            html.append('<div class="tile empty-tile"></div>')
        elif index in movable_tiles:
            html.append(f'<a class="tile" href="?tile={index}">{escape(str(value))}</a>')
        else:
            html.append(f'<div class="tile">{escape(str(value))}</div>')
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def draw_trace_panel(steps, step_index, message):
    step = steps[min(step_index, len(steps) - 1)] if steps else None
    current = step.current_state if step else None
    frontier = step.frontier if step else []
    reached = step.visited if step else []

    def list_items(values):
        items = [f'<div class="trace-item">count: {len(values)}</div>']
        for value in values[:9]:
            items.append(f'<div class="trace-item">{escape(compact_state(value))}</div>')
        if len(values) > 9:
            items.append('<div class="trace-item">...</div>')
        return "".join(items)

    html = f"""
    <div class="pixel-panel">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <h3 style="margin:0;">Search Trace</h3>
        <strong style="color:var(--accent);">{min(step_index + 1, len(steps)) if steps else 0}/{len(steps)}</strong>
      </div>
      <div class="trace-grid">
        <div class="trace-col">
          <div class="trace-title">STATE DANG XET</div>
          <div class="trace-item" style="text-align:center;font-size:16px;margin-top:34px;">{escape(compact_state(current))}</div>
        </div>
        <div class="trace-col">
          <div class="trace-title">FRONTIER</div>
          {list_items(frontier)}
        </div>
        <div class="trace-col">
          <div class="trace-title">REACHED</div>
          {list_items(reached)}
        </div>
      </div>
      <p class="status">{escape(message)}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def draw_vacuum_room():
    step = None
    if st.session_state.vacuum_steps:
        step = st.session_state.vacuum_steps[
            min(st.session_state.vacuum_step_index, len(st.session_state.vacuum_steps) - 1)
        ]

    reached = set(step.visited[-30:]) if step else set()
    frontier = set(step.frontier[-20:]) if step else set()
    current = step.current_state if step else None
    path = set(st.session_state.vacuum_path)
    robot = st.session_state.vacuum_robot
    dirt = st.session_state.vacuum_dirt

    html = ['<div class="vacuum-room">']
    for row in range(VACUUM_ROWS):
        for col in range(VACUUM_COLS):
            cell = (col, row)
            classes = ["cell", "floor-a" if (row + col) % 2 == 0 else "floor-b"]
            if cell in reached:
                classes.append("reached")
            if cell in frontier:
                classes.append("frontier")
            if cell == current:
                classes.append("current")
            if cell in path:
                classes.append("path")

            inner = ""
            if cell in dirt:
                inner += '<div class="dirt"></div>'
            if cell == robot:
                inner += '<div class="robot"></div>'
            html.append(f'<div class="{" ".join(classes)}">{inner}</div>')
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def move_puzzle_tile(index):
    board = st.session_state.puzzle_board
    empty = board.index(0)
    if index not in puzzle_neighbors(empty):
        return
    board[empty], board[index] = board[index], board[empty]
    st.session_state.puzzle_steps = []
    st.session_state.puzzle_solution = []


def handle_puzzle_tile_query():
    tile = st.query_params.get("tile")
    if tile is None:
        return

    try:
        tile_index = int(tile)
    except ValueError:
        st.query_params.clear()
        return

    if st.session_state.screen == "8-puzzle" and 0 <= tile_index < 9:
        move_puzzle_tile(tile_index)
    st.query_params.clear()
    st.rerun()


def apply_puzzle_algorithm():
    steps = run_puzzle_search(st.session_state.algorithm, st.session_state.puzzle_board)
    st.session_state.puzzle_steps = steps
    st.session_state.puzzle_step_index = 0
    final_step = steps[-1] if steps else None
    st.session_state.puzzle_solution = list(final_step.path) if final_step and final_step.found else []


def nearest_dirty_cell(robot, dirt):
    if not dirt:
        return None
    return min(dirt, key=lambda cell: abs(robot[0] - cell[0]) + abs(robot[1] - cell[1]))


def apply_vacuum_algorithm():
    robot = st.session_state.vacuum_robot
    goal = nearest_dirty_cell(robot, st.session_state.vacuum_dirt)
    if goal is None:
        st.session_state.vacuum_message = "Phong da sach."
        return

    steps = run_algorithm(
        st.session_state.algorithm,
        robot,
        goal,
        lambda state: get_vacuum_next_states(state, VACUUM_COLS, VACUUM_ROWS),
        max_steps=1000,
    )
    st.session_state.vacuum_steps = steps
    st.session_state.vacuum_step_index = 0
    final_step = steps[-1] if steps else None
    st.session_state.vacuum_path = list(final_step.path[1:]) if final_step and final_step.found else []
    st.session_state.vacuum_message = "Dang hien thi BFS/DFS tim khu bui tiep theo."


def vacuum_move_one_path_cell():
    if not st.session_state.vacuum_path:
        if st.session_state.vacuum_dirt:
            apply_vacuum_algorithm()
        return

    next_cell = st.session_state.vacuum_path.pop(0)
    st.session_state.vacuum_robot = next_cell
    st.session_state.vacuum_dirt.discard(next_cell)
    if not st.session_state.vacuum_path and st.session_state.vacuum_dirt:
        apply_vacuum_algorithm()
    elif not st.session_state.vacuum_dirt:
        st.session_state.vacuum_message = "Da don sach phong."


def header():
    st.title("AI Agent Visualizer")
    tabs = st.columns([1, 1, 4])
    if tabs[0].button("8-PUZZLE", use_container_width=True):
        st.session_state.screen = "8-puzzle"
    if tabs[1].button("VACUUM", use_container_width=True):
        st.session_state.screen = "vacuum"


def side_controls():
    st.session_state.algorithm = st.selectbox(
        "Thuat toan",
        ALGORITHMS,
        index=ALGORITHMS.index(st.session_state.algorithm),
    )
    if st.button("APPLY", use_container_width=True):
        if st.session_state.screen == "8-puzzle":
            apply_puzzle_algorithm()
        else:
            apply_vacuum_algorithm()


def puzzle_screen():
    st.subheader("8-Puzzle")
    st.caption("Bam tile sat o trong de choi. Bam Apply de xem BFS/DFS tim goal tung buoc.")

    left, right = st.columns([1.1, 1])
    with left:
        draw_puzzle_board(st.session_state.puzzle_board)
        if st.button("Shuffle puzzle"):
            st.session_state.puzzle_board = shuffle_puzzle()
            st.session_state.puzzle_steps = []
            st.session_state.puzzle_solution = []

    with right:
        message = "Bam Next Search Step de xem tung buoc thuat toan."
        draw_trace_panel(st.session_state.puzzle_steps, st.session_state.puzzle_step_index, message)
        c1, c2 = st.columns(2)
        if c1.button("Next Search Step", use_container_width=True):
            if st.session_state.puzzle_steps:
                st.session_state.puzzle_step_index = min(
                    st.session_state.puzzle_step_index + 1,
                    len(st.session_state.puzzle_steps) - 1,
                )
        if c2.button("Show Answer", use_container_width=True):
            if st.session_state.puzzle_solution:
                st.session_state.puzzle_board = list(st.session_state.puzzle_solution[-1])
        if st.session_state.puzzle_solution:
            st.write("Duong di dap an:")
            st.code(" -> ".join(compact_state(state) for state in st.session_state.puzzle_solution))


def vacuum_screen():
    st.subheader("May hut bui")
    st.caption(st.session_state.vacuum_message)

    left, right = st.columns([1.1, 1])
    with left:
        draw_vacuum_room()
        c1, c2, c3 = st.columns(3)
        if c1.button("Auto Next", use_container_width=True):
            vacuum_move_one_path_cell()
        if c2.button("Find Next Dirt", use_container_width=True):
            apply_vacuum_algorithm()
        if c3.button("Reset Room", use_container_width=True):
            st.session_state.vacuum_robot = (VACUUM_COLS // 2, VACUUM_ROWS // 2)
            st.session_state.vacuum_dirt = make_dirt_cells()
            st.session_state.vacuum_steps = []
            st.session_state.vacuum_path = []
            st.session_state.vacuum_message = "Chon thuat toan roi bam Apply."

    with right:
        draw_trace_panel(
            st.session_state.vacuum_steps,
            st.session_state.vacuum_step_index,
            "Panel hien thi state dang xet, frontier va reached.",
        )
        if st.button("Next Search Step", use_container_width=True):
            if st.session_state.vacuum_steps:
                st.session_state.vacuum_step_index = min(
                    st.session_state.vacuum_step_index + 1,
                    len(st.session_state.vacuum_steps) - 1,
                )
        st.write(f"Con lai: {len(st.session_state.vacuum_dirt)} o bui")


ensure_state()
handle_puzzle_tile_query()
header()

sidebar, content = st.columns([0.22, 0.78])
with sidebar:
    side_controls()

with content:
    if st.session_state.screen == "8-puzzle":
        puzzle_screen()
    else:
        vacuum_screen()
