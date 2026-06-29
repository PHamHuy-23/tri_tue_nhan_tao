import pygame
import sys
import time
import copy
import random
from solvers import bfs_way_1, bfs_way_2, dfs_way_1, dfs_way_2, ids_way_1, ids_way_2, ucs, get_state_sequence

# Initialize Pygame
pygame.init()

# Window Configuration
WIDTH, HEIGHT = 950, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("8-Puzzle Solver Interactive Visualizer")
clock = pygame.time.Clock()

# Colors
COLOR_BG = (26, 37, 48)          # Dark Slate Blue
COLOR_PANEL_BG = (34, 49, 63)    # Lighter Slate
COLOR_TILE = (41, 128, 185)       # Strong Blue
COLOR_EMPTY = (52, 73, 94)       # Muted Blue-Gray
COLOR_TEXT = (236, 240, 241)     # Off White
COLOR_BUTTON = (52, 152, 219)    # Bright Blue
COLOR_BUTTON_HOVER = (41, 128, 185)
COLOR_BUTTON_ACTIVE = (46, 204, 113) # Green
COLOR_WARNING = (231, 76, 60)    # Red
COLOR_GOLD = (241, 196, 15)      # Accent Gold

# Fonts
try:
    font_title = pygame.font.SysFont("Segoe UI", 26, bold=True)
    font_header = pygame.font.SysFont("Segoe UI", 20, bold=True)
    font_text = pygame.font.SysFont("Segoe UI", 16, bold=False)
    font_bold = pygame.font.SysFont("Segoe UI", 16, bold=True)
    font_tile = pygame.font.SysFont("Segoe UI", 48, bold=True)
except:
    font_title = pygame.font.Font(None, 36)
    font_header = pygame.font.Font(None, 28)
    font_text = pygame.font.Font(None, 20)
    font_bold = pygame.font.Font(None, 20)
    font_tile = pygame.font.Font(None, 60)

# States presets
goal_state = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

presets = {
    "Easy (2 moves)": [
        [1, 2, 3],
        [4, 0, 6],
        [7, 5, 8]
    ],
    "Medium (3 moves)": [
        [1, 2, 3],
        [0, 4, 6],
        [7, 5, 8]
    ],
    "Hard (14 moves)": [
        [1, 3, 5],
        [4, 2, 6],
        [0, 7, 8]
    ]
}

# State Variables
current_board = copy.deepcopy(presets["Easy (2 moves)"])
initial_state_user = copy.deepcopy(presets["Easy (2 moves)"])

selected_algo = "BFS (Cách 2)"
algos = [
    "BFS (Cách 1)", "BFS (Cách 2)",
    "DFS (Cách 1)", "DFS (Cách 2)",
    "IDS (Cách 1)", "IDS (Cách 2)",
    "UCS"
]

# Statistics
stats_status = "Chờ lệnh (Ready)"
stats_time = "-"
stats_steps = "-"
stats_expanded = "-"
stats_reached = "-"
stats_solution_length = "-"

# Solution playback state
solution_path = []
solution_states = [current_board]
playback_index = 0
playback_paused = True
playback_delay = 0.8  # seconds
last_playback_time = time.time()

# UI Buttons definition
class Button:
    def __init__(self, x, y, w, h, text, callback, data=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.data = data
        self.hovered = False

    def draw(self, screen, is_active=False):
        color = COLOR_BUTTON_ACTIVE if is_active else (COLOR_BUTTON_HOVER if self.hovered else COLOR_BUTTON)
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        
        # Border
        pygame.draw.rect(screen, COLOR_TEXT, self.rect, width=1, border_radius=6)
        
        text_surf = font_bold.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def handle_click(self):
        if self.data is not None:
            self.callback(self.data)
        else:
            self.callback()

# Callbacks
def set_algo(algo_name):
    global selected_algo
    selected_algo = algo_name

def set_preset(preset_name):
    global current_board, initial_state_user, playback_index, solution_path, solution_states, playback_paused
    current_board = copy.deepcopy(presets[preset_name])
    initial_state_user = copy.deepcopy(presets[preset_name])
    reset_playback()

def reset_playback():
    global playback_index, playback_paused, solution_path, solution_states, current_board
    playback_index = 0
    playback_paused = True
    solution_path = []
    solution_states = [initial_state_user]
    current_board = copy.deepcopy(initial_state_user)

def generate_random_puzzle():
    global current_board, initial_state_user
    # Start from goal state and make random moves to guarantee solvability
    state = copy.deepcopy(goal_state)
    
    # helper for finding zero
    def get_zero(s):
        for i in range(3):
            for j in range(3):
                if s[i][j] == 0: return i, j
    
    last_zero = get_zero(state)
    for _ in range(15): # 15 random moves
        x, y = last_zero
        possible_moves = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                possible_moves.append((nx, ny))
        nx, ny = random.choice(possible_moves)
        state[x][y], state[nx][ny] = state[nx][ny], state[x][y]
        last_zero = (nx, ny)
        
    current_board = copy.deepcopy(state)
    initial_state_user = copy.deepcopy(state)
    reset_playback()

def solve_puzzle():
    global initial_state_user, selected_algo, solution_path, solution_states
    global stats_status, stats_time, stats_steps, stats_expanded, stats_reached, stats_solution_length
    global playback_index, playback_paused
    
    stats_status = "Đang giải..."
    reset_playback()
    
    # Draw quick status during execution
    screen.fill(COLOR_BG)
    # Simple draw text
    status_surf = font_title.render("ĐANG GIẢI QUYẾT BÀI TOÁN...", True, COLOR_GOLD)
    screen.blit(status_surf, (WIDTH//2 - status_surf.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    
    start_time = time.perf_counter()
    
    path = None
    steps = 0
    expanded = 0
    reached = 0
    
    if selected_algo == "BFS (Cách 1)":
        path, steps, expanded, reached = bfs_way_1(initial_state_user, goal_state)
    elif selected_algo == "BFS (Cách 2)":
        path, steps, expanded, reached = bfs_way_2(initial_state_user, goal_state)
    elif selected_algo == "DFS (Cách 1)":
        path, steps, expanded, reached = dfs_way_1(initial_state_user, goal_state)
    elif selected_algo == "DFS (Cách 2)":
        path, steps, expanded, reached = dfs_way_2(initial_state_user, goal_state)
    elif selected_algo == "IDS (Cách 1)":
        path, depth, steps = ids_way_1(initial_state_user, goal_state)
        expanded = steps  # approximation
        reached = steps
    elif selected_algo == "IDS (Cách 2)":
        path, depth, steps = ids_way_2(initial_state_user, goal_state)
        expanded = steps
        reached = steps
    elif selected_algo == "UCS":
        path, cost, steps, expanded, reached = ucs(initial_state_user, goal_state)
        
    end_time = time.perf_counter()
    
    if path is not None:
        solution_path = path
        solution_states = get_state_sequence(initial_state_user, path)
        stats_status = "Đã giải xong!"
        stats_time = f"{(end_time - start_time)*1000:.2f} ms"
        stats_steps = str(steps)
        stats_expanded = str(expanded)
        stats_reached = str(reached)
        stats_solution_length = f"{len(path)} nước đi"
        playback_paused = False # Auto play solution
    else:
        stats_status = "Không có lời giải!"
        stats_time = f"{(end_time - start_time)*1000:.2f} ms"
        stats_steps = str(steps)
        stats_expanded = str(expanded)
        stats_reached = str(reached)
        stats_solution_length = "-"

# Setup UI Buttons
buttons = []
# Algorithm selector buttons
y_start = 80
for i, algo in enumerate(algos):
    btn = Button(530 + (i % 2) * 200, y_start + (i // 2) * 40, 190, 32, algo, set_algo, algo)
    buttons.append(btn)

# Presets buttons
y_presets = 260
for i, key in enumerate(presets.keys()):
    btn = Button(530 + i * 135, y_presets, 125, 32, key.split(" ")[0], set_preset, key)
    buttons.append(btn)

# Randomize button
buttons.append(Button(530 + 3 * 135, y_presets, 125, 32, "Ngẫu nhiên", generate_random_puzzle))

# Main action buttons
buttons.append(Button(530, 315, 400, 40, "GIẢI BÀI TOÁN (SOLVE)", solve_puzzle))

# Playback controls
def toggle_playback():
    global playback_paused
    playback_paused = not playback_paused

def step_backward():
    global playback_index, current_board, playback_paused
    playback_paused = True
    if playback_index > 0:
        playback_index -= 1
        current_board = copy.deepcopy(solution_states[playback_index])

def step_forward():
    global playback_index, current_board, playback_paused
    playback_paused = True
    if playback_index < len(solution_states) - 1:
        playback_index += 1
        current_board = copy.deepcopy(solution_states[playback_index])

buttons.append(Button(530, 550, 90, 32, "Tua lại", reset_playback))
buttons.append(Button(630, 550, 90, 32, "Bước lùi", step_backward))
buttons.append(Button(730, 550, 90, 32, "Play/Pause", toggle_playback))
buttons.append(Button(830, 550, 90, 32, "Bước tới", step_forward))

# Main loop
running = True
while running:
    pos = pygame.mouse.get_pos()
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                for btn in buttons:
                    if btn.rect.collidepoint(pos):
                        btn.handle_click()
                        break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                toggle_playback()
            elif event.key == pygame.K_LEFT:
                step_backward()
            elif event.key == pygame.K_RIGHT:
                step_forward()
            elif event.key == pygame.K_r:
                reset_playback()
                
    # Update hover states
    for btn in buttons:
        btn.check_hover(pos)
        
    # Solution playback update
    if not playback_paused and playback_index < len(solution_states) - 1:
        now = time.time()
        if now - last_playback_time >= playback_delay:
            playback_index += 1
            current_board = copy.deepcopy(solution_states[playback_index])
            last_playback_time = now

    # Render
    screen.fill(COLOR_BG)
    
    # 1. Draw Title
    title_surf = font_title.render("8-PUZZLE SOLVER INTERACTIVE VISUALIZER", True, COLOR_GOLD)
    screen.blit(title_surf, (20, 20))
    
    # 2. Draw Puzzle Board Panel
    board_rect = pygame.Rect(40, 80, 420, 420)
    pygame.draw.rect(screen, COLOR_PANEL_BG, board_rect, border_radius=15)
    pygame.draw.rect(screen, COLOR_TEXT, board_rect, width=2, border_radius=15)
    
    cell_size = 400 // 3
    for r in range(3):
        for c in range(3):
            val = current_board[r][c]
            cell_rect = pygame.Rect(board_rect.x + 10 + c * cell_size + 4, 
                                    board_rect.y + 10 + r * cell_size + 4, 
                                    cell_size - 8, 
                                    cell_size - 8)
            
            if val == 0:
                pygame.draw.rect(screen, COLOR_BG, cell_rect, border_radius=10)
            else:
                pygame.draw.rect(screen, COLOR_TILE, cell_rect, border_radius=10)
                text_surf = font_tile.render(str(val), True, COLOR_TEXT)
                text_rect = text_surf.get_rect(center=cell_rect.center)
                screen.blit(text_surf, text_rect)
                
    # 3. Draw Right Panel Background
    panel_rect = pygame.Rect(500, 70, 430, 520)
    pygame.draw.rect(screen, COLOR_PANEL_BG, panel_rect, border_radius=10)
    pygame.draw.rect(screen, COLOR_TEXT, panel_rect, width=1, border_radius=10)
    
    # 4. Draw Section Headers
    screen.blit(font_header.render("1. Chọn thuật toán tìm kiếm", True, COLOR_GOLD), (520, 80))
    screen.blit(font_header.render("2. Chọn cấu hình ban đầu", True, COLOR_GOLD), (520, 230))
    
    # Draw active algorithm indicator
    active_algo_surf = font_bold.render(f"Đang chọn: {selected_algo}", True, COLOR_GOLD)
    screen.blit(active_algo_surf, (520, 200))
    
    # Draw statistics section
    stats_y = 370
    screen.blit(font_header.render("3. Số liệu thống kê (Statistics)", True, COLOR_GOLD), (520, stats_y))
    
    stats = [
        ("Trạng thái:", stats_status),
        ("Thuật toán đã chạy:", selected_algo if stats_steps != "-" else "-"),
        ("Tổng thời gian giải:", stats_time),
        ("Số lần lặp (steps):", stats_steps),
        ("Số nút đã mở rộng:", stats_expanded),
        ("Kích thước reached set:", stats_reached),
        ("Chiều dài đường đi:", stats_solution_length)
    ]
    
    for idx, (label, val) in enumerate(stats):
        lbl_surf = font_text.render(label, True, COLOR_TEXT)
        val_surf = font_bold.render(val, True, COLOR_GOLD if val not in ["-", "Đang giải..."] else COLOR_TEXT)
        screen.blit(lbl_surf, (530, stats_y + 30 + idx * 22))
        screen.blit(val_surf, (730, stats_y + 30 + idx * 22))
        
    # Playback stats below board
    playback_desc = f"Trạng thái hiển thị: {playback_index} / {len(solution_states)-1}"
    pb_surf = font_bold.render(playback_desc, True, COLOR_TEXT)
    screen.blit(pb_surf, (40, 510))
    
    if len(solution_path) > 0:
        path_str = " -> ".join(solution_path[:5])
        if len(solution_path) > 5:
            path_str += f" ... (+{len(solution_path)-5} bước)"
        path_surf = font_text.render(f"Đường đi: {path_str}", True, COLOR_GOLD)
        screen.blit(path_surf, (40, 535))
        
    # 5. Draw Buttons
    for btn in buttons:
        # Check active algo
        is_active = (btn.text == selected_algo)
        btn.draw(screen, is_active=is_active)
        
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
