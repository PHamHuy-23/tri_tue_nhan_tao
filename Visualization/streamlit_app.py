import random
from html import escape

import streamlit as st
import streamlit.components.v1 as components

from search_adapters import grid_to_point, run_puzzle_search, run_vacuum_search


WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 720
TOP_BAR_HEIGHT = 74
LEFT_PANEL_WIDTH = 204
BOARD_TILE_SIZE = 132
BOARD_GAP = 8
BOARD_SIZE = BOARD_TILE_SIZE * 3 + BOARD_GAP * 2
MAIN_PANEL_X = LEFT_PANEL_WIDTH + 52
MAIN_PANEL_Y = 204
INFO_PANEL_X = 704
INFO_PANEL_Y = 210
TRACE_PANEL_W = 374
TRACE_PANEL_H = 392

ALGORITHMS = ["bfs1", "bfs2", "dfs1", "dfs2"]
GOAL_PUZZLE = [1, 2, 3, 4, 5, 6, 7, 8, 0]

COLORS = {
    "bg": "#181425",
    "panel": "#262b44",
    "panel_dark": "#1f2235",
    "line": "#3a4466",
    "text": "#f4f4f4",
    "muted": "#a7b0d8",
    "accent": "#f4b860",
    "accent_dark": "#c9822b",
    "green": "#63c74d",
    "red": "#e43b44",
    "blue": "#4fa4b8",
    "floor_a": "#755f4a",
    "floor_b": "#6a5545",
    "wall": "#3e3546",
    "wall_light": "#54475e",
    "dirt": "#2f251d",
}


st.set_page_config(
    page_title="AI Agent Visualizer",
    page_icon=":robot_face:",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def link(action, **params):
    parts = [f"action={action}"]
    parts.extend(f"{key}={value}" for key, value in params.items())
    return "?" + "&".join(parts)


def style_rect(x, y, w, h, fill, outline="", width=0, extra=""):
    border = f"border:{width}px solid {outline};" if outline and width else ""
    return (
        f"left:{x}px;top:{y}px;width:{w}px;height:{h}px;"
        f"background:{fill};{border}{extra}"
    )


def text_div(x, y, text, size, color, weight="400", anchor="nw", width=None):
    transform = ""
    if anchor == "center":
        transform = "transform:translate(-50%,-50%);"
    elif anchor == "w":
        transform = "transform:translateY(-50%);"
    elif anchor == "e":
        transform = "transform:translate(-100%,-50%);"
    style = (
        f"left:{x}px;top:{y}px;{transform}font-size:{size}px;"
        f"color:{color};font-weight:{weight};"
    )
    if width:
        style += f"width:{width}px;"
    return f'<div class="txt" style="{style}">{escape(str(text))}</div>'


def pixel_button(x, y, w, h, text, href, active=False):
    fill = COLORS["accent"] if active else COLORS["panel"]
    shadow = COLORS["accent_dark"] if active else COLORS["panel_dark"]
    color = COLORS["bg"] if active else COLORS["text"]
    return f"""
    <div class="shape" style="{style_rect(x + 4, y + 5, w, h, shadow)}"></div>
    <a class="pixel-button" href="{href}" style="{style_rect(x, y, w, h, fill, COLORS["line"], 3)}">
      <span style="color:{color};">{escape(text)}</span>
    </a>
    """


def compact_state_text(state):
    if state is None:
        return "-"
    if isinstance(state, tuple) and len(state) == 9:
        values = ["_" if value == 0 else str(value) for value in state]
        return "".join(values[0:3]) + "/" + "".join(values[3:6]) + "/" + "".join(values[6:9])
    return str(state)


def neighbor_indexes(index):
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
        choices = neighbor_indexes(empty)
        if previous in choices and len(choices) > 1:
            choices.remove(previous)
        next_empty = random.choice(choices)
        board[empty], board[next_empty] = board[next_empty], board[empty]
        previous = empty
        empty = next_empty
    return board


def make_dirt():
    spots = []
    for _ in range(72):
        spots.append(
            {
                "x": random.randint(MAIN_PANEL_X + 30, MAIN_PANEL_X + BOARD_SIZE - 30),
                "y": random.randint(MAIN_PANEL_Y + 30, MAIN_PANEL_Y + BOARD_SIZE - 30),
                "size": random.choice([5, 6, 7, 8]),
                "clean": False,
            }
        )
    return spots


def ensure_state():
    defaults = {
        "active_screen": "8-puzzle",
        "selected_algorithm": "bfs1",
        "algorithm_expanded": False,
        "puzzle_board": shuffle_puzzle,
        "puzzle_moves": 0,
        "puzzle_message": "Da tron puzzle. Hay dua ve 1..8.",
        "puzzle_search_steps": list,
        "puzzle_search_step_index": 0,
        "puzzle_pending_solution_path": list,
        "puzzle_solution_path": list,
        "puzzle_solution_index": 0,
        "puzzle_start_board_before_search": list,
        "vacuum_robot_x": MAIN_PANEL_X + BOARD_SIZE / 2,
        "vacuum_robot_y": MAIN_PANEL_Y + BOARD_SIZE / 2,
        "vacuum_target_x": None,
        "vacuum_target_y": None,
        "vacuum_auto_path": list,
        "vacuum_auto_path_index": 0,
        "vacuum_pending_auto_path": list,
        "vacuum_auto_clean_enabled": False,
        "vacuum_auto_clean_algorithm": "bfs1",
        "vacuum_search_steps": list,
        "vacuum_search_step_index": 0,
        "vacuum_message": "Chon thuat toan roi bam Apply de robot tim bui gan nhat.",
        "vacuum_dirt": make_dirt,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value() if callable(value) else value


def reset_puzzle():
    st.session_state.puzzle_board = shuffle_puzzle()
    st.session_state.puzzle_moves = 0
    st.session_state.puzzle_search_steps = []
    st.session_state.puzzle_search_step_index = 0
    st.session_state.puzzle_pending_solution_path = []
    st.session_state.puzzle_solution_path = []
    st.session_state.puzzle_solution_index = 0
    st.session_state.puzzle_message = "Da tron puzzle. Hay dua ve 1..8."


def move_puzzle_tile(index):
    board = st.session_state.puzzle_board
    empty = board.index(0)
    if index not in neighbor_indexes(empty):
        st.session_state.puzzle_message = "Tile nay khong sat o trong."
        return
    board[empty], board[index] = board[index], board[empty]
    st.session_state.puzzle_moves += 1
    st.session_state.puzzle_search_steps = []
    st.session_state.puzzle_solution_path = []
    st.session_state.puzzle_pending_solution_path = []
    st.session_state.puzzle_message = "Tot. Tiep tuc nao."
    if board == GOAL_PUZZLE:
        st.session_state.puzzle_message = "Hoan thanh puzzle!"


def apply_puzzle_algorithm():
    algorithm = st.session_state.selected_algorithm
    st.session_state.puzzle_message = f"Dang chay {algorithm.upper()}..."
    st.session_state.puzzle_start_board_before_search = st.session_state.puzzle_board.copy()
    st.session_state.puzzle_solution_path = []
    st.session_state.puzzle_pending_solution_path = []
    steps = run_puzzle_search(algorithm, st.session_state.puzzle_board)
    final_step = steps[-1] if steps else None
    st.session_state.puzzle_search_steps = steps
    st.session_state.puzzle_search_step_index = 0
    if final_step is None or not final_step.found or final_step.path is None:
        detail = final_step.message if final_step else "Khong co step nao."
        st.session_state.puzzle_message = f"{algorithm.upper()} chua tim thay. {detail}"
        return
    st.session_state.puzzle_pending_solution_path = [list(state) for state in final_step.path]
    st.session_state.puzzle_message = f"{algorithm.upper()} dang hien thi cach tim goal..."


def clean_near_robot():
    radius = 27
    rx = st.session_state.vacuum_robot_x
    ry = st.session_state.vacuum_robot_y
    for spot in st.session_state.vacuum_dirt:
        if spot["clean"]:
            continue
        distance = ((rx - spot["x"]) ** 2 + (ry - spot["y"]) ** 2) ** 0.5
        if distance < radius + spot["size"]:
            spot["clean"] = True


def clean_grid_cell(cell):
    for spot in st.session_state.vacuum_dirt:
        if spot["clean"]:
            continue
        spot_cell_x = int((spot["x"] - MAIN_PANEL_X) // 34)
        spot_cell_y = int((spot["y"] - MAIN_PANEL_Y) // 34)
        if (spot_cell_x, spot_cell_y) == cell:
            spot["clean"] = True


def reset_vacuum():
    st.session_state.vacuum_robot_x = MAIN_PANEL_X + BOARD_SIZE / 2
    st.session_state.vacuum_robot_y = MAIN_PANEL_Y + BOARD_SIZE / 2
    st.session_state.vacuum_target_x = None
    st.session_state.vacuum_target_y = None
    st.session_state.vacuum_auto_path = []
    st.session_state.vacuum_auto_path_index = 0
    st.session_state.vacuum_pending_auto_path = []
    st.session_state.vacuum_auto_clean_enabled = False
    st.session_state.vacuum_auto_clean_algorithm = "bfs1"
    st.session_state.vacuum_search_steps = []
    st.session_state.vacuum_search_step_index = 0
    st.session_state.vacuum_message = "Chon thuat toan roi bam Apply de robot tim bui gan nhat."
    st.session_state.vacuum_dirt = make_dirt()


def plan_next_dirty_area():
    algorithm = st.session_state.vacuum_auto_clean_algorithm
    steps = run_vacuum_search(
        algorithm,
        st.session_state.vacuum_robot_x,
        st.session_state.vacuum_robot_y,
        st.session_state.vacuum_dirt,
        MAIN_PANEL_X,
        MAIN_PANEL_Y,
        BOARD_SIZE,
        BOARD_SIZE,
        34,
    )
    final_step = steps[-1] if steps else None
    st.session_state.vacuum_search_steps = steps
    st.session_state.vacuum_search_step_index = 0
    st.session_state.vacuum_auto_path = []
    st.session_state.vacuum_pending_auto_path = []
    if final_step is None or not final_step.found or final_step.path is None:
        detail = final_step.message if final_step else "Khong con bui."
        st.session_state.vacuum_auto_clean_enabled = False
        st.session_state.vacuum_message = f"Da hoan tat hoac dung lai. {detail}"
        return
    st.session_state.vacuum_pending_auto_path = [
        grid_to_point(cell, MAIN_PANEL_X, MAIN_PANEL_Y, 34) for cell in final_step.path[1:]
    ]
    if not st.session_state.vacuum_pending_auto_path:
        clean_grid_cell(final_step.path[-1])
        st.session_state.vacuum_search_steps = []
        if any(not spot["clean"] for spot in st.session_state.vacuum_dirt):
            st.session_state.vacuum_message = "Dang o ngay tren bui. Tiep tuc tim khu tiep theo..."
            plan_next_dirty_area()
        else:
            st.session_state.vacuum_auto_clean_enabled = False
            st.session_state.vacuum_message = "Da don sach phong."
        return
    st.session_state.vacuum_target_x = None
    st.session_state.vacuum_target_y = None
    st.session_state.vacuum_message = f"{algorithm.upper()} dang hien thi cach tim bui..."


def apply_vacuum_algorithm():
    st.session_state.vacuum_auto_clean_enabled = True
    st.session_state.vacuum_auto_clean_algorithm = st.session_state.selected_algorithm
    plan_next_dirty_area()


def set_vacuum_target(x, y):
    if MAIN_PANEL_X <= x <= MAIN_PANEL_X + BOARD_SIZE and MAIN_PANEL_Y <= y <= MAIN_PANEL_Y + BOARD_SIZE:
        st.session_state.vacuum_target_x = x
        st.session_state.vacuum_target_y = y
        st.session_state.vacuum_auto_path = []
        st.session_state.vacuum_auto_clean_enabled = False
        st.session_state.vacuum_search_steps = []


def handle_query():
    action = st.query_params.get("action")
    if not action:
        return

    if action == "screen":
        st.session_state.active_screen = st.query_params.get("screen", "8-puzzle")
    elif action == "toggle_alg":
        st.session_state.algorithm_expanded = not st.session_state.algorithm_expanded
    elif action == "alg":
        algorithm = st.query_params.get("value", "bfs1")
        if algorithm in ALGORITHMS:
            st.session_state.selected_algorithm = algorithm
        st.session_state.algorithm_expanded = False
    elif action == "apply":
        if st.session_state.active_screen == "8-puzzle":
            apply_puzzle_algorithm()
        else:
            apply_vacuum_algorithm()
    elif action == "tile":
        try:
            move_puzzle_tile(int(st.query_params.get("index", "-1")))
        except ValueError:
            pass
    elif action == "shuffle":
        reset_puzzle()
    elif action == "reset_vacuum":
        reset_vacuum()
    elif action == "room":
        try:
            set_vacuum_target(float(st.query_params.get("x")), float(st.query_params.get("y")))
        except (TypeError, ValueError):
            pass

    st.query_params.clear()
    st.rerun()


def tick_puzzle():
    steps = st.session_state.puzzle_search_steps
    if steps:
        index = min(st.session_state.puzzle_search_step_index, len(steps) - 1)
        step = steps[index]
        if isinstance(step.current_state, tuple) and len(step.current_state) == 9:
            st.session_state.puzzle_board = list(step.current_state)
        st.session_state.puzzle_search_step_index += 1
        if st.session_state.puzzle_search_step_index >= len(steps):
            found = steps[-1].found
            st.session_state.puzzle_search_steps = []
            st.session_state.puzzle_search_step_index = 0
            if found and st.session_state.puzzle_pending_solution_path:
                st.session_state.puzzle_board = st.session_state.puzzle_start_board_before_search.copy()
                st.session_state.puzzle_solution_path = st.session_state.puzzle_pending_solution_path
                st.session_state.puzzle_pending_solution_path = []
                st.session_state.puzzle_solution_index = 0
                st.session_state.puzzle_message = "Da tim goal. Bat dau animate dap an di chuyen."
        return

    solution = st.session_state.puzzle_solution_path
    if solution:
        index = st.session_state.puzzle_solution_index
        if index < len(solution):
            st.session_state.puzzle_board = solution[index].copy()
            st.session_state.puzzle_solution_index += 1
        if st.session_state.puzzle_solution_index >= len(solution):
            st.session_state.puzzle_solution_path = []
            st.session_state.puzzle_solution_index = 0
            st.session_state.puzzle_message = "Da ap dung xong loi giai."


def tick_vacuum():
    steps = st.session_state.vacuum_search_steps
    if steps:
        st.session_state.vacuum_search_step_index += 1
        if st.session_state.vacuum_search_step_index >= len(steps):
            found = steps[-1].found
            st.session_state.vacuum_search_steps = []
            st.session_state.vacuum_search_step_index = 0
            if found and st.session_state.vacuum_pending_auto_path:
                st.session_state.vacuum_auto_path = st.session_state.vacuum_pending_auto_path
                st.session_state.vacuum_pending_auto_path = []
                st.session_state.vacuum_auto_path_index = 0
                st.session_state.vacuum_message = f"Da tim goal. Robot bat dau di {len(st.session_state.vacuum_auto_path)} cell."
        return

    path = st.session_state.vacuum_auto_path
    if path:
        index = st.session_state.vacuum_auto_path_index
        if index < len(path):
            st.session_state.vacuum_robot_x, st.session_state.vacuum_robot_y = path[index]
            st.session_state.vacuum_auto_path_index += 1
            clean_near_robot()
        if st.session_state.vacuum_auto_path_index >= len(path):
            st.session_state.vacuum_auto_path = []
            st.session_state.vacuum_auto_path_index = 0
            if st.session_state.vacuum_auto_clean_enabled:
                st.session_state.vacuum_message = "Da don mot khu vuc. Dang tim khu tiep theo..."
                plan_next_dirty_area()
            else:
                st.session_state.vacuum_message = "Da di xong duong tim duoc."
        return

    tx = st.session_state.vacuum_target_x
    ty = st.session_state.vacuum_target_y
    if tx is None or ty is None:
        return
    rx = st.session_state.vacuum_robot_x
    ry = st.session_state.vacuum_robot_y
    speed = 18
    diff_x = tx - rx
    diff_y = ty - ry
    distance = (diff_x**2 + diff_y**2) ** 0.5
    if distance <= speed:
        st.session_state.vacuum_robot_x = tx
        st.session_state.vacuum_robot_y = ty
        st.session_state.vacuum_target_x = None
        st.session_state.vacuum_target_y = None
        clean_near_robot()
        return
    st.session_state.vacuum_robot_x = rx + speed * diff_x / distance
    st.session_state.vacuum_robot_y = ry + speed * diff_y / distance
    clean_near_robot()


def needs_tick():
    return bool(
        st.session_state.puzzle_search_steps
        or st.session_state.puzzle_solution_path
        or st.session_state.vacuum_search_steps
        or st.session_state.vacuum_auto_path
        or st.session_state.vacuum_target_x is not None
    )


def auto_refresh():
    if needs_tick():
        components.html(
            "<script>setTimeout(() => window.parent.location.reload(), 170);</script>",
            height=0,
        )


def current_step(prefix):
    steps = st.session_state[f"{prefix}_search_steps"]
    if not steps:
        return None
    index = min(st.session_state[f"{prefix}_search_step_index"], len(steps) - 1)
    return steps[index]


def draw_puzzle_state(state, x, y, cell=24):
    if state is None or not (isinstance(state, tuple) and len(state) == 9):
        return text_div(x, y, "-", 11, COLORS["muted"])
    html = []
    for index, value in enumerate(state):
        row = index // 3
        col = index % 3
        px = x + col * cell
        py = y + row * cell
        fill = COLORS["bg"] if value == 0 else COLORS["accent"]
        html.append(f'<div class="shape" style="{style_rect(px, py, cell - 3, cell - 3, fill, COLORS["line"], 2)}"></div>')
        if value:
            html.append(text_div(px + cell / 2 - 2, py + cell / 2 - 2, value, 10, COLORS["bg"], "700", "center"))
    return "".join(html)


def draw_trace_column(title, values, x, y, w, current=False):
    html = [
        f'<div class="shape" style="{style_rect(x, y, w, TRACE_PANEL_H - 64, COLORS["panel_dark"], COLORS["line"], 3)}"></div>',
        text_div(x + w / 2, y + 20, title, 10, COLORS["accent"], "700", "center"),
    ]
    if current:
        if isinstance(values, tuple) and len(values) == 9:
            html.append(draw_puzzle_state(values, x + 24, y + 52, 28))
        else:
            html.append(text_div(x + w / 2, y + 86, compact_state_text(values), 12, COLORS["text"], "700", "center"))
        return "".join(html)

    shown = values[:8]
    html.append(text_div(x + 10, y + 48, f"count: {len(values)}", 9, COLORS["muted"], anchor="w"))
    for index, state in enumerate(shown):
        html.append(text_div(x + 10, y + 78 + index * 27, compact_state_text(state), 8, COLORS["text"], anchor="w"))
    if len(values) > len(shown):
        html.append(text_div(x + 10, y + 78 + len(shown) * 27, "...", 9, COLORS["muted"], anchor="w"))
    return "".join(html)


def draw_trace_panel(step, message, step_index, total_steps):
    x = INFO_PANEL_X
    y = INFO_PANEL_Y
    col_w = 116
    gap = 6
    current_state = step.current_state if step else None
    frontier = step.frontier if step else []
    reached = step.visited if step else []
    html = [
        f'<div class="shape" style="{style_rect(x, y, TRACE_PANEL_W, TRACE_PANEL_H, COLORS["panel"], COLORS["line"], 4)}"></div>',
        text_div(x + 18, y + 26, "Search Trace", 18, COLORS["text"], "700", "w"),
        text_div(x + TRACE_PANEL_W - 18, y + 27, f"{step_index}/{total_steps}", 11, COLORS["accent"], "700", "e"),
    ]
    col_y = y + 54
    html.append(draw_trace_column("DANG XET", current_state, x + 10, col_y, col_w, current=True))
    html.append(draw_trace_column("FRONTIER", frontier, x + 10 + col_w + gap, col_y, col_w))
    html.append(draw_trace_column("REACHED", reached, x + 10 + (col_w + gap) * 2, col_y, col_w))
    html.append(text_div(x + 18, y + TRACE_PANEL_H - 42, message, 9, COLORS["muted"], width=TRACE_PANEL_W - 36))
    return "".join(html)


def draw_background():
    html = [f'<div class="shape" style="{style_rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, COLORS["bg"])}"></div>']
    for x in range(0, WINDOW_WIDTH, 22):
        html.append(f'<div class="shape" style="left:{x}px;top:{TOP_BAR_HEIGHT}px;width:1px;height:{WINDOW_HEIGHT - TOP_BAR_HEIGHT}px;background:#1f1a31;"></div>')
    for y in range(TOP_BAR_HEIGHT, WINDOW_HEIGHT, 22):
        html.append(f'<div class="shape" style="left:0;top:{y}px;width:{WINDOW_WIDTH}px;height:1px;background:#1f1a31;"></div>')
    return "".join(html)


def draw_top_bar():
    active = st.session_state.active_screen
    return f"""
    <div class="shape" style="{style_rect(0, 0, WINDOW_WIDTH, TOP_BAR_HEIGHT, COLORS["panel_dark"], COLORS["line"], 3)}"></div>
    {text_div(34, 36, "AI Agent Visualizer", 20, COLORS["text"], "700", "w")}
    {pixel_button(380, 17, 150, 38, "8-PUZZLE", link("screen", screen="8-puzzle"), active == "8-puzzle")}
    {pixel_button(548, 17, 170, 38, "VACUUM", link("screen", screen="vacuum"), active == "vacuum")}
    """


def draw_algorithm_panel():
    x = 18
    y = 96
    w = 166
    selected = st.session_state.selected_algorithm
    html = [
        f'<div class="shape" style="{style_rect(x, y, w, 410, COLORS["panel"], COLORS["line"], 4)}"></div>',
        text_div(x + 18, y + 30, "Thuat toan", 15, COLORS["text"], "700", "w"),
        f'<a class="select-box" href="{link("toggle_alg")}" style="{style_rect(x + 18, y + 54, 130, 34, COLORS["panel_dark"], COLORS["line"], 3)}"></a>',
        text_div(x + 30, y + 71, selected.upper(), 13, COLORS["accent"], "700", "w"),
        text_div(x + 131, y + 71, "v" if not st.session_state.algorithm_expanded else "^", 14, COLORS["text"], "700", "center"),
    ]
    if st.session_state.algorithm_expanded:
        for index, option in enumerate(ALGORITHMS):
            oy = y + 94 + index * 34
            active = option == selected
            fill = COLORS["accent"] if active else COLORS["panel_dark"]
            color = COLORS["bg"] if active else COLORS["text"]
            html.append(f'<a class="select-box" href="{link("alg", value=option)}" style="{style_rect(x + 18, oy, 130, 30, fill, COLORS["line"], 2)}"></a>')
            html.append(text_div(x + 30, oy + 15, option.upper(), 12, color, "700", "w"))
    html.append(pixel_button(x + 18, y + 328, 130, 40, "APPLY", link("apply")))
    html.append(text_div(x + 18, y + 384, "Bam de ap dung", 10, COLORS["muted"], anchor="w"))
    return "".join(html)


def draw_empty_pixels(x, y, size):
    html = []
    for px in range(0, size, 22):
        for py in range(0, size, 22):
            if (px + py) % 44 == 0:
                html.append(f'<div class="shape" style="{style_rect(x + px + 8, y + py + 8, 6, 6, COLORS["panel"])}"></div>')
    return "".join(html)


def draw_puzzle_tile(x, y, size, value, index):
    href = link("tile", index=index)
    return f"""
    <div class="shape" style="{style_rect(x + 5, y + 7, size, size, COLORS["accent_dark"])}"></div>
    <a class="tile-hit" href="{href}" style="{style_rect(x, y, size, size, COLORS["accent"], "#ffd98a", 4)}"></a>
    {text_div(x + size / 2, y + size / 2, value, 48, COLORS["bg"], "700", "center")}
    """


def draw_puzzle_view():
    board = st.session_state.puzzle_board
    start_x = MAIN_PANEL_X
    start_y = MAIN_PANEL_Y
    html = [
        text_div(LEFT_PANEL_WIDTH + 34, 112, "8-Puzzle", 30, COLORS["text"], "700", "w"),
        text_div(LEFT_PANEL_WIDTH + 36, 150, "Choi bang chuot. Logic tim kiem BFS/DFS se gan vao day o buoc tiep theo.", 13, COLORS["muted"], "400", "w"),
        f'<div class="shape" style="{style_rect(start_x - 22, start_y - 22, BOARD_SIZE + 44, BOARD_SIZE + 44, COLORS["panel_dark"], COLORS["line"], 4)}"></div>',
    ]
    for index, value in enumerate(board):
        row = index // 3
        col = index % 3
        x = start_x + col * (BOARD_TILE_SIZE + BOARD_GAP)
        y = start_y + row * (BOARD_TILE_SIZE + BOARD_GAP)
        if value == 0:
            html.append(f'<div class="shape" style="{style_rect(x, y, BOARD_TILE_SIZE, BOARD_TILE_SIZE, COLORS["bg"], COLORS["line"], 3)}"></div>')
            html.append(draw_empty_pixels(x, y, BOARD_TILE_SIZE))
        else:
            html.append(draw_puzzle_tile(x, y, BOARD_TILE_SIZE, value, index))

    step = current_step("puzzle")
    total = len(st.session_state.puzzle_search_steps)
    step_no = min(st.session_state.puzzle_search_step_index + 1, total) if total else 0
    html.append(draw_trace_panel(step, st.session_state.puzzle_message, step_no, total))
    x = INFO_PANEL_X
    y = INFO_PANEL_Y + TRACE_PANEL_H + 18
    html.append(text_div(x + 4, y + 4, f"So buoc choi: {st.session_state.puzzle_moves}", 12, COLORS["accent"], "700", "w"))
    html.append(text_div(x + 4, y + 32, "Goal: 123/456/78_", 10, COLORS["muted"], anchor="w"))
    html.append(pixel_button(x + 214, y + 18, 134, 42, "SHUFFLE", link("shuffle")))
    return "".join(html)


def draw_furniture():
    x = MAIN_PANEL_X
    y = MAIN_PANEL_Y
    return f"""
    <div class="shape" style="{style_rect(x + 34, y + 40, 124, 56, "#5a3f3a", "#33272d", 4)}"></div>
    <div class="shape" style="{style_rect(x + 50, y + 53, 92, 30, "#7a5045")}"></div>
    <div class="shape" style="{style_rect(x + 292, y + 42, 88, 102, "#34405f", "#20283e", 4)}"></div>
    <div class="shape" style="{style_rect(x + 310, y + 60, 52, 66, "#4b5f8c")}"></div>
    <div class="shape" style="{style_rect(x + 62, y + 282, 126, 92, "#3f5a4f", "#263c35", 4)}"></div>
    <div class="shape" style="{style_rect(x + 86, y + 304, 78, 46, "#5b7a6d")}"></div>
    """


def draw_search_overlay():
    step = current_step("vacuum")
    if step is None:
        return ""
    html = []
    for cell in step.visited[-35:]:
        x, y = grid_to_point(cell, MAIN_PANEL_X, MAIN_PANEL_Y, 34)
        html.append(f'<div class="shape" style="{style_rect(x - 6, y - 6, 12, 12, COLORS["line"])}"></div>')
    for cell in step.frontier[-20:]:
        x, y = grid_to_point(cell, MAIN_PANEL_X, MAIN_PANEL_Y, 34)
        html.append(f'<div class="shape" style="{style_rect(x - 7, y - 7, 14, 14, COLORS["accent"])}"></div>')
    if step.current_state is not None:
        x, y = grid_to_point(step.current_state, MAIN_PANEL_X, MAIN_PANEL_Y, 34)
        html.append(f'<div class="shape" style="left:{x - 10}px;top:{y - 10}px;width:20px;height:20px;background:transparent;border:3px solid {COLORS["green"]};"></div>')
    return "".join(html)


def draw_auto_path():
    path = st.session_state.vacuum_auto_path
    if not path:
        return ""
    points = [(st.session_state.vacuum_robot_x, st.session_state.vacuum_robot_y)] + path[st.session_state.vacuum_auto_path_index :]
    html = []
    for x, y in points[1:]:
        html.append(f'<div class="shape" style="{style_rect(x - 4, y - 4, 8, 8, COLORS["green"])}"></div>')
    return "".join(html)


def draw_room_click_grid():
    html = []
    tile = 38
    for row in range((BOARD_SIZE // tile) + 1):
        for col in range((BOARD_SIZE // tile) + 1):
            x = MAIN_PANEL_X + col * tile
            y = MAIN_PANEL_Y + row * tile
            w = min(tile, MAIN_PANEL_X + BOARD_SIZE - x)
            h = min(tile, MAIN_PANEL_Y + BOARD_SIZE - y)
            if w > 0 and h > 0:
                html.append(f'<a class="room-hit" href="{link("room", x=x + w / 2, y=y + h / 2)}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;"></a>')
    return "".join(html)


def draw_vacuum_view():
    x = MAIN_PANEL_X
    y = MAIN_PANEL_Y
    tile = 38
    html = [
        text_div(LEFT_PANEL_WIDTH + 34, 112, "May hut bui", 30, COLORS["text"], "700", "w"),
        text_div(LEFT_PANEL_WIDTH + 36, 150, st.session_state.vacuum_message, 13, COLORS["muted"], "400", "w", 720),
        f'<div class="shape" style="{style_rect(x - 16, y - 16, BOARD_SIZE + 32, BOARD_SIZE + 32, COLORS["wall"], COLORS["wall_light"], 6)}"></div>',
    ]
    for row in range((BOARD_SIZE // tile) + 1):
        for col in range((BOARD_SIZE // tile) + 1):
            fill = COLORS["floor_a"] if (row + col) % 2 == 0 else COLORS["floor_b"]
            px = x + col * tile
            py = y + row * tile
            html.append(f'<div class="shape" style="{style_rect(px, py, min(tile, x + BOARD_SIZE - px), min(tile, y + BOARD_SIZE - py), fill, "#5f4a3e", 1)}"></div>')
    html.append(draw_furniture())
    html.append(draw_search_overlay())
    html.append(draw_auto_path())
    for spot in st.session_state.vacuum_dirt:
        if not spot["clean"]:
            size = spot["size"]
            html.append(f'<div class="shape" style="{style_rect(spot["x"] - size, spot["y"] - size, size * 2, size * 2, COLORS["dirt"])}"></div>')
    if st.session_state.vacuum_target_x is not None:
        tx = st.session_state.vacuum_target_x
        ty = st.session_state.vacuum_target_y
        html.append(f'<div class="shape" style="left:{tx - 9}px;top:{ty - 9}px;width:18px;height:18px;background:transparent;border:3px solid {COLORS["green"]};"></div>')

    rx = st.session_state.vacuum_robot_x
    ry = st.session_state.vacuum_robot_y
    r = 27
    html.extend(
        [
            f'<div class="oval" style="{style_rect(rx - r + 5, ry - r + 7, r * 2, r * 2, "#262030")}"></div>',
            f'<div class="oval" style="{style_rect(rx - r, ry - r, r * 2, r * 2, COLORS["blue"], "#d7f6ff", 4)}"></div>',
            f'<div class="oval" style="{style_rect(rx - 10, ry - 10, 20, 20, "#1d4d5a", "#d7f6ff", 2)}"></div>',
            f'<div class="shape" style="{style_rect(rx - 6, ry - r - 6, 12, 13, COLORS["red"])}"></div>',
            draw_room_click_grid(),
        ]
    )

    step = current_step("vacuum")
    total = len(st.session_state.vacuum_search_steps)
    step_no = min(st.session_state.vacuum_search_step_index + 1, total) if total else 0
    html.append(draw_trace_panel(step, st.session_state.vacuum_message, step_no, total))
    y2 = INFO_PANEL_Y + TRACE_PANEL_H + 18
    cleaned = sum(1 for spot in st.session_state.vacuum_dirt if spot["clean"])
    total_dirt = len(st.session_state.vacuum_dirt)
    html.append(text_div(INFO_PANEL_X + 4, y2 + 4, f"Da don: {cleaned}/{total_dirt}", 12, COLORS["accent"], "700", "w"))
    html.append(text_div(INFO_PANEL_X + 4, y2 + 32, "Manual: W A S D / click room", 10, COLORS["muted"], anchor="w"))
    html.append(pixel_button(INFO_PANEL_X + 214, y2 + 18, 134, 42, "RESET", link("reset_vacuum")))
    return "".join(html)


def draw_app():
    body = [
        draw_background(),
        draw_top_bar(),
        draw_algorithm_panel(),
        draw_puzzle_view() if st.session_state.active_screen == "8-puzzle" else draw_vacuum_view(),
    ]
    st.markdown(
        f"""
        <style>
          .stApp {{
            background:{COLORS["bg"]};
          }}
          .block-container {{
            padding: 0 !important;
            max-width: none !important;
          }}
          header, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {{
            display: none !important;
          }}
          .app-canvas {{
            position: relative;
            width: {WINDOW_WIDTH}px;
            height: {WINDOW_HEIGHT}px;
            margin: 0;
            overflow: hidden;
            font-family: Consolas, "Courier New", monospace;
          }}
          .shape, .txt, .pixel-button, .select-box, .tile-hit, .room-hit, .oval {{
            position: absolute;
            box-sizing: border-box;
          }}
          .txt {{
            line-height: 1.15;
            white-space: pre-wrap;
            pointer-events: none;
            z-index: 5;
          }}
          .pixel-button {{
            display: grid;
            place-items: center;
            text-decoration: none;
            z-index: 8;
          }}
          .pixel-button span {{
            font-size: 16px;
            font-weight: 700;
          }}
          .select-box, .tile-hit, .room-hit {{
            display: block;
            text-decoration: none;
            z-index: 7;
          }}
          .tile-hit:hover, .pixel-button:hover {{
            filter: brightness(1.07);
          }}
          .room-hit {{
            background: transparent;
          }}
          .oval {{
            border-radius: 50%;
          }}
        </style>
        <div class="app-canvas">{"".join(body)}</div>
        """,
        unsafe_allow_html=True,
    )


ensure_state()
handle_query()

if needs_tick():
    if st.session_state.active_screen == "8-puzzle":
        tick_puzzle()
    else:
        tick_vacuum()

draw_app()
auto_refresh()
