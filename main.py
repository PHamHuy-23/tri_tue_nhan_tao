import pygame
import sys
import os
import time
import copy
import random
import math

# Add directories to sys.path to allow clean imports
sys.path.append(os.path.abspath("Search_Algorithm"))
sys.path.append(os.path.abspath("Search_Algorithm/08_HillClimbing"))
sys.path.append(os.path.abspath("Project_ca_nhan/VacuumCleaner"))
sys.path.append(os.path.abspath("Project_ca_nhan/MapColoring"))
sys.path.append(os.path.abspath("Project_ca_nhan/TicTacToe"))

# Import Solvers
from solvers import (
    bfs_way_1, bfs_way_2, dfs_way_1, dfs_way_2, ids_way_1, ids_way_2, ucs as puzzle_ucs,
    greedy as puzzle_greedy, astar as puzzle_astar, idastar as puzzle_idastar,
    h_hamming as puzzle_h_hamming, h_manhattan as puzzle_h_manhattan,
    h_euclidean as puzzle_h_euclidean, get_state_sequence as puzzle_get_sequence
)
from nqueens_solvers import (
    h_attack, simple_hill_climbing, steepest_ascent_hill_climbing,
    stochastic_hill_climbing, random_restart_hill_climbing,
    local_beam_search, simulated_annealing
)
from vacuum_solvers import (
    bfs as vac_bfs, dfs as vac_dfs, ids as vac_ids, ucs as vac_ucs,
    greedy as vac_greedy, astar as vac_astar, idastar as vac_idastar,
    hill_climbing as vac_hc, get_neighbors as vac_get_neighbors
)
from map_solvers import (
    solve_backtracking, solve_forward_checking, solve_ac3, solve_min_conflicts
)
from tictactoe_solvers import (
    minimax as ttt_minimax, alpha_beta as ttt_ab, expectimax as ttt_expectimax,
    is_terminal as ttt_is_terminal
)

# Initialize Pygame
pygame.init()

# Window Configuration
WIDTH, HEIGHT = 980, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Algorithms & Visualization Hub")
clock = pygame.time.Clock()

# Common Premium Color Palette
COLOR_BG = (18, 24, 38)          # Deep Cyber Dark
COLOR_PANEL_BG = (28, 36, 55)    # Sleek Panel Slate
COLOR_GRID_LINE = (38, 50, 77)   # Grid line highlight
COLOR_TEXT = (245, 246, 250)     # Clean Ice White
COLOR_MUTED_TEXT = (149, 165, 166)
COLOR_BUTTON = (41, 128, 185)    # Bright Cyan Blue
COLOR_BUTTON_HOVER = (52, 152, 219)
COLOR_BUTTON_ACTIVE = (46, 204, 113) # Emerald Green
COLOR_GOLD = (241, 196, 15)      # Rich Amber Gold
COLOR_RED = (231, 76, 60)        # Laser Red
COLOR_CYAN = (52, 152, 219)
COLOR_PURPLE = (155, 89, 182)

# Common Fonts
try:
    font_title = pygame.font.SysFont("Segoe UI", 26, bold=True)
    font_subtitle = pygame.font.SysFont("Segoe UI", 16, bold=False)
    font_header = pygame.font.SysFont("Segoe UI", 18, bold=True)
    font_text = pygame.font.SysFont("Segoe UI", 15, bold=False)
    font_bold = pygame.font.SysFont("Segoe UI", 15, bold=True)
    font_large_symbol = pygame.font.SysFont("Segoe UI", 68, bold=True)
except:
    font_title = pygame.font.Font(None, 34)
    font_subtitle = pygame.font.Font(None, 22)
    font_header = pygame.font.Font(None, 24)
    font_text = pygame.font.Font(None, 18)
    font_bold = pygame.font.Font(None, 18)
    font_large_symbol = pygame.font.Font(None, 75)

# Current Screen State
# "MENU", "PUZZLE", "NQUEENS", "VACUUM", "MAPCOLORING", "TICTACTOE"
current_screen = "MENU"

# Space starfield background decoration
stars = [{"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT), "r": random.random()*2, "s": random.random()*0.5+0.1} for _ in range(80)]

def update_and_draw_stars(screen):
    for star in stars:
        star["y"] += star["s"]
        if star["y"] > HEIGHT:
            star["y"] = 0
            star["x"] = random.randint(0, WIDTH)
        # Glow effect
        alpha = int(120 + 80 * math.sin(time.time() * 2 + star["x"]))
        alpha = max(0, min(255, alpha))
        color = (255, 255, 255, alpha)
        # Draw soft star
        s_surf = pygame.Surface((int(star["r"]*2)+2, int(star["r"]*2)+2), pygame.SRCALPHA)
        pygame.draw.circle(s_surf, color, (int(star["r"])+1, int(star["r"])+1), star["r"])
        screen.blit(s_surf, (star["x"], star["y"]))

# Button UI helper class
class Button:
    def __init__(self, x, y, w, h, text, callback, data=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.data = data
        self.hovered = False

    def draw(self, screen, is_active=False):
        color = COLOR_BUTTON_ACTIVE if is_active else (COLOR_BUTTON_HOVER if self.hovered else COLOR_BUTTON)
        # Soft drop shadow for button
        shadow_rect = self.rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(screen, (10, 14, 23, 100), shadow_rect, border_radius=8)
        
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_TEXT, self.rect, width=1, border_radius=8)
        
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

# =========================================================================
# SECTION 1: LAUNCHER HUB MENU
# =========================================================================
class MenuScreen:
    def __init__(self):
        self.cards = [
            {"id": "PUZZLE", "title": "1. Bài toán 8-Puzzle", "desc": "Tìm kiếm đường đi trượt các ô số. Hỗ trợ 13 biến thể giải thuật khác nhau.", "icon": "🧩", "color": COLOR_CYAN},
            {"id": "NQUEENS", "title": "2. Bài toán N-Queens", "desc": "Đặt 8 quân hậu tránh tấn công nhau bằng các giải thuật leo đồi & tối ưu.", "icon": "👑", "color": COLOR_GOLD},
            {"id": "VACUUM", "title": "3. Thế giới Máy hút bụi", "desc": "Robot dọn rác và tránh chướng ngại vật trên lưới 2D. 8 thuật toán.", "icon": "🤖", "color": COLOR_BUTTON_ACTIVE},
            {"id": "MAPCOLORING", "title": "4. Tô màu bản đồ (CSP)", "desc": "Tô màu các miền sao cho không có 2 miền kề trùng màu. AC-3 & Backtrack.", "icon": "🎨", "color": COLOR_PURPLE},
            {"id": "TICTACTOE", "title": "5. Game Tic-Tac-Toe", "desc": "Trò chơi 3x3 đối kháng kịch tính chống lại AI Minimax & Expectimax.", "icon": "❌", "color": COLOR_RED}
        ]
        self.hovered_card = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos = pygame.mouse.get_pos()
                for idx, card in enumerate(self.cards):
                    card_rect = pygame.Rect(80, 150 + idx * 75, 820, 62)
                    if card_rect.collidepoint(pos):
                        global current_screen
                        current_screen = card["id"]
                        screen_initializers[card["id"]]()
                        break

    def update(self):
        pos = pygame.mouse.get_pos()
        self.hovered_card = None
        for idx, card in enumerate(self.cards):
            card_rect = pygame.Rect(80, 150 + idx * 75, 820, 62)
            if card_rect.collidepoint(pos):
                self.hovered_card = idx
                break

    def draw(self, screen):
        # Draw Title
        title_surf = font_title.render("TRUNG TÂM GIẢI THUẬT & TRỰC QUAN HÓA AI", True, COLOR_GOLD)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 40))
        
        sub_surf = font_subtitle.render("Học phần: Trí Tuệ Nhân Tạo (252ARIN330585_06) | Sinh viên: Phạm Quốc Huy - 24110226", True, COLOR_MUTED_TEXT)
        screen.blit(sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, 85))
        
        # Draw Cards
        for idx, card in enumerate(self.cards):
            is_hover = (self.hovered_card == idx)
            card_rect = pygame.Rect(80, 150 + idx * 75, 820, 62)
            
            # Hover glow border
            border_color = card["color"] if is_hover else COLOR_GRID_LINE
            fill_color = (COLOR_PANEL_BG[0]+10, COLOR_PANEL_BG[1]+10, COLOR_PANEL_BG[2]+10) if is_hover else COLOR_PANEL_BG
            
            # Scale effect on hover
            if is_hover:
                card_rect = card_rect.inflate(6, 6)
                
            pygame.draw.rect(screen, fill_color, card_rect, border_radius=12)
            pygame.draw.rect(screen, border_color, card_rect, width=2, border_radius=12)
            
            # Draw Icon
            icon_surf = font_title.render(card["icon"], True, COLOR_TEXT)
            screen.blit(icon_surf, (card_rect.x + 20, card_rect.y + card_rect.height//2 - icon_surf.get_height()//2))
            
            # Draw Title & Desc
            t_surf = font_header.render(card["title"], True, COLOR_GOLD if is_hover else COLOR_TEXT)
            screen.blit(t_surf, (card_rect.x + 80, card_rect.y + 10))
            
            d_surf = font_text.render(card["desc"], True, COLOR_TEXT if is_hover else COLOR_MUTED_TEXT)
            screen.blit(d_surf, (card_rect.x + 80, card_rect.y + 34))

            # Arrow indicator
            arrow_surf = font_header.render(">", True, card["color"] if is_hover else COLOR_MUTED_TEXT)
            screen.blit(arrow_surf, (card_rect.x + card_rect.width - 30, card_rect.y + card_rect.height//2 - arrow_surf.get_height()//2))

# =========================================================================
# SECTION 2: 8-PUZZLE SCREEN (Lerp Slide & Glassmorphism)
# =========================================================================
class PuzzleScreen:
    def __init__(self):
        self.initial_state = [[1, 2, 3], [4, 0, 6], [7, 5, 8]]
        self.board = copy.deepcopy(self.initial_state)
        self.selected_algo = "BFS 2"
        self.algos = ["BFS 1", "BFS 2", "UCS", "DFS 1", "DFS 2", "Greedy H", "IDS 1", "IDS 2", "Greedy M", "A* H", "A* M", "IDA* H", "IDA* M"]
        self.stats = {"status": "Chờ lệnh", "time": "-", "steps": "-", "reached": "-", "length": "-"}
        self.solution_states = [self.board]
        self.playback_index = 0
        self.playback_paused = True
        self.last_update = time.time()
        
        # Tile visual positions for smooth Lerp slide
        self.tile_positions = {} # val -> (current_x, current_y)
        self.reset_tile_positions()
        
        # Setup UI Buttons
        self.buttons = []
        # Back to menu
        self.buttons.append(Button(40, 30, 160, 30, "<- Menu chính", lambda: set_screen("MENU")))
        
        # Algos Grid
        for i, algo in enumerate(self.algos):
            col = i % 3
            row = i // 3
            self.buttons.append(Button(520 + col * 130, 140 + row * 32, 120, 26, algo, self.set_algo, algo))
            
        # Presets & Actions
        self.buttons.append(Button(520, 310, 85, 30, "Easy", self.set_preset, "Easy"))
        self.buttons.append(Button(615, 310, 85, 30, "Medium", self.set_preset, "Medium"))
        self.buttons.append(Button(710, 310, 85, 30, "Hard", self.set_preset, "Hard"))
        self.buttons.append(Button(805, 310, 85, 30, "Random", self.generate_random))
        self.buttons.append(Button(520, 350, 375, 40, "GIẢI BÀI TOÁN (SOLVE)", self.solve))
        
        # Playback controls
        self.buttons.append(Button(40, 565, 90, 32, "Tua lại", self.reset_playback))
        self.buttons.append(Button(145, 565, 90, 32, "Bước lùi", self.step_back))
        self.buttons.append(Button(250, 565, 90, 32, "Play/Pause", self.toggle_play))
        self.buttons.append(Button(355, 565, 90, 32, "Bước tới", self.step_forward))

    def reset_tile_positions(self):
        # Calculate screen coordinates for grid positions
        # Board starts at x = 40, y = 100, size = 420
        cell_size = 400 // 3
        start_x, start_y = 50, 110
        for r in range(3):
            for c in range(3):
                val = self.board[r][c]
                self.tile_positions[val] = (start_x + c * cell_size, start_y + r * cell_size)

    def set_algo(self, name):
        self.selected_algo = name

    def set_preset(self, key):
        presets = {
            "Easy": [[1, 2, 3], [4, 0, 6], [7, 5, 8]],
            "Medium": [[1, 2, 3], [0, 4, 6], [7, 5, 8]],
            "Hard": [[1, 3, 5], [4, 2, 6], [0, 7, 8]]
        }
        self.board = copy.deepcopy(presets[key])
        self.initial_state = copy.deepcopy(presets[key])
        self.reset_playback()

    def generate_random(self):
        state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        def get_zero(s):
            for i in range(3):
                for j in range(3):
                    if s[i][j] == 0: return i, j
        last_zero = get_zero(state)
        for _ in range(15):
            x, y = last_zero
            possible = []
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 3 and 0 <= ny < 3: possible.append((nx, ny))
            nx, ny = random.choice(possible)
            state[x][y], state[nx][ny] = state[nx][ny], state[x][y]
            last_zero = (nx, ny)
        self.board = copy.deepcopy(state)
        self.initial_state = copy.deepcopy(state)
        self.reset_playback()

    def reset_playback(self):
        self.playback_index = 0
        self.playback_paused = True
        self.solution_states = [self.initial_state]
        self.board = copy.deepcopy(self.initial_state)
        self.reset_tile_positions()

    def toggle_play(self):
        self.playback_paused = not self.playback_paused

    def step_back(self):
        self.playback_paused = True
        if self.playback_index > 0:
            self.playback_index -= 1
            self.board = copy.deepcopy(self.solution_states[self.playback_index])

    def step_forward(self):
        self.playback_paused = True
        if self.playback_index < len(self.solution_states) - 1:
            self.playback_index += 1
            self.board = copy.deepcopy(self.solution_states[self.playback_index])

    def solve(self):
        self.reset_playback()
        self.stats["status"] = "Đang giải..."
        start = time.perf_counter()
        
        path, steps, reached, expanded = None, 0, 0, 0
        goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        
        if self.selected_algo == "BFS 1":
            path, steps, expanded, reached = bfs_way_1(self.initial_state, goal)
        elif self.selected_algo == "BFS 2":
            path, steps, expanded, reached = bfs_way_2(self.initial_state, goal)
        elif self.selected_algo == "DFS 1":
            path, steps, expanded, reached = dfs_way_1(self.initial_state, goal)
        elif self.selected_algo == "DFS 2":
            path, steps, expanded, reached = dfs_way_2(self.initial_state, goal)
        elif self.selected_algo == "IDS 1":
            path, depth, steps = ids_way_1(self.initial_state, goal)
            expanded, reached = steps, steps
        elif self.selected_algo == "IDS 2":
            path, depth, steps = ids_way_2(self.initial_state, goal)
            expanded, reached = steps, steps
        elif self.selected_algo == "UCS":
            path, cost, steps, expanded, reached = puzzle_ucs(self.initial_state, goal)
        elif self.selected_algo == "Greedy H":
            path, steps, expanded, reached = puzzle_greedy(self.initial_state, goal, puzzle_h_hamming)
        elif self.selected_algo == "Greedy M":
            path, steps, expanded, reached = puzzle_greedy(self.initial_state, goal, puzzle_h_manhattan)
        elif self.selected_algo == "A* H":
            path, cost, steps, expanded, reached = puzzle_astar(self.initial_state, goal, puzzle_h_hamming)
        elif self.selected_algo == "A* M":
            path, cost, steps, expanded, reached = puzzle_astar(self.initial_state, goal, puzzle_h_manhattan)
        elif self.selected_algo == "IDA* H":
            path, limit, steps = puzzle_idastar(self.initial_state, goal, puzzle_h_hamming)
            expanded, reached = steps, steps
        elif self.selected_algo == "IDA* M":
            path, limit, steps = puzzle_idastar(self.initial_state, goal, puzzle_h_manhattan)
            expanded, reached = steps, steps
            
        duration = (time.perf_counter() - start) * 1000
        
        if path is not None:
            self.solution_states = puzzle_get_sequence(self.initial_state, path)
            self.stats = {
                "status": "Đã giải xong!",
                "time": f"{duration:.2f} ms",
                "steps": str(steps),
                "reached": str(reached),
                "length": f"{len(path)} bước"
            }
            self.playback_paused = False
        else:
            self.stats = {
                "status": "Không có lời giải!",
                "time": f"{duration:.2f} ms",
                "steps": str(steps),
                "reached": str(reached),
                "length": "-"
            }

    def handle_event(self, event):
        pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for btn in self.buttons:
                    if btn.rect.collidepoint(pos):
                        btn.handle_click()
                        break

    def update(self):
        pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.check_hover(pos)
            
        # Playback timer
        if not self.playback_paused and self.playback_index < len(self.solution_states) - 1:
            now = time.time()
            if now - self.last_update >= 0.6:
                self.playback_index += 1
                self.board = copy.deepcopy(self.solution_states[self.playback_index])
                self.last_update = now
                
        # Lerp visual positions towards target grid positions
        cell_size = 400 // 3
        start_x, start_y = 50, 110
        for r in range(3):
            for c in range(3):
                val = self.board[r][c]
                target_x = start_x + c * cell_size
                target_y = start_y + r * cell_size
                
                curr_x, curr_y = self.tile_positions.get(val, (target_x, target_y))
                # Linear Interpolation (Lerp) - 20% closer each frame
                curr_x += (target_x - curr_x) * 0.20
                curr_y += (target_y - curr_y) * 0.20
                self.tile_positions[val] = (curr_x, curr_y)

    def draw(self, screen):
        # Draw Panel Background
        board_rect = pygame.Rect(40, 100, 420, 420)
        pygame.draw.rect(screen, COLOR_PANEL_BG, board_rect, border_radius=15)
        pygame.draw.rect(screen, COLOR_GRID_LINE, board_rect, width=2, border_radius=15)
        
        # Draw tiles smoothly using their current lerped positions
        cell_size = 400 // 3
        for val, (tx, ty) in self.tile_positions.items():
            if val == 0:
                continue # Skip empty tile (shows background)
                
            tile_rect = pygame.Rect(tx + 4, ty + 4, cell_size - 8, cell_size - 8)
            
            # Premium Glassmorphic look
            # Draw glow base
            pygame.draw.rect(screen, COLOR_CYAN, tile_rect, border_radius=12)
            # Specular glass border
            pygame.draw.rect(screen, COLOR_TEXT, tile_rect, width=2, border_radius=12)
            
            # Number Label
            num_surf = font_large_symbol.render(str(val), True, COLOR_TEXT)
            num_rect = num_surf.get_rect(center=tile_rect.center)
            screen.blit(num_surf, num_rect)
            
        # Draw Right Panel Info
        right_panel = pygame.Rect(500, 100, 415, 500)
        pygame.draw.rect(screen, COLOR_PANEL_BG, right_panel, border_radius=10)
        pygame.draw.rect(screen, COLOR_GRID_LINE, right_panel, width=1, border_radius=10)
        
        screen.blit(font_header.render("1. Chọn thuật toán giải bài toán", True, COLOR_GOLD), (520, 110))
        screen.blit(font_header.render("2. Chọn cấu hình ban đầu", True, COLOR_GOLD), (520, 280))
        screen.blit(font_header.render("3. Số liệu hiệu năng giải", True, COLOR_GOLD), (520, 400))
        
        # Display Stats
        stats_y = 425
        labels = [
            ("Trạng thái:", self.stats["status"]),
            ("Thời gian giải:", self.stats["time"]),
            ("Số bước lặp:", self.stats["steps"]),
            ("Nút đạt được:", self.stats["reached"]),
            ("Độ dài đường đi:", self.stats["length"])
        ]
        for idx, (lbl, val) in enumerate(labels):
            screen.blit(font_text.render(lbl, True, COLOR_TEXT), (530, stats_y + idx * 24))
            screen.blit(font_bold.render(val, True, COLOR_GOLD if val != "-" else COLOR_TEXT), (730, stats_y + idx * 24))
            
        # Playback Status Line
        playback_desc = f"Bước hiển thị: {self.playback_index} / {len(self.solution_states)-1}"
        screen.blit(font_bold.render(playback_desc, True, COLOR_TEXT), (40, 530))
        
        # Draw Buttons
        for btn in self.buttons:
            is_active = (btn.text == self.selected_algo)
            btn.draw(screen, is_active=is_active)

# =========================================================================
# SECTION 3: N-QUEENS SCREEN (Crown vector & Laser conflicts)
# =========================================================================
class NQueensScreen:
    def __init__(self):
        self.n = 8
        self.current_state = [random.randint(0, 7) for _ in range(8)]
        self.initial_state = list(self.current_state)
        self.selected_algo = "Steepest HC"
        self.algos = ["Simple HC", "Steepest HC", "Stochastic HC", "Random Restart", "Local Beam", "Simulated Ann."]
        self.stats = {"status": "Chờ lệnh", "time": "-", "steps": "-", "restarts": "-", "attacks": str(h_attack(self.current_state))}
        self.playback_history = [(self.current_state, h_attack(self.current_state))]
        self.playback_index = 0
        self.playback_paused = True
        self.last_update = time.time()
        
        # Smooth Vertical Lerp positions for queens
        self.queen_y_positions = [q * 50 for q in self.current_state] # 8 vertical coordinates
        
        # UI Buttons
        self.buttons = []
        self.buttons.append(Button(40, 30, 160, 30, "<- Menu chính", lambda: set_screen("MENU")))
        
        # Algos Grid
        for i, algo in enumerate(self.algos):
            col = i % 2
            row = i // 2
            self.buttons.append(Button(520 + col * 195, 140 + row * 38, 180, 30, algo, self.set_algo, algo))
            
        # Controls
        self.buttons.append(Button(520, 260, 180, 35, "TẠO NGẪU NHIÊN", self.generate_random))
        self.buttons.append(Button(715, 260, 180, 35, "GIẢI BÀI TOÁN", self.solve))
        
        # Playback controls
        self.buttons.append(Button(40, 565, 90, 32, "Tua lại", self.reset_playback))
        self.buttons.append(Button(145, 565, 90, 32, "Bước lùi", self.step_back))
        self.buttons.append(Button(250, 565, 90, 32, "Play/Pause", self.toggle_play))
        self.buttons.append(Button(355, 565, 90, 32, "Bước tới", self.step_forward))

    def set_algo(self, name):
        self.selected_algo = name

    def generate_random(self):
        self.current_state = [random.randint(0, 7) for _ in range(8)]
        self.initial_state = list(self.current_state)
        self.stats["attacks"] = str(h_attack(self.current_state))
        self.reset_playback()
        self.playback_history = [(self.current_state, h_attack(self.current_state))]

    def reset_playback(self):
        self.playback_index = 0
        self.playback_paused = True
        self.current_state = list(self.initial_state)

    def toggle_play(self):
        self.playback_paused = not self.playback_paused

    def step_back(self):
        self.playback_paused = True
        if self.playback_index > 0:
            self.playback_index -= 1
            self.current_state = list(self.playback_history[self.playback_index][0])

    def step_forward(self):
        self.playback_paused = True
        if self.playback_index < len(self.playback_history) - 1:
            self.playback_index += 1
            self.current_state = list(self.playback_history[self.playback_index][0])

    def solve(self):
        self.reset_playback()
        self.stats["status"] = "Đang giải..."
        start = time.perf_counter()
        
        best_state = None
        best_h = -1
        steps = 0
        restarts = 0
        history = []
        
        if self.selected_algo == "Simple HC":
            best_state, best_h, steps, history = simple_hill_climbing(self.initial_state)
        elif self.selected_algo == "Steepest HC":
            best_state, best_h, steps, history = steepest_ascent_hill_climbing(self.initial_state)
        elif self.selected_algo == "Stochastic HC":
            best_state, best_h, steps, history = stochastic_hill_climbing(self.initial_state)
        elif self.selected_algo == "Random Restart":
            best_state, best_h, steps, restarts, history = random_restart_hill_climbing(8, 100)
        elif self.selected_algo == "Local Beam":
            best_state, best_h, steps, history = local_beam_search(8, 3, 100)
        elif self.selected_algo == "Simulated Ann.":
            best_state, best_h, steps, history = simulated_annealing(self.initial_state)
            
        duration = (time.perf_counter() - start) * 1000
        self.playback_history = history
        
        self.stats = {
            "status": "Giải thành công!" if best_h == 0 else "Kẹt cục bộ",
            "time": f"{duration:.2f} ms",
            "steps": str(steps),
            "restarts": str(restarts) if self.selected_algo == "Random Restart" else "-",
            "attacks": str(best_h)
        }
        self.playback_paused = False

    def handle_event(self, event):
        pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for btn in self.buttons:
                    if btn.rect.collidepoint(pos):
                        btn.handle_click()
                        break

    def update(self):
        pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.check_hover(pos)
            
        # Playback
        if not self.playback_paused and self.playback_index < len(self.playback_history) - 1:
            now = time.time()
            if now - self.last_update >= 0.4:
                self.playback_index += 1
                self.current_state = list(self.playback_history[self.playback_index][0])
                self.last_update = now
                
        # Lerp Y positions of queens
        # Board start_y is 110, cell size is 50
        for i in range(8):
            target_y = 110 + self.current_state[i] * 50
            curr_y = self.queen_y_positions[i]
            curr_y += (target_y - curr_y) * 0.20
            self.queen_y_positions[i] = curr_y

    def draw_crown(self, screen, rect):
        # Draw highly detailed royal gold crown
        # Base bar
        pygame.draw.rect(screen, COLOR_GOLD, (rect.x + 8, rect.y + rect.height - 12, rect.width - 16, 6), border_radius=2)
        # Crown peaks (3 triangles)
        pts_left = [(rect.x+8, rect.y+rect.height-12), (rect.x+15, rect.y+10), (rect.x+22, rect.y+rect.height-12)]
        pts_mid = [(rect.x+20, rect.y+rect.height-12), (rect.x+rect.width//2, rect.y+6), (rect.x+rect.width-20, rect.y+rect.height-12)]
        pts_right = [(rect.x+rect.width-22, rect.y+rect.height-12), (rect.x+rect.width-15, rect.y+10), (rect.x+rect.width-8, rect.y+rect.height-12)]
        
        pygame.draw.polygon(screen, COLOR_GOLD, pts_left)
        pygame.draw.polygon(screen, COLOR_GOLD, pts_mid)
        pygame.draw.polygon(screen, COLOR_GOLD, pts_right)
        
        # Jewels (Circles on peaks)
        pygame.draw.circle(screen, COLOR_RED, (rect.x+15, 10), 3)
        pygame.draw.circle(screen, COLOR_CYAN, (rect.width//2 + rect.x, 6), 4)
        pygame.draw.circle(screen, COLOR_RED, (rect.x+rect.width-15, 10), 3)

    def draw(self, screen):
        # Draw Chessboard Panel
        board_rect = pygame.Rect(40, 100, 420, 420)
        pygame.draw.rect(screen, COLOR_PANEL_BG, board_rect, border_radius=10)
        
        cell_size = 400 // 8
        start_x, start_y = 50, 110
        for r in range(8):
            for c in range(8):
                rect = pygame.Rect(start_x + c * cell_size, start_y + r * cell_size, cell_size, cell_size)
                color = (236, 240, 241) if (r + c) % 2 == 0 else (127, 140, 141)
                pygame.draw.rect(screen, color, rect)
                
        # Draw laser conflict lines dynamically
        # Find all attacking pairs in the current state
        attacks = []
        for i in range(8):
            for j in range(i+1, 8):
                if self.current_state[i] == self.current_state[j] or abs(self.current_state[i] - self.current_state[j]) == abs(i - j):
                    attacks.append((i, j))
                    
        # Render glowing laser lines
        for i, j in attacks:
            # Pulse intensity based on time
            alpha = int(120 + 80 * math.sin(time.time() * 15))
            alpha = max(0, min(255, alpha))
            
            # Start and End points using current lerped positions for fluid animation
            x1 = start_x + i * cell_size + cell_size//2
            y1 = self.queen_y_positions[i] + cell_size//2
            x2 = start_x + j * cell_size + cell_size//2
            y2 = self.queen_y_positions[j] + cell_size//2
            
            # Thick laser glow
            pygame.draw.line(screen, (COLOR_RED[0], COLOR_RED[1], COLOR_RED[2], alpha), (x1, y1), (x2, y2), width=4)
            pygame.draw.line(screen, COLOR_TEXT, (x1, y1), (x2, y2), width=1)
            
        # Draw Queens using their lerped visual positions
        for i in range(8):
            qy = self.queen_y_positions[i]
            qx = start_x + i * cell_size
            rect = pygame.Rect(qx, qy, cell_size, cell_size)
            self.draw_crown(screen, rect)
            
        # Draw Right Panel
        right_panel = pygame.Rect(500, 100, 415, 500)
        pygame.draw.rect(screen, COLOR_PANEL_BG, right_panel, border_radius=10)
        pygame.draw.rect(screen, COLOR_GRID_LINE, right_panel, width=1, border_radius=10)
        
        screen.blit(font_header.render("1. Chọn thuật toán tìm kiếm cục bộ", True, COLOR_GOLD), (520, 110))
        screen.blit(font_header.render("2. Điều khiển giải thuật", True, COLOR_GOLD), (520, 230))
        screen.blit(font_header.render("3. Số liệu thống kê", True, COLOR_GOLD), (520, 315))
        
        # Display Stats
        stats_y = 340
        labels = [
            ("Trạng thái giải:", self.stats["status"]),
            ("Thời gian giải:", self.stats["time"]),
            ("Tổng số bước lặp:", self.stats["steps"]),
            ("Số lần khởi động lại:", self.stats["restarts"]),
            ("Số cặp tấn công (H):", self.stats["attacks"])
        ]
        for idx, (lbl, val) in enumerate(labels):
            screen.blit(font_text.render(lbl, True, COLOR_TEXT), (530, stats_y + idx * 24))
            screen.blit(font_bold.render(val, True, COLOR_GOLD if val != "-" else COLOR_TEXT), (730, stats_y + idx * 24))
            
        # Playback status
        pb_desc = f"Bước hiển thị: {self.playback_index} / {len(self.playback_history)-1} | Cặp tấn công: {h_attack(self.current_state)}"
        screen.blit(font_bold.render(pb_desc, True, COLOR_TEXT), (40, 530))
        
        # Draw Buttons
        for btn in self.buttons:
            is_active = (btn.text == self.selected_algo)
            btn.draw(screen, is_active=is_active)

# =========================================================================
# SECTION 4: VACUUM CLEANER SCREEN (Robot metallic & Dust vortex particles)
# =========================================================================
class VacuumScreen:
    def __init__(self):
        self.rows, self.cols = 6, 6
        self.robot_pos = (0, 0)
        self.dirt_positions = {(1, 1), (2, 3), (4, 1), (3, 5)}
        self.obstacles = {(1, 2), (2, 2), (4, 4)}
        self.tool_mode = "dirt"
        self.selected_algo = "A*"
        self.algos = ["BFS", "DFS", "IDS", "UCS", "Greedy", "A*", "IDA*", "Hill Climbing"]
        self.stats = {"status": "Chờ lệnh", "time": "-", "steps": "-", "reached": "-", "cost": "-"}
        self.playback_history = [((self.robot_pos, frozenset(self.dirt_positions)))]
        self.playback_index = 0
        self.playback_paused = True
        self.last_update = time.time()
        
        # Smooth Lerp coordinates for robot position
        self.robot_visual_x = 50.0
        self.robot_visual_y = 110.0
        
        # Vortex particles system for Suck effect
        self.particles = [] # list of {"x", "y", "vx", "vy", "life"}
        
        # UI Buttons
        self.buttons = []
        self.buttons.append(Button(40, 30, 160, 30, "<- Menu chính", lambda: set_screen("MENU")))
        
        # Algos Grid
        for i, algo in enumerate(self.algos):
            col = i % 2
            row = i // 2
            self.buttons.append(Button(520 + col * 195, 140 + row * 34, 180, 26, algo, self.set_algo, algo))
            
        # Tool modes & Actions
        self.buttons.append(Button(520, 260, 120, 26, "Cọ: Robot", self.set_tool, "robot"))
        self.buttons.append(Button(650, 260, 120, 26, "Cọ: Rác", self.set_tool, "dirt"))
        self.buttons.append(Button(780, 260, 120, 26, "Cọ: Tường", self.set_tool, "obstacle"))
        
        self.buttons.append(Button(520, 300, 120, 32, "Ngẫu nhiên", self.generate_random))
        self.buttons.append(Button(650, 300, 120, 32, "Xóa sạch", self.clear_grid))
        self.buttons.append(Button(780, 300, 120, 32, "GIẢI (SOLVE)", self.solve))
        
        # Playback controls
        self.buttons.append(Button(40, 565, 90, 32, "Tua lại", self.reset_playback))
        self.buttons.append(Button(145, 565, 90, 32, "Bước lùi", self.step_back))
        self.buttons.append(Button(250, 565, 90, 32, "Play/Pause", self.toggle_play))
        self.buttons.append(Button(355, 565, 90, 32, "Bước tới", self.step_forward))

    def set_algo(self, name):
        self.selected_algo = name

    def set_tool(self, mode):
        self.tool_mode = mode

    def clear_grid(self):
        self.dirt_positions = set()
        self.obstacles = set()
        self.reset_playback()
        self.playback_history = [((self.robot_pos, frozenset(self.dirt_positions)))]

    def generate_random(self):
        self.clear_grid()
        self.robot_pos = (random.randint(0, 5), random.randint(0, 5))
        for r in range(6):
            for c in range(6):
                if (r, c) != self.robot_pos:
                    if random.random() < 0.25:
                        self.dirt_positions.add((r, c))
                    elif random.random() < 0.15:
                        self.obstacles.add((r, c))
        self.reset_playback()
        self.playback_history = [((self.robot_pos, frozenset(self.dirt_positions)))]

    def reset_playback(self):
        self.playback_index = 0
        self.playback_paused = True

    def toggle_play(self):
        self.playback_paused = not self.playback_paused

    def step_back(self):
        self.playback_paused = True
        if self.playback_index > 0:
            self.playback_index -= 1

    def step_forward(self):
        self.playback_paused = True
        if self.playback_index < len(self.playback_history) - 1:
            self.playback_index += 1

    def solve(self):
        self.reset_playback()
        self.stats["status"] = "Đang giải..."
        init_state = (self.robot_pos, frozenset(self.dirt_positions))
        grid_size = (6, 6)
        
        start = time.perf_counter()
        path, steps, reached, cost = None, 0, 0, 0
        
        if self.selected_algo == "BFS":
            path, steps, reached = vac_bfs(init_state, grid_size, self.obstacles)
            cost = len(path) if path else 0
        elif self.selected_algo == "DFS":
            path, steps, reached = vac_dfs(init_state, grid_size, self.obstacles)
            cost = len(path) if path else 0
        elif self.selected_algo == "IDS":
            path, depth, steps = vac_ids(init_state, grid_size, self.obstacles)
            reached = steps
            cost = len(path) if path else 0
        elif self.selected_algo == "UCS":
            path, cost, steps, reached = vac_ucs(init_state, grid_size, self.obstacles)
        elif self.selected_algo == "Greedy":
            path, steps, reached = vac_greedy(init_state, grid_size, self.obstacles)
            cost = len(path) if path else 0
        elif self.selected_algo == "A*":
            path, cost, steps, reached = vac_astar(init_state, grid_size, self.obstacles)
        elif self.selected_algo == "IDA*":
            path, limit, steps = vac_idastar(init_state, grid_size, self.obstacles)
            reached = steps
            cost = len(path) if path else 0
        elif self.selected_algo == "Hill Climbing":
            path, success, steps, reached = vac_hc(init_state, grid_size, self.obstacles)
            cost = len(path) if path else 0
            if not success:
                self.stats["status"] = "Kẹt cục bộ!"
                self.playback_history = [init_state]
                curr = init_state
                for act in path:
                    for action, next_s, _ in vac_get_neighbors(curr, grid_size, self.obstacles):
                        if action == act:
                            curr = next_s
                            self.playback_history.append(curr)
                            break
                duration = (time.perf_counter() - start) * 1000
                self.stats = {"status": "Kẹt cực trị!", "time": f"{duration:.2f} ms", "steps": str(steps), "reached": str(reached), "cost": f"{cost} bước"}
                self.playback_paused = False
                return
                
        duration = (time.perf_counter() - start) * 1000
        
        if path is not None:
            self.playback_history = [init_state]
            curr = init_state
            for act in path:
                for action, next_s, _ in vac_get_neighbors(curr, grid_size, self.obstacles):
                    if action == act:
                        curr = next_s
                        self.playback_history.append(curr)
                        break
            self.stats = {
                "status": "Đã giải xong!",
                "time": f"{duration:.2f} ms",
                "steps": str(steps),
                "reached": str(reached),
                "cost": f"{cost} bước"
            }
            self.playback_paused = False
        else:
            self.stats = {
                "status": "Không có lời giải!",
                "time": f"{duration:.2f} ms",
                "steps": str(steps),
                "reached": str(reached),
                "cost": "-"
            }

    def trigger_suck_particles(self, rx, ry):
        # Spawn particles swirling towards center
        for _ in range(25):
            angle = random.random() * math.pi * 2
            dist = random.randint(30, 60)
            self.particles.append({
                "x": rx + math.cos(angle) * dist,
                "y": ry + math.sin(angle) * dist,
                "target_x": rx,
                "target_y": ry,
                "speed": random.uniform(2.5, 4.5),
                "color": random.choice([COLOR_GOLD, COLOR_RED, COLOR_MUTED_TEXT])
            })

    def handle_event(self, event):
        pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked = False
                for btn in self.buttons:
                    if btn.rect.collidepoint(pos):
                        btn.handle_click()
                        clicked = True
                        break
                
                # Grid Click interaction
                board_rect = pygame.Rect(40, 100, 420, 420)
                if not clicked and board_rect.collidepoint(pos):
                    cell_size = 400 // 6
                    col = (pos[0] - 50) // cell_size
                    row = (pos[1] - 110) // cell_size
                    if 0 <= row < 6 and 0 <= col < 6:
                        grid_pos = (row, col)
                        if self.tool_mode == "robot":
                            if grid_pos not in self.obstacles:
                                self.robot_pos = grid_pos
                                self.reset_playback()
                                self.playback_history = [(self.robot_pos, frozenset(self.dirt_positions))]
                        elif self.tool_mode == "dirt":
                            if grid_pos not in self.obstacles and grid_pos != self.robot_pos:
                                if grid_pos in self.dirt_positions: self.dirt_positions.remove(grid_pos)
                                else: self.dirt_positions.add(grid_pos)
                                self.reset_playback()
                                self.playback_history = [(self.robot_pos, frozenset(self.dirt_positions))]
                        elif self.tool_mode == "obstacle":
                            if grid_pos != self.robot_pos:
                                if grid_pos in self.obstacles: self.obstacles.remove(grid_pos)
                                else:
                                    self.obstacles.add(grid_pos)
                                    if grid_pos in self.dirt_positions: self.dirt_positions.remove(grid_pos)
                                self.reset_playback()
                                self.playback_history = [(self.robot_pos, frozenset(self.dirt_positions))]

    def update(self):
        pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.check_hover(pos)
            
        # Playback updates
        if not self.playback_paused and self.playback_index < len(self.playback_history) - 1:
            now = time.time()
            if now - self.last_update >= 0.5:
                # If next action is HÚT, trigger vortex particles
                prev_robot, prev_dirt = self.playback_history[self.playback_index]
                next_robot, next_dirt = self.playback_history[self.playback_index + 1]
                if len(next_dirt) < len(prev_dirt):
                    # Robot is cleaning -> trigger dust particles
                    cell_size = 400 // 6
                    rx = 50 + prev_robot[1] * cell_size + cell_size//2
                    ry = 110 + prev_robot[0] * cell_size + cell_size//2
                    self.trigger_suck_particles(rx, ry)
                self.playback_index += 1
                self.last_update = now
                
        # Lerp robot visual coordinates
        if self.playback_index < len(self.playback_history):
            cr, cc = self.playback_history[self.playback_index][0]
        else:
            cr, cc = self.robot_pos
        cell_size = 400 // 6
        target_x = 50 + cc * cell_size + cell_size//2
        target_y = 110 + cr * cell_size + cell_size//2
        
        self.robot_visual_x += (target_x - self.robot_visual_x) * 0.15
        self.robot_visual_y += (target_y - self.robot_visual_y) * 0.15
        
        # Update particles
        for p in list(self.particles):
            dx = p["target_x"] - p["x"]
            dy = p["target_y"] - p["y"]
            dist = math.sqrt(dx**2 + dy**2)
            if dist < 4:
                self.particles.remove(p)
            else:
                p["x"] += (dx / dist) * p["speed"]
                p["y"] += (dy / dist) * p["speed"]

    def draw_robot(self, screen, rx, ry, cell_size):
        # Draw detailed metallic robot vacuum véc-tơ
        # Soft shadow
        pygame.draw.circle(screen, (10, 14, 23), (rx+2, ry+2), cell_size//2 - 6)
        # Metallic outer ring
        pygame.draw.circle(screen, COLOR_OBSTACLE, (rx, ry), cell_size//2 - 6)
        pygame.draw.circle(screen, (50, 60, 80), (rx, ry), cell_size//2 - 8)
        # Glowing Cyan visor
        start_angle = time.time() * 3
        pygame.draw.arc(screen, COLOR_CYAN, (rx - cell_size//3, ry - cell_size//3, cell_size*2//3, cell_size*2//3), start_angle, start_angle + 1.2, width=3)
        # Blinking central status LED
        led_color = COLOR_BUTTON_ACTIVE if int(time.time()*3)%2 == 0 else COLOR_RED
        pygame.draw.circle(screen, led_color, (rx, ry), 4)

    def draw(self, screen):
        # Draw Grid Panel
        board_rect = pygame.Rect(40, 100, 420, 420)
        pygame.draw.rect(screen, COLOR_PANEL_BG, board_rect, border_radius=15)
        pygame.draw.rect(screen, COLOR_GRID_LINE, board_rect, width=2, border_radius=15)
        
        cell_size = 400 // 6
        start_x, start_y = 50, 110
        
        # Get current state from playback history
        if self.playback_index < len(self.playback_history):
            cr, cc = self.playback_history[self.playback_index][0]
            current_dirts = self.playback_history[self.playback_index][1]
        else:
            cr, cc = self.robot_pos
            current_dirts = frozenset(self.dirt_positions)
            
        for r in range(6):
            for c in range(6):
                rect = pygame.Rect(start_x + c * cell_size, start_y + r * cell_size, cell_size, cell_size)
                
                # Base Clean vs Wall
                if (r, c) in self.obstacles:
                    # Draw detailed brick wall véc-tơ
                    pygame.draw.rect(screen, COLOR_OBSTACLE, rect.inflate(-4, -4), border_radius=6)
                    # Brick bevel outline
                    pygame.draw.rect(screen, (90, 100, 110), rect.inflate(-4, -4), width=2, border_radius=6)
                else:
                    pygame.draw.rect(screen, COLOR_CLEAN, rect.inflate(-4, -4), border_radius=6)
                    
                    # Draw Dirt pile véc-tơ if present
                    if (r, c) in current_dirts:
                        # Draw brown dirt piles with multiple specks
                        pygame.draw.circle(screen, COLOR_DIRT, rect.center, cell_size//4)
                        pygame.draw.circle(screen, (150, 90, 30), (rect.center[0]-4, rect.center[1]-3), 4)
                        pygame.draw.circle(screen, (150, 90, 30), (rect.center[0]+5, rect.center[1]+3), 3)
                        dirt_lbl = font_visual.render("Rác", True, COLOR_TEXT)
                        screen.blit(dirt_lbl, dirt_lbl.get_rect(center=rect.center))
                        
                pygame.draw.rect(screen, COLOR_GRID_LINE, rect, width=1)
                
        # Draw vortex particles
        for p in self.particles:
            pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), 3)
            
        # Draw robot at its current lerped visual position
        self.draw_robot(screen, int(self.robot_visual_x), int(self.robot_visual_y), cell_size)
        
        # Draw Right panel
        right_panel = pygame.Rect(500, 100, 415, 500)
        pygame.draw.rect(screen, COLOR_PANEL_BG, right_panel, border_radius=10)
        pygame.draw.rect(screen, COLOR_GRID_LINE, right_panel, width=1, border_radius=10)
        
        screen.blit(font_header.render("1. Chọn thuật toán tìm kiếm Robot", True, COLOR_GOLD), (520, 110))
        screen.blit(font_header.render("2. Chọn cọ vẽ & Tác vụ bản đồ", True, COLOR_GOLD), (520, 235))
        screen.blit(font_header.render("3. Số liệu thống kê", True, COLOR_GOLD), (520, 350))
        
        # Highlights brush borders
        brush_tools = {"robot": btn_t_robot, "dirt": btn_t_dirt, "obstacle": btn_t_obs}
        for mode, btn in brush_tools.items():
            if self.tool_mode == mode:
                pygame.draw.rect(screen, COLOR_GOLD, btn.rect.inflate(4, 4), width=2, border_radius=8)

        # Display Stats
        stats_y = 375
        labels = [
            ("Trạng thái giải:", self.stats["status"]),
            ("Thời gian giải:", self.stats["time"]),
            ("Tổng số bước lặp:", self.stats["steps"]),
            ("Số nút đã mở rộng:", self.stats["reached"]),
            ("Chi phí đường đi:", self.stats["cost"])
        ]
        for idx, (lbl, val) in enumerate(labels):
            screen.blit(font_text.render(lbl, True, COLOR_TEXT), (530, stats_y + idx * 24))
            screen.blit(font_bold.render(val, True, COLOR_GOLD if val != "-" else COLOR_TEXT), (730, stats_y + idx * 24))
            
        # Playback status line
        pb_desc = f"Bước hiển thị: {self.playback_index} / {len(self.playback_history)-1}"
        screen.blit(font_bold.render(pb_desc, True, COLOR_TEXT), (40, 530))
        
        # Draw Buttons
        for btn in self.buttons:
            is_active = (btn.text == self.selected_algo)
            btn.draw(screen, is_active=is_active)

# =========================================================================
# SECTION 5: MAP COLORING SCREEN (Jade sphere nodes & Edge laser pulses)
# =========================================================================
class MapColoringScreen:
    def __init__(self):
        self.nodes = {}
        self.adj = {}
        self.node_counter = 1
        self.tool_mode = "add_node"
        self.selected_first = None
        self.selected_algo = "Backtracking"
        self.algos = ["Backtracking", "Forward Check", "AC-3", "Min-Conflicts"]
        self.num_colors = 3
        self.stats = {"status": "Chờ lệnh", "time": "-", "steps": "-", "backtracks": "-"}
        self.playback_history = []
        self.playback_index = 0
        self.playback_paused = True
        self.last_update = time.time()
        
        # Laser pulses running along constraint edges
        # List of {"start_x", "start_y", "end_x", "end_y", "progress"}
        self.edge_pulses = []
        
        # UI Buttons
        self.buttons = []
        self.buttons.append(Button(40, 30, 160, 30, "<- Menu chính", lambda: set_screen("MENU")))
        
        # Algos Grid
        for i, algo in enumerate(self.algos):
            col = i % 2
            row = i // 2
            self.buttons.append(Button(520 + col * 195, 140 + row * 36, 180, 28, algo, self.set_algo, algo))
            
        # Colors & Tool selections
        self.buttons.append(Button(520, 200, 180, 28, "3 màu (RGB)", self.set_colors, 3))
        self.buttons.append(Button(715, 200, 180, 28, "4 màu (RGBY)", self.set_colors, 4))
        
        self.buttons.append(Button(520, 255, 120, 28, "Vẽ Đỉnh (Node)", self.set_tool, "add_node"))
        self.buttons.append(Button(650, 255, 120, 28, "Vẽ Cạnh (Edge)", self.set_tool, "add_edge"))
        self.buttons.append(Button(780, 255, 120, 28, "Xóa Đỉnh", self.set_tool, "delete_node"))
        
        self.buttons.append(Button(520, 300, 85, 30, "Bản đồ Úc", self.load_aus))
        self.buttons.append(Button(615, 300, 85, 30, "Đồ thị mẫu", self.load_tri))
        self.buttons.append(Button(710, 300, 85, 30, "Xóa hết", self.clear))
        self.buttons.append(Button(805, 300, 85, 30, "TÔ MÀU", self.solve))
        
        # Playback controls
        self.buttons.append(Button(40, 565, 90, 32, "Tua lại", self.reset_playback))
        self.buttons.append(Button(145, 565, 90, 32, "Bước lùi", self.step_back))
        self.buttons.append(Button(250, 565, 90, 32, "Play/Pause", self.toggle_play))
        self.buttons.append(Button(355, 565, 90, 32, "Bước tới", self.step_forward))

    def set_algo(self, name):
        self.selected_algo = name

    def set_colors(self, count):
        self.num_colors = count

    def set_tool(self, mode):
        self.tool_mode = mode
        self.selected_first = None

    def clear(self):
        self.nodes = {}
        self.adj = {}
        self.node_counter = 1
        self.selected_first = None
        self.reset_playback()

    def load_aus(self):
        self.clear()
        self.nodes = {"WA": (110, 210), "NT": (210, 140), "SA": (230, 280), "Q": (320, 160), "NSW": (330, 290), "V": (270, 360), "T": (290, 440)}
        self.adj = {"WA": ["NT", "SA"], "NT": ["WA", "Q", "SA"], "Q": ["NT", "NSW", "SA"], "NSW": ["Q", "V", "SA"], "V": ["NSW", "SA"], "SA": ["WA", "NT", "Q", "NSW", "V"], "T": []}
        self.node_counter = 8
        self.reset_playback()

    def load_tri(self):
        self.clear()
        self.nodes = {"N1": (220, 120), "N2": (120, 280), "N3": (320, 280), "N4": (220, 400), "N5": (220, 260)}
        self.adj = {"N1": ["N2", "N3", "N5"], "N2": ["N1", "N4", "N5"], "N3": ["N1", "N4", "N5"], "N4": ["N2", "N3", "N5"], "N5": ["N1", "N2", "N3", "N4"]}
        self.node_counter = 6
        self.reset_playback()

    def reset_playback(self):
        self.playback_index = 0
        self.playback_paused = True
        self.edge_pulses = []

    def toggle_play(self):
        self.playback_paused = not self.playback_paused

    def step_back(self):
        self.playback_paused = True
        if self.playback_index > 0:
            self.playback_index -= 1

    def step_forward(self):
        self.playback_paused = True
        if self.playback_index < len(self.playback_history) - 1:
            self.playback_index += 1

    def trigger_edge_pulse(self, u, v):
        # Spawns glowing energy pulse traveling between nodes
        x1, y1 = self.nodes[u]
        x2, y2 = self.nodes[v]
        self.edge_pulses.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2, "p": 0.0})

    def solve(self):
        if not self.nodes:
            self.stats["status"] = "Lỗi: Không có đỉnh!"
            return
            
        self.reset_playback()
        self.stats["status"] = "Đang giải..."
        
        node_list = list(self.nodes.keys())
        clean_adj = {n: [] for n in node_list}
        for u in self.adj:
            for v in self.adj[u]:
                if u in node_list and v in node_list:
                    if v not in clean_adj[u]: clean_adj[u].append(v)
                    if u not in clean_adj[v]: clean_adj[v].append(u)
                    
        start = time.perf_counter()
        res, steps, backtracks, history = None, 0, 0, []
        
        if self.selected_algo == "Backtracking":
            res, steps, backtracks, history = solve_backtracking(node_list, clean_adj, self.num_colors)
        elif self.selected_algo == "Forward Check":
            res, steps, backtracks, history = solve_forward_checking(node_list, clean_adj, self.num_colors)
        elif self.selected_algo == "AC-3":
            res, steps, backtracks, history = solve_ac3(node_list, clean_adj, self.num_colors)
        elif self.selected_algo == "Min-Conflicts":
            res, steps, history = solve_min_conflicts(node_list, clean_adj, self.num_colors)
            backtracks = 0
            
        duration = (time.perf_counter() - start) * 1000
        
        if res is not None:
            self.stats = {"status": "Tô màu thành công!", "time": f"{duration:.2f} ms", "steps": str(steps), "backtracks": str(backtracks)}
            self.playback_history = history
            self.playback_paused = False
        else:
            self.stats = {"status": "Không có lời giải!", "time": f"{duration:.2f} ms", "steps": str(steps), "backtracks": str(backtracks)}
            self.playback_history = history
            self.playback_paused = False

    def handle_event(self, event):
        pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked = False
                for btn in self.buttons:
                    if btn.rect.collidepoint(pos):
                        btn.handle_click()
                        clicked = True
                        break
                        
                canvas_rect = pygame.Rect(40, 100, 420, 420)
                if not clicked and canvas_rect.collidepoint(pos):
                    clicked_node = None
                    for nid, (nx, ny) in self.nodes.items():
                        dist = math.sqrt((pos[0] - nx)**2 + (pos[1] - ny)**2)
                        if dist <= 20:
                            clicked_node = nid
                            break
                            
                    if self.tool_mode == "add_node":
                        if clicked_node is None:
                            new_id = f"N{self.node_counter}"
                            self.nodes[new_id] = pos
                            self.adj[new_id] = []
                            self.node_counter += 1
                            self.reset_playback()
                    elif self.tool_mode == "add_edge":
                        if clicked_node is not None:
                            if self.selected_first is None:
                                self.selected_first = clicked_node
                            else:
                                if self.selected_first != clicked_node:
                                    if clicked_node not in self.adj[self.selected_first]:
                                        self.adj[self.selected_first].append(clicked_node)
                                    if self.selected_first not in self.adj[clicked_node]:
                                        self.adj[clicked_node].append(self.selected_first)
                                self.selected_first = None
                                self.reset_playback()
                        else:
                            self.selected_first = None
                    elif self.tool_mode == "delete_node":
                        if clicked_node is not None:
                            del self.nodes[clicked_node]
                            if clicked_node in self.adj: del self.adj[clicked_node]
                            for u in self.adj:
                                if clicked_node in self.adj[u]: self.adj[u].remove(clicked_node)
                            self.reset_playback()

    def update(self):
        pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.check_hover(pos)
            
        # Playback updates
        if not self.playback_paused and self.playback_index < len(self.playback_history) - 1:
            now = time.time()
            if now - self.last_update >= 0.5:
                # Trigger edge pulse for visual check
                curr_assign = self.playback_history[self.playback_index]
                next_assign = self.playback_history[self.playback_index + 1]
                # Find which node changed
                for node_id in next_assign:
                    if curr_assign.get(node_id) != next_assign[node_id]:
                        # Changed node, check constraints with neighbors
                        for neighbor in self.adj.get(node_id, []):
                            if neighbor in self.nodes:
                                self.trigger_edge_pulse(node_id, neighbor)
                self.playback_index += 1
                self.last_update = now
                
        # Update edge pulses
        for pulse in list(self.edge_pulses):
            pulse["p"] += 0.08
            if pulse["p"] >= 1.0:
                self.edge_pulses.remove(pulse)

    def draw(self, screen):
        # Draw Canvas Panel
        board_rect = pygame.Rect(40, 100, 420, 420)
        pygame.draw.rect(screen, COLOR_PANEL_BG, board_rect, border_radius=15)
        pygame.draw.rect(screen, COLOR_GRID_LINE, board_rect, width=2, border_radius=15)
        
        # Draw constraint edges
        drawn = set()
        for u in self.adj:
            for v in self.adj[u]:
                edge = tuple(sorted((u, v)))
                if edge not in drawn and u in self.nodes and v in nodes:
                    pygame.draw.line(screen, COLOR_GRID_LINE, self.nodes[u], self.nodes[v], width=3)
                    drawn.add(edge)
                    
        # Draw pulsing laser constraints
        for pulse in self.edge_pulses:
            px = pulse["x1"] + (pulse["x2"] - pulse["x1"]) * pulse["p"]
            py = pulse["y1"] + (pulse["y2"] - pulse["y1"]) * pulse["p"]
            pygame.draw.circle(screen, COLOR_GOLD, (int(px), int(py)), 6)
            pygame.draw.circle(screen, COLOR_TEXT, (int(px), int(py)), 3)
            
        # Draw nodes as glowing Jade/gradient spheres
        current_assign = {}
        if len(self.playback_history) > 0 and self.playback_index < len(self.playback_history):
            current_assign = self.playback_history[self.playback_index]
            
        for nid, (nx, ny) in self.nodes.items():
            color_name = current_assign.get(nid)
            node_color = COLOR_MAP.get(color_name, COLOR_UNASSIGNED)
            
            # Selection highlight for drawing edges
            if self.selected_first == nid:
                pygame.draw.circle(screen, COLOR_GOLD, (nx, ny), 25)
                
            # Specular sphere effect: Concentric circles of lighter shade
            pygame.draw.circle(screen, node_color, (nx, ny), 20)
            lighter_color = (min(255, node_color[0]+35), min(255, node_color[1]+35), min(255, node_color[2]+35))
            pygame.draw.circle(screen, lighter_color, (nx-4, ny-4), 8)
            pygame.draw.circle(screen, COLOR_TEXT, (nx, ny), 20, width=2)
            
            # Label
            lbl = font_node.render(nid, True, COLOR_TEXT)
            screen.blit(lbl, lbl.get_rect(center=(nx, ny)))
            
        # Right Panel Info
        right_panel = pygame.Rect(500, 100, 415, 500)
        pygame.draw.rect(screen, COLOR_PANEL_BG, right_panel, border_radius=10)
        pygame.draw.rect(screen, COLOR_GRID_LINE, right_panel, width=1, border_radius=10)
        
        screen.blit(font_header.render("1. Chọn thuật toán CSP giải quyết", True, COLOR_GOLD), (520, 110))
        screen.blit(font_header.render("2. Chọn cọ vẽ & Bản đồ mẫu", True, COLOR_GOLD), (520, 235))
        screen.blit(font_header.render("3. Số liệu thống kê", True, COLOR_GOLD), (520, 350))
        
        # Highlight active selector buttons
        if self.num_colors == 3: pygame.draw.rect(screen, COLOR_GOLD, btn_col3.rect.inflate(4, 4), width=2, border_radius=8)
        else: pygame.draw.rect(screen, COLOR_GOLD, btn_col4.rect.inflate(4, 4), width=2, border_radius=8)
        
        brush_tools = {"add_node": btn_b_node, "add_edge": btn_b_edge, "delete_node": btn_b_del}
        for mode, btn in brush_tools.items():
            if self.tool_mode == mode:
                pygame.draw.rect(screen, COLOR_GOLD, btn.rect.inflate(4, 4), width=2, border_radius=8)

        # Display Stats
        stats_y = 375
        labels = [
            ("Trạng thái giải:", self.stats["status"]),
            ("Thời gian giải:", self.stats["time"]),
            ("Tổng số bước gán:", self.stats["steps"]),
            ("Số lần quay lui (backtracks):", self.stats["backtracks"])
        ]
        for idx, (lbl, val) in enumerate(labels):
            screen.blit(font_text.render(lbl, True, COLOR_TEXT), (530, stats_y + idx * 24))
            screen.blit(font_bold.render(val, True, COLOR_GOLD if val != "-" else COLOR_TEXT), (730, stats_y + idx * 24))
            
        # Playback status line
        pb_desc = f"Bước hiển thị: {self.playback_index} / {max(0, len(self.playback_history)-1)}"
        screen.blit(font_bold.render(pb_desc, True, COLOR_TEXT), (40, 530))
        
        # Draw Buttons
        for btn in self.buttons:
            is_active = (btn.text == self.selected_algo)
            btn.draw(screen, is_active=is_active)

# =========================================================================
# SECTION 6: TIC-TAC-TOE SCREEN (Brush strokes & Dynamic winning strike line)
# =========================================================================
class TicTacToeScreen:
    def __init__(self):
        self.board = [0] * 9
        self.game_mode = "human_ai"
        self.ai_algo = "alpha_beta"
        self.score_x = 0
        self.score_o = 0
        self.score_draw = 0
        self.game_state = "playing"
        self.current_turn = 1
        self.winner_val = None
        
        # Stats
        self.stats = {"status": "Đến lượt bạn (X)", "time": "-", "nodes": "-", "prunes": "-"}
        
        # Autoplay variables
        self.last_ai_move = time.time()
        
        # Winning line animation coordinates
        self.win_strike_progress = 0.0
        self.win_line_coords = None # (start_x, start_y, end_x, end_y)
        
        # UI Buttons
        self.buttons = []
        self.buttons.append(Button(40, 30, 160, 30, "<- Menu chính", lambda: set_screen("MENU")))
        
        # Modes & Algos selections
        self.buttons.append(Button(520, 110, 180, 28, "Human vs AI", self.set_mode, "human_ai"))
        self.buttons.append(Button(715, 110, 180, 28, "AI vs AI Showdown", self.set_mode, "ai_ai"))
        
        self.buttons.append(Button(520, 210, 120, 28, "Minimax", self.set_algo, "minimax"))
        self.buttons.append(Button(650, 210, 120, 28, "Alpha-Beta", self.set_algo, "alpha_beta"))
        self.buttons.append(Button(780, 210, 120, 28, "Expectimax", self.set_algo, "expectimax"))
        
        self.buttons.append(Button(520, 265, 180, 32, "CHƠI LẠI (RESTART)", self.restart))
        self.buttons.append(Button(715, 265, 180, 32, "XÓA ĐIỂM SỐ", self.reset_scores))

    def set_mode(self, mode):
        self.game_mode = mode
        self.restart()

    def set_algo(self, algo):
        self.ai_algo = algo

    def restart(self):
        self.board = [0] * 9
        self.game_state = "playing"
        self.current_turn = 1
        self.winner_val = None
        self.win_strike_progress = 0.0
        self.win_line_coords = None
        self.stats = {"status": "Trận đấu mới" if self.game_mode == "ai_ai" else "Đến lượt bạn (X)", "time": "-", "nodes": "-", "prunes": "-"}

    def reset_scores(self):
        self.score_x = 0
        self.score_o = 0
        self.score_draw = 0
        self.restart()

    def check_winning_line(self):
        win_lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        cell_size = 400 // 3
        start_x, start_y = 50, 110
        for line in win_lines:
            s = self.board[line[0]] + self.board[line[1]] + self.board[line[2]]
            if abs(s) == 3:
                # Find start and end cells coordinates
                r1, c1 = line[0]//3, line[0]%3
                r2, c2 = line[2]//3, line[2]%3
                x1 = start_x + c1 * cell_size + cell_size//2
                y1 = start_y + r1 * cell_size + cell_size//2
                x2 = start_x + c2 * cell_size + cell_size//2
                y2 = start_y + r2 * cell_size + cell_size//2
                self.win_line_coords = (x1, y1, x2, y2)
                break

    def ai_play(self, player):
        self.stats["status"] = "AI đang suy nghĩ..."
        start = time.perf_counter()
        
        stats = {"nodes": 0, "prunes": 0}
        is_max = (player == 1)
        
        if self.ai_algo == "minimax":
            score, move = ttt_minimax(self.board, 0, is_max, stats)
        elif self.ai_algo == "alpha_beta":
            score, move = ttt_ab(self.board, 0, -float('inf'), float('inf'), is_max, stats)
        elif self.ai_algo == "expectimax":
            score, move = ttt_expectimax(self.board, 0, is_max, stats)
            
        duration = (time.perf_counter() - start) * 1000
        
        if move is not None:
            self.board[move] = player
            
        self.stats = {
            "status": "Đang chơi...",
            "time": f"{duration:.2f} ms",
            "nodes": str(stats["nodes"]),
            "prunes": str(stats["prunes"]) if self.ai_algo == "alpha_beta" else "-"
        }
        
        # Check game over
        terminal, winner = ttt_is_terminal(self.board)
        if terminal:
            self.game_state = "game_over"
            self.winner_val = winner
            self.check_winning_line()
            if winner == 1:
                self.score_x += 1
                self.stats["status"] = "X Thắng cuộc!"
            elif winner == -1:
                self.score_o += 1
                self.stats["status"] = "O Thắng cuộc!"
            else:
                self.score_draw += 1
                self.stats["status"] = "Hòa cờ!"

    def handle_event(self, event):
        pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked = False
                for btn in self.buttons:
                    if btn.rect.collidepoint(pos):
                        btn.handle_click()
                        clicked = True
                        break
                        
                board_rect = pygame.Rect(40, 100, 420, 420)
                if not clicked and self.game_state == "playing" and self.game_mode == "human_ai" and self.current_turn == 1:
                    if board_rect.collidepoint(pos):
                        cell_size = 400 // 3
                        col = (pos[0] - 50) // cell_size
                        row = (pos[1] - 110) // cell_size
                        if 0 <= row < 3 and 0 <= col < 3:
                            cell_id = row * 3 + col
                            if self.board[cell_id] == 0:
                                self.board[cell_id] = 1 # Human plays X
                                terminal, winner = ttt_is_terminal(self.board)
                                if terminal:
                                    self.game_state = "game_over"
                                    self.winner_val = winner
                                    self.check_winning_line()
                                    if winner == 1:
                                        self.score_x += 1
                                        self.stats["status"] = "X Thắng cuộc!"
                                    elif winner == -1:
                                        self.score_o += 1
                                        self.stats["status"] = "O Thắng cuộc!"
                                    else:
                                        self.score_draw += 1
                                        self.stats["status"] = "Hòa cờ!"
                                else:
                                    self.current_turn = -1 # AI turn

    def update(self):
        pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.check_hover(pos)
            
        # AI decision updates
        if self.game_state == "playing":
            if self.game_mode == "human_ai" and self.current_turn == -1:
                self.ai_play(-1)
                self.current_turn = 1
                if self.game_state == "playing":
                    self.stats["status"] = "Đến lượt bạn (X)"
            elif self.game_mode == "ai_ai":
                now = time.time()
                if now - self.last_ai_move >= 0.7:
                    self.ai_play(self.current_turn)
                    self.current_turn = -self.current_turn
                    self.last_ai_move = now
                    if self.game_state == "playing":
                        self.stats["status"] = f"AI ({'X' if self.current_turn == 1 else 'O'}) đang tính..."
                        
        # Animate winning line draw
        if self.game_state == "game_over" and self.win_line_coords is not None:
            self.win_strike_progress += 0.08
            self.win_strike_progress = min(1.0, self.win_strike_progress)

    def draw_brush_X(self, screen, rect):
        # Draw premium X with thick gradient brush strokes
        pad = 22
        # Main slash
        pygame.draw.line(screen, COLOR_X, (rect.x + pad, rect.y + pad), (rect.x + rect.width - pad, rect.y + rect.height - pad), width=8)
        pygame.draw.line(screen, COLOR_TEXT, (rect.x + pad + 2, rect.y + pad), (rect.x + rect.width - pad - 2, rect.y + rect.height - pad), width=2)
        # Counter slash
        pygame.draw.line(screen, COLOR_X, (rect.x + rect.width - pad, rect.y + pad), (rect.x + pad, rect.y + rect.height - pad), width=8)
        pygame.draw.line(screen, COLOR_TEXT, (rect.x + rect.width - pad - 2, rect.y + pad), (rect.x + pad + 2, rect.y + rect.height - pad), width=2)

    def draw_brush_O(self, screen, rect):
        # Draw premium metallic O
        # Glow ring
        pygame.draw.circle(screen, COLOR_O, rect.center, rect.width//2 - 20, width=8)
        pygame.draw.circle(screen, COLOR_TEXT, rect.center, rect.width//2 - 20, width=2)

    def draw(self, screen):
        # Draw Grid Board
        board_rect = pygame.Rect(40, 100, 420, 420)
        pygame.draw.rect(screen, COLOR_PANEL_BG, board_rect, border_radius=15)
        pygame.draw.rect(screen, COLOR_GRID_LINE, board_rect, width=2, border_radius=15)
        
        cell_size = 400 // 3
        start_x, start_y = 50, 110
        
        for r in range(3):
            for c in range(3):
                cell_rect = pygame.Rect(start_x + c * cell_size, start_y + r * cell_size, cell_size, cell_size)
                # Glassmorphic rounded cell
                pygame.draw.rect(screen, COLOR_CELL_BG, cell_rect.inflate(-8, -8), border_radius=12)
                pygame.draw.rect(screen, COLOR_GRID_LINE, cell_rect, width=1)
                
                val = self.board[r * 3 + c]
                if val == 1:
                    self.draw_brush_X(screen, cell_rect)
                elif val == -1:
                    self.draw_brush_O(screen, cell_rect)
                    
        # Draw dynamically growing winning line
        if self.game_state == "game_over" and self.win_line_coords is not None:
            x1, y1, x2, y2 = self.win_line_coords
            curr_x = x1 + (x2 - x1) * self.win_strike_progress
            curr_y = y1 + (y2 - y1) * self.win_strike_progress
            # Glowing strike line
            pygame.draw.line(screen, COLOR_GOLD, (x1, y1), (int(curr_x), int(curr_y)), width=8)
            pygame.draw.line(screen, COLOR_TEXT, (x1, y1), (int(curr_x), int(curr_y)), width=2)
            
        # Draw Right Panel
        right_panel = pygame.Rect(500, 100, 415, 500)
        pygame.draw.rect(screen, COLOR_PANEL_BG, right_panel, border_radius=10)
        pygame.draw.rect(screen, COLOR_GRID_LINE, right_panel, width=1, border_radius=10)
        
        screen.blit(font_header.render("1. Chọn chế độ chơi đấu trí", True, COLOR_GOLD), (520, 85))
        screen.blit(font_header.render("2. Cấu hình thuật toán AI", True, COLOR_GOLD), (520, 180))
        screen.blit(font_header.render("3. Điều khiển & Thống kê", True, COLOR_GOLD), (520, 320))
        
        # Border highlight for active selectors
        if self.game_mode == "human_ai": pygame.draw.rect(screen, COLOR_GOLD, btn_m_ha.rect.inflate(4, 4), width=2, border_radius=8)
        else: pygame.draw.rect(screen, COLOR_GOLD, btn_m_aa.rect.inflate(4, 4), width=2, border_radius=8)
        
        ai_buttons = {"minimax": btn_a_minimax, "alpha_beta": btn_a_ab, "expectimax": btn_a_exp}
        for algo, btn in ai_buttons.items():
            if self.ai_algo == algo:
                pygame.draw.rect(screen, COLOR_GOLD, btn.rect.inflate(4, 4), width=2, border_radius=8)

        # Scoreboard
        lbl_score = font_bold.render(f"Bảng điểm:  X (Người/AI): {self.score_x}  |  O (AI): {self.score_o}  |  Hòa: {self.score_draw}", True, COLOR_GOLD)
        screen.blit(lbl_score, (520, 345))
        
        # Display Stats
        stats_y = 385
        labels = [
            ("Trạng thái trận đấu:", self.stats["status"]),
            ("Độ khó AI dùng:", self.ai_algo.upper()),
            ("Thời gian AI suy nghĩ:", self.stats["time"]),
            ("Số nút AI duyệt (nodes):", self.stats["nodes"]),
            ("Số lần cắt tỉa (prunes):", self.stats["prunes"])
        ]
        for idx, (lbl, val) in enumerate(labels):
            screen.blit(font_text.render(lbl, True, COLOR_TEXT), (530, stats_y + idx * 24))
            screen.blit(font_bold.render(val, True, COLOR_GOLD if val != "-" else COLOR_TEXT), (730, stats_y + idx * 24))
            
        # Draw Buttons
        for btn in self.buttons:
            btn.draw(screen)

# Screen switcher callback
def set_screen(name):
    global current_screen
    current_screen = name

# Screen initializer mappings
def init_menu(): pass
def init_puzzle(): global puzzle_scr; puzzle_scr = PuzzleScreen()
def init_nqueens(): global nqueens_scr; nqueens_scr = NQueensScreen()
def init_vacuum(): global vacuum_scr; vacuum_scr = VacuumScreen()
def init_map(): global map_scr; map_scr = MapColoringScreen()
def init_ttt(): global ttt_scr; ttt_scr = TicTacToeScreen()

screen_initializers = {
    "MENU": init_menu,
    "PUZZLE": init_puzzle,
    "NQUEENS": init_nqueens,
    "VACUUM": init_vacuum,
    "MAPCOLORING": init_map,
    "TICTACTOE": init_ttt
}

# Instantiate Screens
menu_scr = MenuScreen()
puzzle_scr = None
nqueens_scr = None
vacuum_scr = None
map_scr = None
ttt_scr = None

# Shared Button layout values for callbacks to reference (Global buttons needed inside callbacks)
# Brush tools (shared) for Vacuum cleaner & Map coloring reference
btn_t_robot = Button(520, 260, 120, 26, "Cọ: Robot", None)
btn_t_dirt = Button(650, 260, 120, 26, "Cọ: Rác", None)
btn_t_obs = Button(780, 260, 120, 26, "Cọ: Tường", None)

btn_b_node = Button(520, 255, 120, 28, "Vẽ Đỉnh (Node)", None)
btn_b_edge = Button(650, 255, 120, 28, "Vẽ Cạnh (Edge)", None)
btn_b_del = Button(780, 255, 120, 28, "Xóa Đỉnh", None)

btn_col3 = Button(520, 200, 180, 28, "3 màu (RGB)", None)
btn_col4 = Button(715, 200, 180, 28, "4 màu (RGBY)", None)

btn_m_ha = Button(520, 110, 180, 28, "Human vs AI", None)
btn_m_aa = Button(715, 110, 180, 28, "AI vs AI Showdown", None)

btn_a_minimax = Button(520, 210, 120, 28, "Minimax", None)
btn_a_ab = Button(650, 210, 120, 28, "Alpha-Beta", None)
btn_a_exp = Button(780, 210, 120, 28, "Expectimax", None)

# Main Loop
running = True
while running:
    # 1. Update logic
    if current_screen == "MENU":
        menu_scr.update()
    elif current_screen == "PUZZLE" and puzzle_scr:
        puzzle_scr.update()
    elif current_screen == "NQUEENS" and nqueens_scr:
        nqueens_scr.update()
    elif current_screen == "VACUUM" and vacuum_scr:
        vacuum_scr.update()
    elif current_screen == "MAPCOLORING" and map_scr:
        map_scr.update()
    elif current_screen == "TICTACTOE" and ttt_scr:
        ttt_scr.update()
        
    # 2. Render Screen
    screen.fill(COLOR_BG)
    update_and_draw_stars(screen)
    
    if current_screen == "MENU":
        menu_scr.draw(screen)
    elif current_screen == "PUZZLE" and puzzle_scr:
        puzzle_scr.draw(screen)
    elif current_screen == "NQUEENS" and nqueens_scr:
        nqueens_scr.draw(screen)
    elif current_screen == "VACUUM" and vacuum_scr:
        vacuum_scr.draw(screen)
    elif current_screen == "MAPCOLORING" and map_scr:
        map_scr.draw(screen)
    elif current_screen == "TICTACTOE" and ttt_scr:
        ttt_scr.draw(screen)
        
    # 3. Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            # Route event to current screen
            if current_screen == "MENU":
                menu_scr.handle_event(event)
            elif current_screen == "PUZZLE" and puzzle_scr:
                puzzle_scr.handle_event(event)
            elif current_screen == "NQUEENS" and nqueens_scr:
                nqueens_scr.handle_event(event)
            elif current_screen == "VACUUM" and vacuum_scr:
                vacuum_scr.handle_event(event)
            elif current_screen == "MAPCOLORING" and map_scr:
                map_scr.handle_event(event)
            elif current_screen == "TICTACTOE" and ttt_scr:
                ttt_scr.handle_event(event)
                
    pygame.display.flip()
    clock.tick(60) # Smooth 60 FPS for Lerp animations

pygame.quit()
sys.exit()
