import pygame
import sys
import time
import copy
import random
from tictactoe_solvers import minimax, alpha_beta, expectimax, is_terminal, get_actions

# Initialize Pygame
pygame.init()

# Window Configuration
WIDTH, HEIGHT = 950, 610
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic-Tac-Toe Adversarial Search Visualizer")
clock = pygame.time.Clock()

# Colors
COLOR_BG = (26, 37, 48)          # Dark Slate Blue
COLOR_PANEL_BG = (34, 49, 63)    # Lighter Slate
COLOR_GRID_LINE = (52, 73, 94)   # Grid line
COLOR_CELL_BG = (47, 53, 66)     # Clean gray for cell
COLOR_X = (46, 204, 113)         # Green for X
COLOR_O = (231, 76, 60)          # Red for O
COLOR_TEXT = (236, 240, 241)     # Off White
COLOR_BUTTON = (52, 152, 219)    # Bright Blue
COLOR_BUTTON_HOVER = (41, 128, 185)
COLOR_BUTTON_ACTIVE = (46, 204, 113) # Green
COLOR_GOLD = (241, 196, 15)      # Accent Gold

# Fonts
try:
    font_title = pygame.font.SysFont("Segoe UI", 26, bold=True)
    font_header = pygame.font.SysFont("Segoe UI", 18, bold=True)
    font_text = pygame.font.SysFont("Segoe UI", 15, bold=False)
    font_bold = pygame.font.SysFont("Segoe UI", 15, bold=True)
    font_symbol = pygame.font.SysFont("Segoe UI", 72, bold=True)
except:
    font_title = pygame.font.Font(None, 34)
    font_header = pygame.font.Font(None, 24)
    font_text = pygame.font.Font(None, 18)
    font_bold = pygame.font.Font(None, 18)
    font_symbol = pygame.font.Font(None, 80)

# Game Variables
# 1: X, -1: O, 0: Empty
board = [0] * 9

# Modes: "human_ai", "ai_ai"
game_mode = "human_ai"

# AI Algorithms: "minimax", "alpha_beta", "expectimax"
ai_algo = "alpha_beta"

# Scoreboard
score_x = 0  # Human or AI_X
score_o = 0  # AI_O
score_draw = 0

# Game State
# "playing", "game_over"
game_state = "playing"
current_turn = 1  # 1: X (Human), -1: O (AI)
winner_val = None

# Stats of current search
stats_nodes = "-"
stats_prunes = "-"
stats_time = "-"
stats_status = "Đến lượt bạn (X)"

# AI vs AI settings
ai_vs_ai_delay = 0.6  # seconds
last_ai_move_time = time.time()

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
def set_game_mode(mode):
    global game_mode
    game_mode = mode
    restart_game()

def set_ai_algo(algo):
    global ai_algo
    ai_algo = algo

def restart_game():
    global board, game_state, current_turn, winner_val
    global stats_nodes, stats_prunes, stats_time, stats_status
    board = [0] * 9
    game_state = "playing"
    current_turn = 1 # X starts
    winner_val = None
    stats_nodes = "-"
    stats_prunes = "-"
    stats_time = "-"
    stats_status = "Trận đấu mới bắt đầu" if game_mode == "ai_ai" else "Đến lượt bạn (X)"

def reset_scoreboard():
    global score_x, score_o, score_draw
    score_x = 0
    score_o = 0
    score_draw = 0
    restart_game()

# AI Search trigger
def ai_make_move(player):
    """
    Kích hoạt AI tính toán và đi nước đi cho player (1 cho X, -1 cho O).
    """
    global board, ai_algo, stats_nodes, stats_prunes, stats_time, stats_status, game_state, winner_val, score_x, score_o, score_draw
    
    stats = {"nodes": 0, "prunes": 0}
    start_time = time.perf_counter()
    
    # Run solver
    is_max = (player == 1)
    
    if ai_algo == "minimax":
        score, move = minimax(board, 0, is_max, stats)
    elif ai_algo == "alpha_beta":
        score, move = alpha_beta(board, 0, -float('inf'), float('inf'), is_max, stats)
    elif ai_algo == "expectimax":
        score, move = expectimax(board, 0, is_max, stats)
        
    end_time = time.perf_counter()
    
    # Record stats
    stats_time = f"{(end_time - start_time)*1000:.2f} ms"
    stats_nodes = str(stats["nodes"])
    stats_prunes = str(stats["prunes"]) if ai_algo == "alpha_beta" else "-"
    
    if move is not None:
        board[move] = player
        
    # Check game over
    terminal, winner = is_terminal(board)
    if terminal:
        game_state = "game_over"
        winner_val = winner
        if winner == 1:
            score_x += 1
            stats_status = "X Thắng cuộc!"
        elif winner == -1:
            score_o += 1
            stats_status = "O Thắng cuộc!"
        else:
            score_draw += 1
            stats_status = "Hòa cờ!"

# Setup Buttons
buttons = []

# 1. Game mode selection buttons (Right Panel)
y_mode = 110
btn_m_ha = Button(520, y_mode, 180, 28, "Human vs AI", set_game_mode, "human_ai")
btn_m_aa = Button(715, y_mode, 180, 28, "AI vs AI Showdown", set_game_mode, "ai_ai")
buttons.extend([btn_m_ha, btn_m_aa])

# 2. AI Algorithm Selection Buttons
y_algo = 210
btn_a_minimax = Button(520, y_algo, 120, 28, "Minimax", set_ai_algo, "minimax")
btn_a_ab = Button(650, y_algo, 120, 28, "Alpha-Beta", set_ai_algo, "alpha_beta")
btn_a_exp = Button(780, y_algo, 120, 28, "Expectimax", set_ai_algo, "expectimax")
buttons.extend([btn_a_minimax, btn_a_ab, btn_a_exp])

# 3. Game controls
y_ctrl = 265
btn_restart = Button(520, y_ctrl, 180, 32, "CHƠI LẠI (RESTART)", restart_game)
btn_reset_score = Button(715, y_ctrl, 180, 32, "XÓA ĐIỂM SỐ", reset_scoreboard)
buttons.extend([btn_restart, btn_reset_score])

# Main loop
running = True
while running:
    pos = pygame.mouse.get_pos()
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Check button clicks
                clicked_button = False
                for btn in buttons:
                    if btn.rect.collidepoint(pos):
                        btn.handle_click()
                        clicked_button = True
                        break
                        
                # Click on grid canvas (Left Panel)
                # Grid bounds: x = 40 to 430, y = 75 to 465 (390 x 390)
                board_rect = pygame.Rect(40, 75, 420, 420)
                if not clicked_button and game_state == "playing" and game_mode == "human_ai" and current_turn == 1:
                    if board_rect.collidepoint(pos):
                        cell_size = 400 // 3
                        col_idx = (pos[0] - (board_rect.x + 10)) // cell_size
                        row_idx = (pos[1] - (board_rect.y + 10)) // cell_size
                        
                        if 0 <= row_idx < 3 and 0 <= col_idx < 3:
                            cell_id = row_idx * 3 + col_idx
                            if board[cell_id] == 0:
                                board[cell_id] = 1 # Human plays X
                                
                                # Check game over
                                terminal, winner = is_terminal(board)
                                if terminal:
                                    game_state = "game_over"
                                    winner_val = winner
                                    if winner == 1:
                                        score_x += 1
                                        stats_status = "X Thắng cuộc!"
                                    elif winner == -1:
                                        score_o += 1
                                        stats_status = "O Thắng cuộc!"
                                    else:
                                        score_draw += 1
                                        stats_status = "Hòa cờ!"
                                else:
                                    current_turn = -1 # Handover to AI
                                    stats_status = "AI đang suy nghĩ..."

    # Update hover states
    for btn in buttons:
        btn.check_hover(pos)
        
    # AI playing logic
    if game_state == "playing":
        if game_mode == "human_ai" and current_turn == -1:
            # Let O (AI) play
            ai_make_move(-1)
            current_turn = 1
            if game_state == "playing":
                stats_status = "Đến lượt bạn (X)"
        elif game_mode == "ai_ai":
            # Autoplay AI vs AI showdown
            now = time.time()
            if now - last_ai_move_time >= ai_vs_ai_delay:
                # Play whoever's turn it is
                ai_make_move(current_turn)
                current_turn = -current_turn
                last_ai_move_time = now
                if game_state == "playing":
                    stats_status = f"Đến lượt AI ({'X' if current_turn == 1 else 'O'})"

    # Render
    screen.fill(COLOR_BG)
    
    # 1. Draw Title Header
    title_surf = font_title.render("TIC-TAC-TOE ADVERSARIAL SEARCH VISUALIZER", True, COLOR_GOLD)
    screen.blit(title_surf, (30, 20))
    
    # 2. Draw Board (Left Panel)
    board_rect = pygame.Rect(40, 75, 420, 420)
    pygame.draw.rect(screen, COLOR_PANEL_BG, board_rect, border_radius=15)
    pygame.draw.rect(screen, COLOR_TEXT, board_rect, width=2, border_radius=15)
    
    cell_size = 400 // 3
    start_x = board_rect.x + 10
    start_y = board_rect.y + 10
    
    for r in range(3):
        for c in range(3):
            cell_rect = pygame.Rect(start_x + c * cell_size, start_y + r * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, COLOR_CELL_BG, cell_rect.inflate(-6, -6), border_radius=10)
            pygame.draw.rect(screen, COLOR_GRID_LINE, cell_rect, width=1)
            
            val = board[r * 3 + c]
            if val == 1:
                # Draw X
                x_surf = font_symbol.render("X", True, COLOR_X)
                screen.blit(x_surf, x_surf.get_rect(center=cell_rect.center))
            elif val == -1:
                # Draw O
                o_surf = font_symbol.render("O", True, COLOR_O)
                screen.blit(o_surf, o_surf.get_rect(center=cell_rect.center))

    # 3. Draw Right Panel Background
    panel_rect = pygame.Rect(500, 75, 415, 512)
    pygame.draw.rect(screen, COLOR_PANEL_BG, panel_rect, border_radius=10)
    pygame.draw.rect(screen, COLOR_TEXT, panel_rect, width=1, border_radius=10)
    
    # 4. Draw Section Headers
    screen.blit(font_header.render("1. Chọn chế độ trò chơi", True, COLOR_GOLD), (520, 85))
    screen.blit(font_header.render("2. Cấu hình giải thuật AI", True, COLOR_GOLD), (520, 185))
    screen.blit(font_header.render("3. Điều khiển & Thống kê", True, COLOR_GOLD), (520, 325))
    
    # Highlights active buttons
    if game_mode == "human_ai":
        pygame.draw.rect(screen, COLOR_GOLD, btn_m_ha.rect.inflate(4, 4), width=2, border_radius=8)
    else:
        pygame.draw.rect(screen, COLOR_GOLD, btn_m_aa.rect.inflate(4, 4), width=2, border_radius=8)
        
    ai_buttons = {"minimax": btn_a_minimax, "alpha_beta": btn_a_ab, "expectimax": btn_a_exp}
    for algo, btn in ai_buttons.items():
        if ai_algo == algo:
            pygame.draw.rect(screen, COLOR_GOLD, btn.rect.inflate(4, 4), width=2, border_radius=8)

    # Scoreboard
    score_y = 350
    lbl_score = font_bold.render("BẢNG ĐIỂM SỐ (SCOREBOARD)", True, COLOR_GOLD)
    screen.blit(lbl_score, (520, score_y))
    
    score_desc = f"X: {score_x}  |  O: {score_o}  |  Hòa: {score_draw}"
    score_val_surf = font_header.render(score_desc, True, COLOR_TEXT)
    screen.blit(score_val_surf, (520, score_y + 20))
    
    # Search stats
    stats_y = 405
    stats = [
        ("Trạng thái trận đấu:", stats_status),
        ("Độ khó AI đang dùng:", ai_algo.upper()),
        ("Thời gian AI suy nghĩ:", stats_time),
        ("Số nút AI duyệt (nodes):", stats_nodes),
        ("Số lần cắt tỉa (prunes):", stats_prunes)
    ]
    
    for idx, (label, val) in enumerate(stats):
        lbl_surf = font_text.render(label, True, COLOR_TEXT)
        val_surf = font_bold.render(val, True, COLOR_GOLD if val not in ["-", "AI đang suy nghĩ..."] else COLOR_TEXT)
        screen.blit(lbl_surf, (530, stats_y + 25 + idx * 22))
        screen.blit(val_surf, (730, stats_y + 25 + idx * 22))
        
    # 5. Draw Buttons
    for btn in buttons:
        btn.draw(screen)
        
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
