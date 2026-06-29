import pygame
import sys
import time
import copy
import random
from vacuum_solvers import (
    bfs, dfs, ids, ucs, greedy, astar, idastar, hill_climbing,
    get_neighbors, is_goal
)

# Initialize Pygame
pygame.init()

# Window Configuration
WIDTH, HEIGHT = 950, 610
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vacuum Cleaner World Interactive Visualizer")
clock = pygame.time.Clock()

# Colors
COLOR_BG = (26, 37, 48)          # Dark Slate Blue
COLOR_PANEL_BG = (34, 49, 63)    # Lighter Slate
COLOR_GRID_LINE = (52, 73, 94)   # Grid border lines
COLOR_CLEAN = (47, 53, 66)       # Slate Gray (Clean room)
COLOR_DIRT = (194, 124, 56)      # Brown/Gold for Dirt
COLOR_OBSTACLE = (149, 165, 166) # Gray Brick for Obstacles
COLOR_ROBOT = (46, 204, 113)     # Green for Robot
COLOR_TEXT = (236, 240, 241)     # Off White
COLOR_BUTTON = (52, 152, 219)    # Bright Blue
COLOR_BUTTON_HOVER = (41, 128, 185)
COLOR_BUTTON_ACTIVE = (46, 204, 113) # Green
COLOR_GOLD = (241, 196, 15)      # Accent Gold
COLOR_ROBOT_INNER = (26, 188, 156)

# Fonts
try:
    font_title = pygame.font.SysFont("Segoe UI", 26, bold=True)
    font_header = pygame.font.SysFont("Segoe UI", 18, bold=True)
    font_text = pygame.font.SysFont("Segoe UI", 15, bold=False)
    font_bold = pygame.font.SysFont("Segoe UI", 15, bold=True)
    font_visual = pygame.font.SysFont("Segoe UI", 16, bold=True)
except:
    font_title = pygame.font.Font(None, 34)
    font_header = pygame.font.Font(None, 24)
    font_text = pygame.font.Font(None, 18)
    font_bold = pygame.font.Font(None, 18)
    font_visual = pygame.font.Font(None, 20)

# Grid Settings (6x6 Grid)
ROWS, COLS = 6, 6
grid_size = (ROWS, COLS)

# Initial State elements
robot_pos = (0, 0)
dirt_positions = {(1, 1), (2, 3), (4, 1), (3, 5)}
obstacles = {(1, 2), (2, 2), (4, 4)}

# Tool mode for editing
# "dirt": click to add/remove dirt
# "obstacle": click to add/remove walls
# "robot": click to place robot
tool_mode = "dirt" 

# Selected algorithm
selected_algo = "A*"
algos = ["BFS", "DFS", "IDS", "UCS", "Greedy", "A*", "IDA*", "Hill Climbing"]

# Statistics
stats_status = "Chờ lệnh (Ready)"
stats_time = "-"
stats_steps = "-"
stats_reached = "-"
stats_cost = "-"

# Playback State
solution_path = []
playback_history = []  # List of (robot_pos, dirt_set)
playback_index = 0
playback_paused = True
playback_delay = 0.5  # seconds
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

def set_tool_mode(mode):
    global tool_mode
    tool_mode = mode

def clear_grid():
    global dirt_positions, obstacles, playback_history, solution_path, playback_index, playback_paused
    dirt_positions = set()
    obstacles = set()
    reset_playback()
    playback_history = []
    solution_path = []

def generate_random_grid():
    global robot_pos, dirt_positions, obstacles
    clear_grid()
    
    # Place robot
    robot_pos = (random.randint(0, ROWS-1), random.randint(0, COLS-1))
    
    # Place random dirt
    for r in range(ROWS):
        for c in range(COLS):
            if (r, c) != robot_pos:
                if random.random() < 0.25:
                    dirt_positions.add((r, c))
                elif random.random() < 0.15:
                    obstacles.add((r, c))
                    
    reset_playback()
    global playback_history
    playback_history = [((robot_pos, frozenset(dirt_positions)))]

def reset_playback():
    global playback_index, playback_paused, playback_history
    playback_index = 0
    playback_paused = True

def solve_vacuum():
    global robot_pos, dirt_positions, obstacles, selected_algo, solution_path, playback_history
    global stats_status, stats_time, stats_steps, stats_reached, stats_cost
    global playback_index, playback_paused
    
    stats_status = "Đang giải..."
    playback_index = 0
    playback_paused = True
    
    screen.fill(COLOR_BG)
    status_surf = font_title.render("ĐANG GIẢI QUYẾT BÀI TOÁN...", True, COLOR_GOLD)
    screen.blit(status_surf, (WIDTH//2 - status_surf.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    
    init_state = (robot_pos, frozenset(dirt_positions))
    
    start_time = time.perf_counter()
    
    path = None
    steps = 0
    reached = 0
    cost = 0
    
    if selected_algo == "BFS":
        path, steps, reached = bfs(init_state, grid_size, obstacles)
        cost = len(path) if path else 0
    elif selected_algo == "DFS":
        path, steps, reached = dfs(init_state, grid_size, obstacles)
        cost = len(path) if path else 0
    elif selected_algo == "IDS":
        path, depth, steps = ids(init_state, grid_size, obstacles)
        reached = steps
        cost = len(path) if path else 0
    elif selected_algo == "UCS":
        path, cost, steps, reached = ucs(init_state, grid_size, obstacles)
    elif selected_algo == "Greedy":
        path, steps, reached = greedy(init_state, grid_size, obstacles)
        cost = len(path) if path else 0
    elif selected_algo == "A*":
        path, cost, steps, reached = astar(init_state, grid_size, obstacles)
    elif selected_algo == "IDA*":
        path, limit, steps = idastar(init_state, grid_size, obstacles)
        reached = steps
        cost = len(path) if path else 0
    elif selected_algo == "Hill Climbing":
        path, success, steps, reached = hill_climbing(init_state, grid_size, obstacles)
        cost = len(path) if path else 0
        if not success:
            stats_status = "Bị kẹt tại cực trị cục bộ!"
            solution_path = path
            # Reconstruct states
            playback_history = []
            curr = init_state
            playback_history.append(curr)
            for act in path:
                # Find next state
                for action, next_s, _ in get_neighbors(curr, grid_size, obstacles):
                    if action == act:
                        curr = next_s
                        playback_history.append(curr)
                        break
            stats_time = f"{(time.perf_counter() - start_time)*1000:.2f} ms"
            stats_steps = str(steps)
            stats_reached = str(reached)
            stats_cost = f"{cost} bước"
            playback_paused = False
            return
            
    end_time = time.perf_counter()
    
    if path is not None:
        solution_path = path
        # Reconstruct playback history
        playback_history = []
        curr = init_state
        playback_history.append(curr)
        for act in path:
            for action, next_s, _ in get_neighbors(curr, grid_size, obstacles):
                if action == act:
                    curr = next_s
                    playback_history.append(curr)
                    break
        stats_status = "Đã giải xong!"
        stats_time = f"{(end_time - start_time)*1000:.2f} ms"
        stats_steps = str(steps)
        stats_reached = str(reached)
        stats_cost = f"{cost} bước"
        playback_paused = False
    else:
        stats_status = "Không có lời giải!"
        stats_time = f"{(end_time - start_time)*1000:.2f} ms"
        stats_steps = str(steps)
        stats_reached = str(reached)
        stats_cost = "-"

def toggle_playback():
    global playback_paused
    playback_paused = not playback_paused

def step_backward():
    global playback_index, playback_paused
    playback_paused = True
    if playback_index > 0:
        playback_index -= 1

def step_forward():
    global playback_index, playback_paused
    playback_paused = True
    if playback_index < len(playback_history) - 1:
        playback_index += 1

# Setup Buttons
buttons = []

# 1. Algorithm selection buttons (Right Panel) - 2 columns
y_start = 110
for i, algo in enumerate(algos):
    col = i % 2
    row = i // 2
    btn = Button(520 + col * 195, y_start + row * 36, 180, 28, algo, set_algo, algo)
    buttons.append(btn)

# 2. Brush Tools selection buttons (Right Panel)
y_tools = 265
btn_t_robot = Button(520, y_tools, 120, 28, "Cọ: Robot", set_tool_mode, "robot")
btn_t_dirt = Button(650, y_tools, 120, 28, "Cọ: Rác", set_tool_mode, "dirt")
btn_t_obs = Button(780, y_tools, 120, 28, "Cọ: Tường", set_tool_mode, "obstacle")
buttons.extend([btn_t_robot, btn_t_dirt, btn_t_obs])

# 3. Environment control actions (Right Panel)
y_actions = 310
btn_rand = Button(520, y_actions, 120, 32, "Ngẫu nhiên", generate_random_grid)
btn_clear = Button(650, y_actions, 120, 32, "Xóa sạch", clear_grid)
btn_solve = Button(780, y_actions, 120, 32, "GIẢI (SOLVE)", solve_vacuum)
buttons.extend([btn_rand, btn_clear, btn_solve])

# 4. Playback controls (Left panel under the board)
btn_reset = Button(40, 555, 90, 32, "Tua lại", reset_playback)
btn_back = Button(145, 555, 90, 32, "Bước lùi", step_backward)
btn_play = Button(250, 555, 90, 32, "Play/Pause", toggle_playback)
btn_forward = Button(355, 555, 90, 32, "Bước tới", step_forward)
buttons.extend([btn_reset, btn_back, btn_play, btn_forward])

# Initialize playback history
playback_history = [(robot_pos, frozenset(dirt_positions))]

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
                # Check button clicks
                clicked_button = False
                for btn in buttons:
                    if btn.rect.collidepoint(pos):
                        btn.handle_click()
                        clicked_button = True
                        break
                        
                # Check grid clicks for painting if we didn't click a button
                if not clicked_button:
                    # Board bounds: x = 40 to 460, y = 75 to 495 (420 x 420)
                    board_rect = pygame.Rect(40, 75, 420, 420)
                    if board_rect.collidepoint(pos):
                        cell_size = 400 // ROWS
                        col_idx = (pos[0] - (board_rect.x + 10)) // cell_size
                        row_idx = (pos[1] - (board_rect.y + 10)) // cell_size
                        
                        if 0 <= row_idx < ROWS and 0 <= col_idx < COLS:
                            grid_pos = (row_idx, col_idx)
                            if tool_mode == "robot":
                                if grid_pos not in obstacles:
                                    robot_pos = grid_pos
                                    reset_playback()
                                    playback_history = [(robot_pos, frozenset(dirt_positions))]
                            elif tool_mode == "dirt":
                                if grid_pos not in obstacles and grid_pos != robot_pos:
                                    if grid_pos in dirt_positions:
                                        dirt_positions.remove(grid_pos)
                                    else:
                                        dirt_positions.add(grid_pos)
                                    reset_playback()
                                    playback_history = [(robot_pos, frozenset(dirt_positions))]
                            elif tool_mode == "obstacle":
                                if grid_pos != robot_pos:
                                    if grid_pos in obstacles:
                                        obstacles.remove(grid_pos)
                                    else:
                                        obstacles.add(grid_pos)
                                        # Remove dirt if placed there
                                        if grid_pos in dirt_positions:
                                            dirt_positions.remove(grid_pos)
                                    reset_playback()
                                    playback_history = [(robot_pos, frozenset(dirt_positions))]

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
        
    # Playback update
    if not playback_paused and playback_index < len(playback_history) - 1:
        now = time.time()
        if now - last_playback_time >= playback_delay:
            playback_index += 1
            last_playback_time = now

    # Render
    screen.fill(COLOR_BG)
    
    # 1. Draw Title Header
    title_surf = font_title.render("VACUUM CLEANER WORLD INTERACTIVE VISUALIZER", True, COLOR_GOLD)
    screen.blit(title_surf, (30, 20))
    
    # 2. Draw Current Board State (From Playback Index)
    board_rect = pygame.Rect(40, 75, 420, 420)
    pygame.draw.rect(screen, COLOR_PANEL_BG, board_rect, border_radius=15)
    pygame.draw.rect(screen, COLOR_TEXT, board_rect, width=2, border_radius=15)
    
    # Get state at current playback index
    if playback_index < len(playback_history):
        current_robot_pos, current_dirts = playback_history[playback_index]
    else:
        current_robot_pos, current_dirts = robot_pos, frozenset(dirt_positions)
        
    cell_size = 400 // ROWS
    start_x = board_rect.x + 10
    start_y = board_rect.y + 10
    
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(start_x + c * cell_size, start_y + r * cell_size, cell_size, cell_size)
            
            # 1. Base color (Clean vs Obstacle vs Dirt)
            if (r, c) in obstacles:
                pygame.draw.rect(screen, COLOR_OBSTACLE, rect.inflate(-4, -4), border_radius=8)
            else:
                pygame.draw.rect(screen, COLOR_CLEAN, rect.inflate(-4, -4), border_radius=8)
                
                # Draw Dirt if dirty
                if (r, c) in current_dirts:
                    # Draw a nice pile/circle for dirt
                    pygame.draw.circle(screen, COLOR_DIRT, rect.center, cell_size // 3)
                    dirt_label = font_visual.render("Rác", True, COLOR_TEXT)
                    screen.blit(dirt_label, dirt_label.get_rect(center=rect.center))
            
            # Draw grid cell border
            pygame.draw.rect(screen, COLOR_GRID_LINE, rect, width=1)
            
            # 2. Draw Robot if current position
            if (r, c) == current_robot_pos:
                pygame.draw.circle(screen, COLOR_ROBOT, rect.center, cell_size // 2 - 6)
                pygame.draw.circle(screen, COLOR_ROBOT_INNER, rect.center, cell_size // 2 - 10, width=2)
                robot_label = font_visual.render("🤖", True, COLOR_TEXT)
                screen.blit(robot_label, robot_label.get_rect(center=rect.center))
                
    # 3. Draw Right Panel Background
    panel_rect = pygame.Rect(500, 75, 415, 512)
    pygame.draw.rect(screen, COLOR_PANEL_BG, panel_rect, border_radius=10)
    pygame.draw.rect(screen, COLOR_TEXT, panel_rect, width=1, border_radius=10)
    
    # 4. Draw Right Panel Section Headers
    screen.blit(font_header.render("1. Chọn thuật toán tìm kiếm Robot", True, COLOR_GOLD), (520, 85))
    screen.blit(font_header.render("2. Chọn cọ vẽ & Tác vụ bản đồ", True, COLOR_GOLD), (520, 240))
    
    # Draw selected/active indicator
    active_algo_surf = font_bold.render(f"Đang chọn: {selected_algo}", True, COLOR_GOLD)
    screen.blit(active_algo_surf, (520, 215))
    
    # Highlight active tool brush button border
    # tool_mode is "robot", "dirt", "obstacle"
    tool_colors = {"robot": btn_t_robot, "dirt": btn_t_dirt, "obstacle": btn_t_obs}
    for mode, btn in tool_colors.items():
        if tool_mode == mode:
            pygame.draw.rect(screen, COLOR_GOLD, btn.rect.inflate(4, 4), width=2, border_radius=8)

    # Draw statistics section
    stats_y = 355
    screen.blit(font_header.render("3. Số liệu thống kê (Statistics)", True, COLOR_GOLD), (520, stats_y))
    
    stats = [
        ("Trạng thái giải:", stats_status),
        ("Tổng thời gian giải:", stats_time),
        ("Tổng số bước lặp (steps):", stats_steps),
        ("Số nút đã mở rộng:", stats_reached),
        ("Chi phí đường đi:", stats_cost)
    ]
    
    for idx, (label, val) in enumerate(stats):
        lbl_surf = font_text.render(label, True, COLOR_TEXT)
        val_surf = font_bold.render(val, True, COLOR_GOLD if val not in ["-", "Đang giải..."] else COLOR_TEXT)
        screen.blit(lbl_surf, (530, stats_y + 25 + idx * 22))
        screen.blit(val_surf, (730, stats_y + 25 + idx * 22))
        
    # Playback stats (Left Panel)
    playback_desc = f"Bước hiển thị: {playback_index} / {len(playback_history)-1}"
    pb_surf = font_bold.render(playback_desc, True, COLOR_TEXT)
    screen.blit(pb_surf, (40, 505))
    
    if len(solution_path) > 0:
        path_str = " -> ".join(solution_path[:5])
        if len(solution_path) > 5:
            path_str += f" ... (+{len(solution_path)-5} hành động)"
        path_surf = font_text.render(f"Kế hoạch: {path_str}", True, COLOR_GOLD)
        screen.blit(path_surf, (40, 530))
        
    # 5. Draw Buttons
    for btn in buttons:
        is_active = (btn.text == selected_algo)
        btn.draw(screen, is_active=is_active)
        
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
