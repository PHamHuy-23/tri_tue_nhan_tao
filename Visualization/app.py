import random
import tkinter as tk
from tkinter import font

from search_adapters import grid_to_point, run_puzzle_search, run_vacuum_search


WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 720
TOP_BAR_HEIGHT = 74
FPS_MS = 16
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


class PixelButton:
    def __init__(self, canvas, x, y, w, h, text, command, active=False):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.command = command
        self.active = active
        self.items = []

    def draw(self):
        fill = COLORS["accent"] if self.active else COLORS["panel"]
        shadow = COLORS["accent_dark"] if self.active else COLORS["panel_dark"]
        self.items = [
            self.canvas.create_rectangle(
                self.x + 4,
                self.y + 5,
                self.x + self.w + 4,
                self.y + self.h + 5,
                fill=shadow,
                outline="",
            ),
            self.canvas.create_rectangle(
                self.x,
                self.y,
                self.x + self.w,
                self.y + self.h,
                fill=fill,
                outline=COLORS["line"],
                width=3,
            ),
            self.canvas.create_text(
                self.x + self.w / 2,
                self.y + self.h / 2,
                text=self.text,
                fill=COLORS["bg"] if self.active else COLORS["text"],
                font=("Consolas", 16, "bold"),
            ),
        ]
        for item in self.items:
            self.canvas.tag_bind(item, "<Button-1>", self.on_click)

    def on_click(self, _event):
        self.command()


class AlgorithmPanel:
    def __init__(self, app):
        self.app = app
        self.canvas = app.canvas
        self.x = 18
        self.y = 96
        self.w = 166
        self.expanded = False
        self.options = ["bfs1", "bfs2", "dfs1", "dfs2"]

    def draw(self):
        self.canvas.create_rectangle(
            self.x,
            self.y,
            self.x + self.w,
            self.y + 410,
            fill=COLORS["panel"],
            outline=COLORS["line"],
            width=4,
        )
        self.canvas.create_text(
            self.x + 18,
            self.y + 30,
            anchor="w",
            text="Thuat toan",
            fill=COLORS["text"],
            font=("Consolas", 15, "bold"),
        )
        self.draw_select_box()

        if self.expanded:
            for index, option in enumerate(self.options):
                self.draw_option(option, self.x + 18, self.y + 94 + index * 34)

        apply_button = PixelButton(
            self.canvas,
            self.x + 18,
            self.y + 328,
            130,
            40,
            "APPLY",
            self.app.apply_algorithm,
        )
        apply_button.draw()

        self.canvas.create_text(
            self.x + 18,
            self.y + 384,
            anchor="w",
            text="Bam de ap dung",
            fill=COLORS["muted"],
            font=("Consolas", 10),
        )

    def draw_select_box(self):
        x = self.x + 18
        y = self.y + 54
        item = self.canvas.create_rectangle(
            x,
            y,
            x + 130,
            y + 34,
            fill=COLORS["panel_dark"],
            outline=COLORS["line"],
            width=3,
        )
        text = self.canvas.create_text(
            x + 12,
            y + 17,
            anchor="w",
            text=self.app.selected_algorithm.upper(),
            fill=COLORS["accent"],
            font=("Consolas", 13, "bold"),
        )
        arrow = self.canvas.create_text(
            x + 113,
            y + 17,
            text="v" if not self.expanded else "^",
            fill=COLORS["text"],
            font=("Consolas", 14, "bold"),
        )

        for canvas_item in (item, text, arrow):
            self.canvas.tag_bind(canvas_item, "<Button-1>", self.toggle)

    def draw_option(self, option, x, y):
        active = option == self.app.selected_algorithm
        fill = COLORS["accent"] if active else COLORS["panel_dark"]
        item = self.canvas.create_rectangle(x, y, x + 130, y + 30, fill=fill, outline=COLORS["line"], width=2)
        text = self.canvas.create_text(
            x + 12,
            y + 15,
            anchor="w",
            text=option.upper(),
            fill=COLORS["bg"] if active else COLORS["text"],
            font=("Consolas", 12, "bold"),
        )

        def choose(_event):
            self.app.selected_algorithm = option
            self.expanded = False

        self.canvas.tag_bind(item, "<Button-1>", choose)
        self.canvas.tag_bind(text, "<Button-1>", choose)

    def toggle(self, _event):
        self.expanded = not self.expanded


def compact_state_text(state):
    if state is None:
        return "-"
    if isinstance(state, tuple) and len(state) == 9:
        values = ["_" if value == 0 else str(value) for value in state]
        return "".join(values[0:3]) + "/" + "".join(values[3:6]) + "/" + "".join(values[6:9])
    return str(state)


def draw_puzzle_state(canvas, state, x, y, cell=24):
    if state is None or not (isinstance(state, tuple) and len(state) == 9):
        canvas.create_text(x, y, anchor="nw", text="-", fill=COLORS["muted"], font=("Consolas", 11))
        return

    for index, value in enumerate(state):
        row = index // 3
        col = index % 3
        px = x + col * cell
        py = y + row * cell
        fill = COLORS["bg"] if value == 0 else COLORS["accent"]
        canvas.create_rectangle(px, py, px + cell - 3, py + cell - 3, fill=fill, outline=COLORS["line"], width=2)
        if value:
            canvas.create_text(px + cell / 2 - 2, py + cell / 2 - 2, text=str(value), fill=COLORS["bg"], font=("Consolas", 10, "bold"))


def draw_trace_column(canvas, title, values, x, y, w, current=False):
    canvas.create_rectangle(x, y, x + w, y + TRACE_PANEL_H - 64, fill=COLORS["panel_dark"], outline=COLORS["line"], width=3)
    canvas.create_text(x + w / 2, y + 20, text=title, fill=COLORS["accent"], font=("Consolas", 10, "bold"))

    if current:
        if isinstance(values, tuple) and len(values) == 9:
            draw_puzzle_state(canvas, values, x + 24, y + 52, cell=28)
        else:
            canvas.create_text(x + w / 2, y + 86, text=compact_state_text(values), fill=COLORS["text"], font=("Consolas", 12, "bold"))
        return

    shown = values[:8]
    canvas.create_text(x + 10, y + 48, anchor="w", text=f"count: {len(values)}", fill=COLORS["muted"], font=("Consolas", 9))
    for index, state in enumerate(shown):
        canvas.create_text(
            x + 10,
            y + 78 + index * 27,
            anchor="w",
            text=compact_state_text(state),
            fill=COLORS["text"],
            font=("Consolas", 8),
        )

    if len(values) > len(shown):
        canvas.create_text(x + 10, y + 78 + len(shown) * 27, anchor="w", text="...", fill=COLORS["muted"], font=("Consolas", 9))


def draw_trace_panel(canvas, step, message, step_index, total_steps):
    x = INFO_PANEL_X
    y = INFO_PANEL_Y
    col_w = 116
    gap = 6

    canvas.create_rectangle(x, y, x + TRACE_PANEL_W, y + TRACE_PANEL_H, fill=COLORS["panel"], outline=COLORS["line"], width=4)
    canvas.create_text(x + 18, y + 26, anchor="w", text="Search Trace", fill=COLORS["text"], font=("Consolas", 18, "bold"))
    canvas.create_text(
        x + TRACE_PANEL_W - 18,
        y + 27,
        anchor="e",
        text=f"{step_index}/{total_steps}",
        fill=COLORS["accent"],
        font=("Consolas", 11, "bold"),
    )

    current_state = step.current_state if step else None
    frontier = step.frontier if step else []
    reached = step.visited if step else []

    col_y = y + 54
    draw_trace_column(canvas, "DANG XET", current_state, x + 10, col_y, col_w, current=True)
    draw_trace_column(canvas, "FRONTIER", frontier, x + 10 + col_w + gap, col_y, col_w)
    draw_trace_column(canvas, "REACHED", reached, x + 10 + (col_w + gap) * 2, col_y, col_w)

    canvas.create_text(
        x + 18,
        y + TRACE_PANEL_H - 42,
        anchor="w",
        text=message,
        fill=COLORS["muted"],
        font=("Consolas", 9),
        width=TRACE_PANEL_W - 36,
    )


class EightPuzzleView:
    def __init__(self, app):
        self.app = app
        self.canvas = app.canvas
        self.board = [1, 2, 3, 4, 5, 6, 7, 8, 0]
        self.moves = 0
        self.message = "Click tile sat o trong de di chuyen"
        self.solution_path = []
        self.solution_index = 0
        self.animation_timer = 0
        self.search_steps = []
        self.search_step_index = 0
        self.search_timer = 0
        self.pending_solution_path = []
        self.start_board_before_search = []
        self.shuffle()

    def shuffle(self):
        self.board = [1, 2, 3, 4, 5, 6, 7, 8, 0]
        empty = 8
        previous = None

        for _ in range(8):
            choices = self.neighbor_indexes(empty)
            if previous in choices and len(choices) > 1:
                choices.remove(previous)
            next_empty = random.choice(choices)
            self.board[empty], self.board[next_empty] = self.board[next_empty], self.board[empty]
            previous = empty
            empty = next_empty

        self.moves = 0
        self.solution_path = []
        self.solution_index = 0
        self.search_steps = []
        self.search_step_index = 0
        self.pending_solution_path = []
        self.message = "Da tron puzzle. Hay dua ve 1..8."

    def draw(self):
        self.animate_search()
        self.animate_solution()
        self.draw_header()
        self.draw_board()
        self.draw_side_panel()

    def draw_header(self):
        self.canvas.create_text(
            LEFT_PANEL_WIDTH + 34,
            112,
            anchor="w",
            text="8-Puzzle",
            fill=COLORS["text"],
            font=("Consolas", 30, "bold"),
        )
        self.canvas.create_text(
            LEFT_PANEL_WIDTH + 36,
            150,
            anchor="w",
            text="Choi bang chuot. Logic tim kiem BFS/DFS se gan vao day o buoc tiep theo.",
            fill=COLORS["muted"],
            font=("Consolas", 13),
        )

    def draw_board(self):
        size = BOARD_TILE_SIZE
        gap = BOARD_GAP
        board_size = BOARD_SIZE
        start_x = MAIN_PANEL_X
        start_y = MAIN_PANEL_Y

        self.canvas.create_rectangle(
            start_x - 22,
            start_y - 22,
            start_x + board_size + 22,
            start_y + board_size + 22,
            fill=COLORS["panel_dark"],
            outline=COLORS["line"],
            width=4,
        )

        for index, value in enumerate(self.board):
            row = index // 3
            col = index % 3
            x = start_x + col * (size + gap)
            y = start_y + row * (size + gap)

            if value == 0:
                self.canvas.create_rectangle(
                    x,
                    y,
                    x + size,
                    y + size,
                    fill=COLORS["bg"],
                    outline=COLORS["line"],
                    width=3,
                )
                self.draw_empty_pixels(x, y, size)
            else:
                self.draw_tile(x, y, size, value, index)

    def draw_empty_pixels(self, x, y, size):
        for px in range(0, size, 22):
            for py in range(0, size, 22):
                if (px + py) % 44 == 0:
                    self.canvas.create_rectangle(
                        x + px + 8,
                        y + py + 8,
                        x + px + 14,
                        y + py + 14,
                        fill=COLORS["panel"],
                        outline="",
                    )

    def draw_tile(self, x, y, size, value, index):
        tags = (f"tile_{index}", "puzzle_tile")
        self.canvas.create_rectangle(
            x + 5,
            y + 7,
            x + size + 5,
            y + size + 7,
            fill=COLORS["accent_dark"],
            outline="",
            tags=tags,
        )
        self.canvas.create_rectangle(
            x,
            y,
            x + size,
            y + size,
            fill=COLORS["accent"],
            outline="#ffd98a",
            width=4,
            tags=tags,
        )
        self.canvas.create_text(
            x + size / 2,
            y + size / 2,
            text=str(value),
            fill=COLORS["bg"],
            font=("Consolas", 48, "bold"),
            tags=tags,
        )
        self.canvas.tag_bind(f"tile_{index}", "<Button-1>", lambda _event, i=index: self.move_tile(i))

    def draw_side_panel(self):
        step = self.current_search_step()
        total_steps = len(self.search_steps)
        step_number = min(self.search_step_index + 1, total_steps) if total_steps else 0
        draw_trace_panel(self.canvas, step, self.message, step_number, total_steps)

        x = INFO_PANEL_X
        y = INFO_PANEL_Y + TRACE_PANEL_H + 18
        self.canvas.create_text(x + 4, y + 4, anchor="w", text=f"So buoc choi: {self.moves}", fill=COLORS["accent"], font=("Consolas", 12, "bold"))
        self.canvas.create_text(x + 4, y + 32, anchor="w", text="Goal: 123/456/78_", fill=COLORS["muted"], font=("Consolas", 10))
        button = PixelButton(self.canvas, x + 214, y + 18, 134, 42, "SHUFFLE", self.shuffle)
        button.draw()

    def draw_small_goal(self, x, y):
        self.canvas.create_text(x, y - 22, anchor="w", text="Goal", fill=COLORS["text"], font=("Consolas", 14, "bold"))
        cell = 34
        for i in range(9):
            value = i + 1 if i < 8 else 0
            row = i // 3
            col = i % 3
            px = x + col * cell
            py = y + row * cell
            fill = COLORS["bg"] if value == 0 else COLORS["accent"]
            self.canvas.create_rectangle(px, py, px + cell - 3, py + cell - 3, fill=fill, outline=COLORS["line"], width=2)
            if value:
                self.canvas.create_text(px + cell / 2 - 2, py + cell / 2 - 2, text=str(value), fill=COLORS["bg"], font=("Consolas", 12, "bold"))

    def move_tile(self, index):
        empty = self.board.index(0)
        if index not in self.neighbor_indexes(empty):
            self.message = "Tile nay khong sat o trong."
            return

        self.board[empty], self.board[index] = self.board[index], self.board[empty]
        self.moves += 1
        self.message = "Tot. Tiep tuc nao."

        if self.board == [1, 2, 3, 4, 5, 6, 7, 8, 0]:
            self.message = "Hoan thanh puzzle!"

    def apply_algorithm(self, algorithm_name):
        self.message = f"Dang chay {algorithm_name.upper()}..."
        self.start_board_before_search = self.board.copy()
        self.solution_path = []
        self.pending_solution_path = []
        steps = run_puzzle_search(algorithm_name, self.board)
        final_step = steps[-1] if steps else None
        self.search_steps = steps
        self.search_step_index = 0
        self.search_timer = 0

        if final_step is None or not final_step.found or final_step.path is None:
            detail = final_step.message if final_step else "Khong co step nao."
            self.message = f"{algorithm_name.upper()} chua tim thay. {detail}"
            return

        self.pending_solution_path = [list(state) for state in final_step.path]
        self.message = f"{algorithm_name.upper()} dang hien thi cach tim goal..."

    def current_search_step(self):
        if not self.search_steps:
            return None
        index = min(self.search_step_index, len(self.search_steps) - 1)
        return self.search_steps[index]

    def animate_search(self):
        if not self.search_steps:
            return

        step = self.current_search_step()
        if step and isinstance(step.current_state, tuple) and len(step.current_state) == 9:
            self.board = list(step.current_state)

        self.search_timer += 1
        if self.search_timer < 10:
            return

        self.search_timer = 0
        self.search_step_index += 1
        if self.search_step_index < len(self.search_steps):
            return

        found = self.search_steps[-1].found
        self.search_steps = []
        self.search_step_index = 0
        if found and self.pending_solution_path:
            self.board = self.start_board_before_search.copy()
            self.solution_path = self.pending_solution_path
            self.pending_solution_path = []
            self.solution_index = 0
            self.animation_timer = 0
            self.message = "Da tim goal. Bat dau animate dap an di chuyen."

    def animate_solution(self):
        if self.search_steps or not self.solution_path:
            return

        self.animation_timer += 1
        if self.animation_timer < 18:
            return

        self.animation_timer = 0
        self.board = self.solution_path[self.solution_index].copy()
        self.solution_index += 1

        if self.solution_index >= len(self.solution_path):
            self.solution_path = []
            self.solution_index = 0
            self.message = "Da ap dung xong loi giai."

    def neighbor_indexes(self, index):
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


class VacuumView:
    def __init__(self, app):
        self.app = app
        self.canvas = app.canvas
        self.room_x = MAIN_PANEL_X
        self.room_y = MAIN_PANEL_Y
        self.room_w = BOARD_SIZE
        self.room_h = BOARD_SIZE
        self.cell_size = 34
        self.robot_x = self.room_x + self.room_w / 2
        self.robot_y = self.room_y + self.room_h / 2
        self.robot_radius = 27
        self.speed = 4.4
        self.keys = set()
        self.target_x = None
        self.target_y = None
        self.auto_path = []
        self.auto_path_index = 0
        self.pending_auto_path = []
        self.auto_clean_enabled = False
        self.auto_clean_algorithm = "bfs1"
        self.search_steps = []
        self.search_step_index = 0
        self.search_timer = 0
        self.message = "Chon thuat toan roi bam Apply de robot tim bui gan nhat."
        self.dirt = self.make_dirt()

    def make_dirt(self):
        spots = []
        for _ in range(72):
            spots.append(
                {
                    "x": random.randint(self.room_x + 30, self.room_x + self.room_w - 30),
                    "y": random.randint(self.room_y + 30, self.room_y + self.room_h - 30),
                    "size": random.choice([5, 6, 7, 8]),
                    "clean": False,
                }
            )
        return spots

    def set_key(self, key, pressed):
        if pressed:
            self.keys.add(key.lower())
            self.target_x = None
            self.target_y = None
            self.auto_path = []
            self.auto_clean_enabled = False
            self.search_steps = []
        else:
            self.keys.discard(key.lower())

    def set_mouse_target(self, x, y):
        if not self.is_inside_room(x, y):
            return
        self.target_x = x
        self.target_y = y
        self.auto_path = []
        self.auto_clean_enabled = False
        self.search_steps = []

    def is_inside_room(self, x, y):
        return self.room_x <= x <= self.room_x + self.room_w and self.room_y <= y <= self.room_y + self.room_h

    def step(self):
        self.follow_auto_path()
        dx = 0
        dy = 0
        if "w" in self.keys or "up" in self.keys:
            dy -= self.speed
        if "s" in self.keys or "down" in self.keys:
            dy += self.speed
        if "a" in self.keys or "left" in self.keys:
            dx -= self.speed
        if "d" in self.keys or "right" in self.keys:
            dx += self.speed

        if not self.keys and self.target_x is not None and self.target_y is not None:
            diff_x = self.target_x - self.robot_x
            diff_y = self.target_y - self.robot_y
            distance = (diff_x**2 + diff_y**2) ** 0.5
            if distance <= self.speed:
                self.robot_x = self.target_x
                self.robot_y = self.target_y
                self.target_x = None
                self.target_y = None
                self.clean_near_robot()
                return
            dx = self.speed * diff_x / distance
            dy = self.speed * diff_y / distance

        self.robot_x = max(self.room_x + self.robot_radius, min(self.room_x + self.room_w - self.robot_radius, self.robot_x + dx))
        self.robot_y = max(self.room_y + self.robot_radius, min(self.room_y + self.room_h - self.robot_radius, self.robot_y + dy))
        self.clean_near_robot()

    def follow_auto_path(self):
        if self.search_steps or self.keys or self.target_x is not None or not self.auto_path:
            return

        if self.auto_path_index >= len(self.auto_path):
            self.auto_path = []
            self.auto_path_index = 0
            if self.auto_clean_enabled:
                self.message = "Da don mot khu vuc. Dang tim khu tiep theo..."
                self.plan_next_dirty_area()
            else:
                self.message = "Da di xong duong tim duoc."
            return

        self.target_x, self.target_y = self.auto_path[self.auto_path_index]
        self.auto_path_index += 1

    def clean_near_robot(self):
        for spot in self.dirt:
            if spot["clean"]:
                continue
            distance = ((self.robot_x - spot["x"]) ** 2 + (self.robot_y - spot["y"]) ** 2) ** 0.5
            if distance < self.robot_radius + spot["size"]:
                spot["clean"] = True

    def draw(self):
        self.animate_search()
        self.step()
        self.draw_header()
        self.draw_room()
        self.draw_robot()
        self.draw_control_panel()

    def draw_header(self):
        self.canvas.create_text(
            LEFT_PANEL_WIDTH + 34,
            112,
            anchor="w",
            text="May hut bui",
            fill=COLORS["text"],
            font=("Consolas", 30, "bold"),
        )
        self.canvas.create_text(
            LEFT_PANEL_WIDTH + 36,
            150,
            anchor="w",
            text=self.message,
            fill=COLORS["muted"],
            font=("Consolas", 13),
        )

    def draw_room(self):
        x = self.room_x
        y = self.room_y
        tile = 38

        self.canvas.create_rectangle(x - 16, y - 16, x + self.room_w + 16, y + self.room_h + 16, fill=COLORS["wall"], outline=COLORS["wall_light"], width=6)
        for row in range((self.room_h // tile) + 1):
            for col in range((self.room_w // tile) + 1):
                fill = COLORS["floor_a"] if (row + col) % 2 == 0 else COLORS["floor_b"]
                px = x + col * tile
                py = y + row * tile
                self.canvas.create_rectangle(px, py, min(px + tile, x + self.room_w), min(py + tile, y + self.room_h), fill=fill, outline="#5f4a3e")

        self.draw_furniture()
        self.draw_search_overlay()
        self.draw_auto_path()
        for spot in self.dirt:
            if not spot["clean"]:
                size = spot["size"]
                self.canvas.create_rectangle(spot["x"] - size, spot["y"] - size, spot["x"] + size, spot["y"] + size, fill=COLORS["dirt"], outline="")

        if self.target_x is not None and self.target_y is not None:
            self.canvas.create_rectangle(
                self.target_x - 9,
                self.target_y - 9,
                self.target_x + 9,
                self.target_y + 9,
                fill="",
                outline=COLORS["green"],
                width=3,
            )

    def draw_furniture(self):
        x = self.room_x
        y = self.room_y
        self.canvas.create_rectangle(x + 34, y + 40, x + 158, y + 96, fill="#5a3f3a", outline="#33272d", width=4)
        self.canvas.create_rectangle(x + 50, y + 53, x + 142, y + 83, fill="#7a5045", outline="")
        self.canvas.create_rectangle(x + 292, y + 42, x + 380, y + 144, fill="#34405f", outline="#20283e", width=4)
        self.canvas.create_rectangle(x + 310, y + 60, x + 362, y + 126, fill="#4b5f8c", outline="")
        self.canvas.create_rectangle(x + 62, y + 282, x + 188, y + 374, fill="#3f5a4f", outline="#263c35", width=4)
        self.canvas.create_rectangle(x + 86, y + 304, x + 164, y + 350, fill="#5b7a6d", outline="")

    def draw_auto_path(self):
        if not self.auto_path:
            return

        points = [(self.robot_x, self.robot_y)] + self.auto_path[self.auto_path_index :]
        for index in range(len(points) - 1):
            self.canvas.create_line(
                points[index][0],
                points[index][1],
                points[index + 1][0],
                points[index + 1][1],
                fill=COLORS["green"],
                width=3,
            )
        for x, y in points[1:]:
            self.canvas.create_rectangle(x - 4, y - 4, x + 4, y + 4, fill=COLORS["green"], outline="")

    def draw_search_overlay(self):
        step = self.current_search_step()
        if step is None:
            return

        for cell in step.visited[-35:]:
            x, y = grid_to_point(cell, self.room_x, self.room_y, self.cell_size)
            self.canvas.create_rectangle(x - 6, y - 6, x + 6, y + 6, fill="#3a4466", outline="")

        for cell in step.frontier[-20:]:
            x, y = grid_to_point(cell, self.room_x, self.room_y, self.cell_size)
            self.canvas.create_rectangle(x - 7, y - 7, x + 7, y + 7, fill=COLORS["accent"], outline="")

        if step.current_state is not None:
            x, y = grid_to_point(step.current_state, self.room_x, self.room_y, self.cell_size)
            self.canvas.create_rectangle(x - 10, y - 10, x + 10, y + 10, fill="", outline=COLORS["green"], width=3)

    def draw_robot(self):
        x = self.robot_x
        y = self.robot_y
        r = self.robot_radius

        self.canvas.create_oval(x - r + 5, y - r + 7, x + r + 5, y + r + 7, fill="#262030", outline="")
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=COLORS["blue"], outline="#d7f6ff", width=4)
        self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="#1d4d5a", outline="#d7f6ff", width=2)
        self.canvas.create_rectangle(x - 6, y - r - 6, x + 6, y - r + 7, fill=COLORS["red"], outline="")

    def draw_control_panel(self):
        step = self.current_search_step()
        total_steps = len(self.search_steps)
        step_number = min(self.search_step_index + 1, total_steps) if total_steps else 0
        draw_trace_panel(self.canvas, step, self.message, step_number, total_steps)

        x = INFO_PANEL_X
        y = INFO_PANEL_Y + TRACE_PANEL_H + 18
        cleaned = sum(1 for spot in self.dirt if spot["clean"])
        total = len(self.dirt)

        self.canvas.create_text(x + 4, y + 4, anchor="w", text=f"Da don: {cleaned}/{total}", fill=COLORS["accent"], font=("Consolas", 12, "bold"))
        self.canvas.create_text(x + 4, y + 32, anchor="w", text="Manual: W A S D / click room", fill=COLORS["muted"], font=("Consolas", 10))
        reset = PixelButton(self.canvas, x + 214, y + 18, 134, 42, "RESET", self.reset)
        reset.draw()

    def draw_arrow_button(self, x, y, key, label):
        active = key in self.keys
        fill = COLORS["green"] if active else COLORS["panel_dark"]
        item = self.canvas.create_rectangle(x, y, x + 40, y + 40, fill=fill, outline=COLORS["line"], width=3)
        text = self.canvas.create_text(x + 20, y + 20, text=label, fill=COLORS["text"], font=("Consolas", 18, "bold"))

        def press(_event):
            self.keys.add(key)
            self.target_x = None
            self.target_y = None
            self.auto_path = []
            self.auto_clean_enabled = False

        def release(_event):
            self.keys.discard(key)

        for canvas_item in (item, text):
            self.canvas.tag_bind(canvas_item, "<ButtonPress-1>", press)
            self.canvas.tag_bind(canvas_item, "<ButtonRelease-1>", release)

    def reset(self):
        self.robot_x = self.room_x + self.room_w / 2
        self.robot_y = self.room_y + self.room_h / 2
        self.target_x = None
        self.target_y = None
        self.auto_path = []
        self.auto_path_index = 0
        self.pending_auto_path = []
        self.auto_clean_enabled = False
        self.auto_clean_algorithm = "bfs1"
        self.search_steps = []
        self.search_step_index = 0
        self.message = "Chon thuat toan roi bam Apply de robot tim bui gan nhat."
        self.dirt = self.make_dirt()

    def apply_algorithm(self, algorithm_name):
        self.auto_clean_enabled = True
        self.auto_clean_algorithm = algorithm_name
        self.plan_next_dirty_area()

    def plan_next_dirty_area(self):
        algorithm_name = self.auto_clean_algorithm
        steps = run_vacuum_search(
            algorithm_name,
            self.robot_x,
            self.robot_y,
            self.dirt,
            self.room_x,
            self.room_y,
            self.room_w,
            self.room_h,
            self.cell_size,
        )
        final_step = steps[-1] if steps else None
        self.search_steps = steps
        self.search_step_index = 0
        self.search_timer = 0
        self.auto_path = []
        self.pending_auto_path = []

        if final_step is None or not final_step.found or final_step.path is None:
            detail = final_step.message if final_step else "Khong con bui."
            self.auto_clean_enabled = False
            self.message = f"Da hoan tat hoac dung lai. {detail}"
            return

        self.pending_auto_path = [
            grid_to_point(cell, self.room_x, self.room_y, self.cell_size)
            for cell in final_step.path[1:]
        ]
        if not self.pending_auto_path:
            self.clean_grid_cell(final_step.path[-1])
            self.search_steps = []
            if any(not spot["clean"] for spot in self.dirt):
                self.message = "Dang o ngay tren bui. Tiep tuc tim khu tiep theo..."
                self.plan_next_dirty_area()
            else:
                self.auto_clean_enabled = False
                self.message = "Da don sach phong."
            return

        self.target_x = None
        self.target_y = None
        self.message = f"{algorithm_name.upper()} dang hien thi cach tim bui..."

    def clean_grid_cell(self, cell):
        for spot in self.dirt:
            if spot["clean"]:
                continue
            spot_cell_x = int((spot["x"] - self.room_x) // self.cell_size)
            spot_cell_y = int((spot["y"] - self.room_y) // self.cell_size)
            if (spot_cell_x, spot_cell_y) == cell:
                spot["clean"] = True

    def current_search_step(self):
        if not self.search_steps:
            return None
        index = min(self.search_step_index, len(self.search_steps) - 1)
        return self.search_steps[index]

    def animate_search(self):
        if not self.search_steps:
            return

        self.search_timer += 1
        if self.search_timer < 10:
            return

        self.search_timer = 0
        self.search_step_index += 1
        if self.search_step_index < len(self.search_steps):
            return

        found = self.search_steps[-1].found
        self.search_steps = []
        self.search_step_index = 0
        if found and self.pending_auto_path:
            self.auto_path = self.pending_auto_path
            self.pending_auto_path = []
            self.auto_path_index = 0
            self.message = f"Da tim goal. Robot bat dau di {len(self.auto_path)} cell."


class VisualizationApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Agent Algorithm Visualization")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["bg"])

        self.pixel_font = font.Font(family="Consolas", size=14, weight="bold")
        self.canvas = tk.Canvas(self.root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg=COLORS["bg"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.active_screen = "8-puzzle"
        self.selected_algorithm = "bfs1"
        self.algorithm_panel = AlgorithmPanel(self)
        self.views = {
            "8-puzzle": EightPuzzleView(self),
            "vacuum": VacuumView(self),
        }

        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.root.after(FPS_MS, self.loop)

    def switch_screen(self, screen_name):
        self.active_screen = screen_name

    def loop(self):
        self.canvas.delete("all")
        self.draw_background()
        self.draw_top_bar()
        self.algorithm_panel.draw()
        self.views[self.active_screen].draw()
        self.root.after(FPS_MS, self.loop)

    def draw_background(self):
        self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill=COLORS["bg"], outline="")
        for x in range(0, WINDOW_WIDTH, 22):
            self.canvas.create_line(x, TOP_BAR_HEIGHT, x, WINDOW_HEIGHT, fill="#1f1a31")
        for y in range(TOP_BAR_HEIGHT, WINDOW_HEIGHT, 22):
            self.canvas.create_line(0, y, WINDOW_WIDTH, y, fill="#1f1a31")

    def draw_top_bar(self):
        self.canvas.create_rectangle(0, 0, WINDOW_WIDTH, TOP_BAR_HEIGHT, fill=COLORS["panel_dark"], outline=COLORS["line"], width=3)
        self.canvas.create_text(34, 36, anchor="w", text="AI Agent Visualizer", fill=COLORS["text"], font=("Consolas", 20, "bold"))

        puzzle_button = PixelButton(
            self.canvas,
            380,
            17,
            150,
            38,
            "8-PUZZLE",
            lambda: self.switch_screen("8-puzzle"),
            active=self.active_screen == "8-puzzle",
        )
        puzzle_button.draw()

        vacuum_button = PixelButton(
            self.canvas,
            548,
            17,
            170,
            38,
            "VACUUM",
            lambda: self.switch_screen("vacuum"),
            active=self.active_screen == "vacuum",
        )
        vacuum_button.draw()

    def on_key_press(self, event):
        if self.active_screen != "vacuum":
            return
        key = event.keysym.lower()
        if key in ("w", "a", "s", "d", "up", "down", "left", "right"):
            self.views["vacuum"].set_key(key, True)

    def on_key_release(self, event):
        if self.active_screen != "vacuum":
            return
        key = event.keysym.lower()
        if key in ("w", "a", "s", "d", "up", "down", "left", "right"):
            self.views["vacuum"].set_key(key, False)

    def on_canvas_click(self, event):
        if self.active_screen == "vacuum":
            self.views["vacuum"].set_mouse_target(event.x, event.y)

    def apply_algorithm(self):
        self.views[self.active_screen].apply_algorithm(self.selected_algorithm)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = VisualizationApp()
    app.run()
