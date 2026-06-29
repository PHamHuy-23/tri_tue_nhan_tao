import pygame
import sys
import time
import copy
import random
from nqueens_solvers import (
    h_attack, simple_hill_climbing, steepest_ascent_hill_climbing,
    stochastic_hill_climbing, random_restart_hill_climbing,
    local_beam_search, simulated_annealing
)

# Initialize Pygame
pygame.init()

# Window Configuration
WIDTH, HEIGHT = 950, 610
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("N-Queens Local Search Solver Visualizer")
clock = pygame.time.Clock()

# Colors
COLOR_BG = (26, 37, 48)          # Dark Slate Blue
COLOR_PANEL_BG = (34, 49, 63)    # Lighter Slate
COLOR_LIGHT_SQUARE = (236, 240, 241) # Light chess square
COLOR_DARK_SQUARE = (127, 140, 141)  # Dark chess square
COLOR_QUEEN = (231, 76, 60)      # Red for Queen
COLOR_TEXT = (236, 240, 241)     # Off White
COLOR_BUTTON = (52, 152, 219)    # Bright Blue
COLOR_BUTTON_HOVER = (41, 128, 185)
COLOR_BUTTON_ACTIVE = (46, 204, 113) # Green
COLOR_GOLD = (241, 196, 15)      # Accent Gold
COLOR_ATTACK_LINE = (231, 76, 60) # Red line for attack highlight

# Fonts
try:
    font_title = pygame.font.SysFont("Segoe UI", 26, bold=True)
    font_header = pygame.font.SysFont("Segoe UI", 18, bold=True)
    font_text = pygame.font.SysFont("Segoe UI", 15, bold=False)
    font_bold = pygame.font.SysFont("Segoe UI", 15, bold=True)
    font_queen = pygame.font.SysFont("Segoe UI", 36, bold=True)
except:
    font_title = pygame.font.Font(None, 34)
    font_header = pygame.font.Font(None, 24)
    font_text = pygame.font.Font(None, 18)
    font_bold = pygame.font.Font(None, 18)
    font_queen = pygame.font.Font(None, 40)

# States variables
n_queens = 8
current_state = [random.randint(0, n_queens - 1) for _ in range(n_queens)]
initial_state_user = list(current_state)

selected_algo = "Steepest HC"
algos = [
    "Simple HC", "Steepest HC", "Stochastic HC",
    "Random Restart", "Local Beam", "Simulated Ann."
]

algo_display_names = {
    "Simple HC": "Simple Hill Climbing",
    "Steepest HC": "Steepest Ascent Hill Climbing",
    "Stochastic HC": "Stochastic Hill Climbing",
    "Random Restart": "Random-Restart Hill Climbing",
    "Local Beam": "Local Beam Search (k=3)",
    "Simulated Ann.": "Simulated Annealing"
}

# Statistics
stats_status = "Chờ lệnh (Ready)"
stats_time = "-"
stats_steps = "-"
stats_restarts = "-"
stats_attacks = str(h_attack(current_state))

# Playback state
playback_history = [(current_state, h_attack(current_state))]
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

def reset_playback():
    global playback_index, playback_paused, current_state
    playback_index = 0
    playback_paused = True
    current_state = list(initial_state_user)

def generate_random_board():
    global current_state, initial_state_user, stats_attacks
    current_state = [random.randint(0, n_queens - 1) for _ in range(n_queens)]
    initial_state_user = list(current_state)
    stats_attacks = str(h_attack(current_state))
    reset_playback()
    global playback_history
    playback_history = [(current_state, h_attack(current_state))]

def solve_nqueens():
    global initial_state_user, selected_algo, playback_history, current_state
    global stats_status, stats_time, stats_steps, stats_restarts, stats_attacks
    global playback_index, playback_paused
    
    stats_status = "Đang giải..."
    playback_index = 0
    playback_paused = True
    
    screen.fill(COLOR_BG)
    status_surf = font_title.render("ĐANG GIẢI QUYẾT BÀI TOÁN...", True, COLOR_GOLD)
    screen.blit(status_surf, (WIDTH//2 - status_surf.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    
    start_time = time.perf_counter()
    
    best_state = None
    best_h = -1
    steps = 0
    restarts = 0
    history = []
    
    if selected_algo == "Simple HC":
        best_state, best_h, steps, history = simple_hill_climbing(initial_state_user)
        playback_history = history
    elif selected_algo == "Steepest HC":
        best_state, best_h, steps, history = steepest_ascent_hill_climbing(initial_state_user)
        playback_history = history
    elif selected_algo == "Stochastic HC":
        best_state, best_h, steps, history = stochastic_hill_climbing(initial_state_user)
        playback_history = history
    elif selected_algo == "Random Restart":
        best_state, best_h, steps, restarts, history = random_restart_hill_climbing(n_queens=8, max_restarts=100)
        playback_history = history
    elif selected_algo == "Local Beam":
        best_state, best_h, steps, history = local_beam_search(n_queens=8, k=3, max_steps=100)
        playback_history = history
    elif selected_algo == "Simulated Ann.":
        best_state, best_h, steps, history = simulated_annealing(initial_state_user, temp=100.0, alpha=0.95, min_temp=0.01)
        playback_history = history
        
    end_time = time.perf_counter()
    
    stats_time = f"{(end_time - start_time)*1000:.2f} ms"
    stats_steps = str(steps)
    stats_restarts = str(restarts) if selected_algo == "Random Restart" else "-"
    stats_attacks = str(best_h)
    
    if best_h == 0:
        stats_status = "Đã tìm thấy lời giải tối ưu!"
    else:
        stats_status = f"Bị kẹt ở cực trị cục bộ (H={best_h})"
        
    playback_paused = False # Auto play solution

def toggle_playback():
    global playback_paused
    playback_paused = not playback_paused

def step_backward():
    global playback_index, current_state, playback_paused
    playback_paused = True
    if playback_index > 0:
        playback_index -= 1
        current_state = list(playback_history[playback_index][0])

def step_forward():
    global playback_index, current_state, playback_paused
    playback_paused = True
    if playback_index < len(playback_history) - 1:
        playback_index += 1
        current_state = list(playback_history[playback_index][0])

# Setup UI Buttons
buttons = []

# 1. Algorithm selector buttons (Right panel) - 2 columns
y_start = 110
for i, algo in enumerate(algos):
    col = i % 2
    row = i // 2
    btn = Button(520 + col * 195, y_start + row * 38, 180, 30, algo, set_algo, algo)
    buttons.append(btn)

# 2. Main control buttons (Right panel)
btn_rand = Button(520, 260, 180, 35, "TẠO NGẪU NHIÊN", generate_random_board)
btn_solve = Button(715, 260, 180, 35, "GIẢI BÀI TOÁN", solve_nqueens)
buttons.extend([btn_rand, btn_solve])

# 3. Playback controls (Left panel under the board)
btn_reset = Button(40, 555, 90, 32, "Tua lại", reset_playback)
btn_back = Button(145, 555, 90, 32, "Bước lùi", step_backward)
btn_play = Button(250, 555, 90, 32, "Play/Pause", toggle_playback)
btn_forward = Button(355, 555, 90, 32, "Bước tới", step_forward)
buttons.extend([btn_reset, btn_back, btn_play, btn_forward])

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
        
    # Playback update
    if not playback_paused and playback_index < len(playback_history) - 1:
        now = time.time()
        if now - last_playback_time >= playback_delay:
            playback_index += 1
            current_state = list(playback_history[playback_index][0])
            last_playback_time = now

    # Render
    screen.fill(COLOR_BG)
    
    # 1. Draw Title Header
    title_surf = font_title.render("N-QUEENS LOCAL SEARCH INTERACTIVE VISUALIZER", True, COLOR_GOLD)
    screen.blit(title_surf, (30, 20))
    
    # 2. Draw Chessboard (Left Side)
    board_rect = pygame.Rect(40, 75, 420, 420)
    pygame.draw.rect(screen, COLOR_PANEL_BG, board_rect, border_radius=10)
    
    cell_size = 400 // n_queens
    # Adjust starting x, y slightly inside board_rect
    start_x = board_rect.x + 10
    start_y = board_rect.y + 10
    
    # Draw Board grid
    for r in range(n_queens):
        for c in range(n_queens):
            rect = pygame.Rect(start_x + c * cell_size, start_y + r * cell_size, cell_size, cell_size)
            color = COLOR_LIGHT_SQUARE if (r + c) % 2 == 0 else COLOR_DARK_SQUARE
            pygame.draw.rect(screen, color, rect)
            
            # Draw queen if present in this col
            if current_state[c] == r:
                # Draw a beautiful circle representing Queen
                pygame.draw.circle(screen, COLOR_QUEEN, rect.center, cell_size // 2 - 4)
                pygame.draw.circle(screen, COLOR_TEXT, rect.center, cell_size // 2 - 8, width=2)
                # Print "Q" text
                q_surf = font_queen.render("Q", True, COLOR_TEXT)
                q_rect = q_surf.get_rect(center=rect.center)
                screen.blit(q_surf, q_rect)
                
    # 3. Draw Right Panel Background
    panel_rect = pygame.Rect(500, 75, 415, 512)
    pygame.draw.rect(screen, COLOR_PANEL_BG, panel_rect, border_radius=10)
    pygame.draw.rect(screen, COLOR_TEXT, panel_rect, width=1, border_radius=10)
    
    # 4. Draw Right Panel Sections
    screen.blit(font_header.render("1. Chọn thuật toán tìm kiếm cục bộ", True, COLOR_GOLD), (520, 85))
    screen.blit(font_header.render("2. Điều khiển giải thuật", True, COLOR_GOLD), (520, 230))
    
    # Active algorithm indicator
    active_algo_surf = font_bold.render(f"Đang chọn: {algo_display_names.get(selected_algo, selected_algo)}", True, COLOR_GOLD)
    screen.blit(active_algo_surf, (520, 200))
    
    # Draw statistics section (Right Panel)
    stats_y = 315
    screen.blit(font_header.render("3. Số liệu thống kê (Statistics)", True, COLOR_GOLD), (520, stats_y))
    
    stats = [
        ("Trạng thái giải:", stats_status),
        ("Tổng thời gian giải:", stats_time),
        ("Tổng số bước lặp (steps):", stats_steps),
        ("Số lần khởi động lại:", stats_restarts),
        ("Số cặp hậu tấn công (H):", stats_attacks)
    ]
    
    for idx, (label, val) in enumerate(stats):
        lbl_surf = font_text.render(label, True, COLOR_TEXT)
        val_surf = font_bold.render(val, True, COLOR_GOLD if val not in ["-", "Đang giải..."] else COLOR_TEXT)
        screen.blit(lbl_surf, (530, stats_y + 25 + idx * 22))
        screen.blit(val_surf, (730, stats_y + 25 + idx * 22))
        
    # Playback stats (Left Panel)
    cur_h = h_attack(current_state)
    playback_desc = f"Bước hiển thị: {playback_index} / {len(playback_history)-1}  |  Cặp tấn công: {cur_h}"
    pb_surf = font_bold.render(playback_desc, True, COLOR_TEXT if cur_h > 0 else COLOR_GOLD)
    screen.blit(pb_surf, (40, 505))
    
    # Draw Buttons
    for btn in buttons:
        is_active = (btn.text == selected_algo)
        btn.draw(screen, is_active=is_active)
        
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
