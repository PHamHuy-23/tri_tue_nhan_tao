import pygame
import sys
import time
import copy
import random
import math
from map_solvers import solve_backtracking, solve_forward_checking, solve_ac3, solve_min_conflicts

# Initialize Pygame
pygame.init()

# Window Configuration
WIDTH, HEIGHT = 950, 610
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Map Coloring CSP Interactive Visualizer")
clock = pygame.time.Clock()

# Colors
COLOR_BG = (26, 37, 48)          # Dark Slate Blue
COLOR_PANEL_BG = (34, 49, 63)    # Lighter Slate
COLOR_TEXT = (236, 240, 241)     # Off White
COLOR_BUTTON = (52, 152, 219)    # Bright Blue
COLOR_BUTTON_HOVER = (41, 128, 185)
COLOR_BUTTON_ACTIVE = (46, 204, 113) # Green
COLOR_GOLD = (241, 196, 15)      # Accent Gold
COLOR_EDGE = (149, 165, 166)      # Slate line for edge

COLOR_MAP = {
    "Red": (231, 76, 60),
    "Green": (46, 204, 113),
    "Blue": (52, 152, 219),
    "Yellow": (241, 196, 15),
    "Orange": (230, 126, 34),
    "Purple": (155, 89, 182)
}
COLOR_UNASSIGNED = (127, 140, 141)

# Fonts
try:
    font_title = pygame.font.SysFont("Segoe UI", 26, bold=True)
    font_header = pygame.font.SysFont("Segoe UI", 18, bold=True)
    font_text = pygame.font.SysFont("Segoe UI", 15, bold=False)
    font_bold = pygame.font.SysFont("Segoe UI", 15, bold=True)
    font_node = pygame.font.SysFont("Segoe UI", 14, bold=True)
except:
    font_title = pygame.font.Font(None, 34)
    font_header = pygame.font.Font(None, 24)
    font_text = pygame.font.Font(None, 18)
    font_bold = pygame.font.Font(None, 18)
    font_node = pygame.font.Font(None, 16)

# Graph Variables
nodes = {} # id: (x, y)
adj = {}   # id: list of neighbor ids
node_counter = 1

# Tool Modes: "add_node", "add_edge", "delete_node"
tool_mode = "add_node"
selected_first_node = None # For drawing edges

# Solver options
selected_algo = "Backtracking"
algos = ["Backtracking", "Forward Check", "AC-3", "Min-Conflicts"]
num_colors = 3

# Statistics
stats_status = "Chờ lệnh (Ready)"
stats_time = "-"
stats_steps = "-"
stats_backtracks = "-"

# Playback State
playback_history = [] # List of assignments at each step
playback_index = 0
playback_paused = True
playback_delay = 0.4  # seconds
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
    global tool_mode, selected_first_node
    tool_mode = mode
    selected_first_node = None

def set_colors_count(count):
    global num_colors
    num_colors = count

def clear_graph():
    global nodes, adj, node_counter, selected_first_node
    nodes = {}
    adj = {}
    node_counter = 1
    selected_first_node = None
    reset_playback()

def load_australia_preset():
    global nodes, adj, node_counter, selected_first_node
    clear_graph()
    
    # Coordinates mapping
    nodes = {
        "WA": (110, 210),
        "NT": (210, 140),
        "SA": (230, 280),
        "Q": (320, 160),
        "NSW": (330, 290),
        "V": (270, 360),
        "T": (290, 440)
    }
    
    adj = {
        "WA": ["NT", "SA"],
        "NT": ["WA", "Q", "SA"],
        "Q": ["NT", "NSW", "SA"],
        "NSW": ["Q", "V", "SA"],
        "V": ["NSW", "SA"],
        "SA": ["WA", "NT", "Q", "NSW", "V"],
        "T": []
    }
    node_counter = 8
    reset_playback()

def load_triangle_preset():
    global nodes, adj, node_counter
    clear_graph()
    
    nodes = {
        "N1": (220, 120),
        "N2": (120, 280),
        "N3": (320, 280),
        "N4": (220, 400),
        "N5": (220, 260)
    }
    
    adj = {
        "N1": ["N2", "N3", "N5"],
        "N2": ["N1", "N4", "N5"],
        "N3": ["N1", "N4", "N5"],
        "N4": ["N2", "N3", "N5"],
        "N5": ["N1", "N2", "N3", "N4"]
    }
    node_counter = 6
    reset_playback()

def reset_playback():
    global playback_index, playback_paused, playback_history
    playback_index = 0
    playback_paused = True

def run_solver():
    global nodes, adj, selected_algo, num_colors, playback_history
    global stats_status, stats_time, stats_steps, stats_backtracks
    global playback_paused, playback_index
    
    if not nodes:
        stats_status = "Lỗi: Đồ thị rỗng!"
        return
        
    stats_status = "Đang giải..."
    reset_playback()
    
    screen.fill(COLOR_BG)
    status_surf = font_title.render("ĐANG GIẢI QUYẾT BÀI TOÁN...", True, COLOR_GOLD)
    screen.blit(status_surf, (WIDTH//2 - status_surf.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    
    node_list = list(nodes.keys())
    # Ensure all adjacency entries exist bidirectionally
    clean_adj = {n: [] for n in node_list}
    for u in adj:
        for v in adj[u]:
            if u in node_list and v in node_list:
                if v not in clean_adj[u]: clean_adj[u].append(v)
                if u not in clean_adj[v]: clean_adj[v].append(u)
                
    start_time = time.perf_counter()
    
    res = None
    steps = 0
    backtracks = 0
    history = []
    
    if selected_algo == "Backtracking":
        res, steps, backtracks, history = solve_backtracking(node_list, clean_adj, num_colors)
    elif selected_algo == "Forward Check":
        res, steps, backtracks, history = solve_forward_checking(node_list, clean_adj, num_colors)
    elif selected_algo == "AC-3":
        res, steps, backtracks, history = solve_ac3(node_list, clean_adj, num_colors)
    elif selected_algo == "Min-Conflicts":
        res, steps, history = solve_min_conflicts(node_list, clean_adj, num_colors)
        backtracks = 0
        
    end_time = time.perf_counter()
    
    stats_time = f"{(end_time - start_time)*1000:.2f} ms"
    stats_steps = str(steps)
    stats_backtracks = str(backtracks)
    
    if res is not None:
        stats_status = "Đã tìm ra cách tô màu!"
        playback_history = history
        playback_paused = False
    else:
        stats_status = "Không có lời giải!"
        playback_history = history
        playback_paused = False

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

# 1. Algorithm Selection Buttons (Right Panel)
y_start = 110
for i, algo in enumerate(algos):
    col = i % 2
    row = i // 2
    btn = Button(520 + col * 195, y_start + row * 36, 180, 28, algo, set_algo, algo)
    buttons.append(btn)

# 2. Colors count Selector Buttons
y_colors = 200
btn_col3 = Button(520, y_colors, 180, 28, "3 màu (RGB)", set_colors_count, 3)
btn_col4 = Button(715, y_colors, 180, 28, "4 màu (RGBY)", set_colors_count, 4)
buttons.extend([btn_col3, btn_col4])

# 3. Canvas Edit Brushes
y_brushes = 255
btn_b_node = Button(520, y_brushes, 120, 28, "Vẽ Đỉnh (Node)", set_tool_mode, "add_node")
btn_b_edge = Button(650, y_brushes, 120, 28, "Vẽ Cạnh (Edge)", set_tool_mode, "add_edge")
btn_b_del = Button(780, y_brushes, 120, 28, "Xóa Đỉnh", set_tool_mode, "delete_node")
buttons.extend([btn_b_node, btn_b_edge, btn_b_del])

# 4. Action Presets
y_actions = 300
btn_pre_aus = Button(520, y_actions, 85, 30, "Bản đồ Úc", load_australia_preset)
btn_pre_tri = Button(615, y_actions, 85, 30, "Đồ thị mẫu", load_triangle_preset)
btn_pre_clr = Button(710, y_actions, 85, 30, "Xóa hết", clear_graph)
btn_solve = Button(805, y_actions, 85, 30, "TÔ MÀU", run_solver)
buttons.extend([btn_pre_aus, btn_pre_tri, btn_pre_clr, btn_solve])

# 5. Playback buttons (Left panel under the board)
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
            if event.button == 1:
                # Check button clicks
                clicked_button = False
                for btn in buttons:
                    if btn.rect.collidepoint(pos):
                        btn.handle_click()
                        clicked_button = True
                        break
                        
                # Click on the graph canvas (Left panel)
                # Canvas bounds: x = 40 to 460, y = 75 to 495
                canvas_rect = pygame.Rect(40, 75, 420, 420)
                if not clicked_button and canvas_rect.collidepoint(pos):
                    # Find if we clicked an existing node
                    clicked_node_id = None
                    for nid, (nx, ny) in nodes.items():
                        dist = math.sqrt((pos[0] - nx)**2 + (pos[1] - ny)**2)
                        if dist <= 20:
                            clicked_node_id = nid
                            break
                            
                    if tool_mode == "add_node":
                        if clicked_node_id is None:
                            new_id = f"N{node_counter}"
                            nodes[new_id] = pos
                            adj[new_id] = []
                            node_counter += 1
                            reset_playback()
                    elif tool_mode == "add_edge":
                        if clicked_node_id is not None:
                            if selected_first_node is None:
                                selected_first_node = clicked_node_id
                            else:
                                if selected_first_node != clicked_node_id:
                                    # Add bidirectional edge
                                    if clicked_node_id not in adj[selected_first_node]:
                                        adj[selected_first_node].append(clicked_node_id)
                                    if selected_first_node not in adj[clicked_node_id]:
                                        adj[clicked_node_id].append(selected_first_node)
                                selected_first_node = None
                                reset_playback()
                        else:
                            selected_first_node = None
                    elif tool_mode == "delete_node":
                        if clicked_node_id is not None:
                            del nodes[clicked_node_id]
                            # Remove edges connected to this node
                            if clicked_node_id in adj:
                                del adj[clicked_node_id]
                            for u in adj:
                                if clicked_node_id in adj[u]:
                                    adj[u].remove(clicked_node_id)
                            reset_playback()
                            
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
    
    # 1. Title Header
    title_surf = font_title.render("MAP COLORING CSP INTERACTIVE VISUALIZER", True, COLOR_GOLD)
    screen.blit(title_surf, (30, 20))
    
    # 2. Draw Graph Canvas (Left Side)
    canvas_rect = pygame.Rect(40, 75, 420, 420)
    pygame.draw.rect(screen, COLOR_PANEL_BG, canvas_rect, border_radius=15)
    pygame.draw.rect(screen, COLOR_TEXT, canvas_rect, width=2, border_radius=15)
    
    # Limit drawing area inside canvas
    # Draw all edges first
    drawn_edges = set()
    for u in adj:
        for v in adj[u]:
            edge = tuple(sorted((u, v)))
            if edge not in drawn_edges and u in nodes and v in nodes:
                pygame.draw.line(screen, COLOR_EDGE, nodes[u], nodes[v], width=3)
                drawn_edges.add(edge)
                
    # Get current assignment from playback index
    current_assignment = {}
    if len(playback_history) > 0 and playback_index < len(playback_history):
        current_assignment = playback_history[playback_index]
        
    # Draw nodes
    for nid, (nx, ny) in nodes.items():
        # Node color based on assignment
        color_name = current_assignment.get(nid)
        node_color = COLOR_MAP.get(color_name, COLOR_UNASSIGNED)
        
        # Highlight if selected for edge drawing
        if selected_first_node == nid:
            pygame.draw.circle(screen, COLOR_GOLD, (nx, ny), 24)
            
        pygame.draw.circle(screen, node_color, (nx, ny), 20)
        pygame.draw.circle(screen, COLOR_TEXT, (nx, ny), 20, width=2)
        
        # Draw node label
        label_surf = font_node.render(nid, True, COLOR_TEXT)
        label_rect = label_surf.get_rect(center=(nx, ny))
        screen.blit(label_surf, label_rect)
        
    # 3. Draw Right Panel Background
    panel_rect = pygame.Rect(500, 75, 415, 512)
    pygame.draw.rect(screen, COLOR_PANEL_BG, panel_rect, border_radius=10)
    pygame.draw.rect(screen, COLOR_TEXT, panel_rect, width=1, border_radius=10)
    
    # 4. Right Panel Sections
    screen.blit(font_header.render("1. Chọn thuật toán CSP giải quyết", True, COLOR_GOLD), (520, 85))
    screen.blit(font_header.render("2. Chọn cọ vẽ & Bản đồ mẫu", True, COLOR_GOLD), (520, 235))
    
    # Active algorithm indicator
    active_algo_surf = font_bold.render(f"Đang chọn: {selected_algo} ({num_colors} màu)", True, COLOR_GOLD)
    screen.blit(active_algo_surf, (520, 175))
    
    # Active color count button highlight
    if num_colors == 3:
        pygame.draw.rect(screen, COLOR_GOLD, btn_col3.rect.inflate(4, 4), width=2, border_radius=8)
    else:
        pygame.draw.rect(screen, COLOR_GOLD, btn_col4.rect.inflate(4, 4), width=2, border_radius=8)
        
    # Active brush tool border highlight
    brush_tools = {"add_node": btn_b_node, "add_edge": btn_b_edge, "delete_node": btn_b_del}
    for mode, btn in brush_tools.items():
        if tool_mode == mode:
            pygame.draw.rect(screen, COLOR_GOLD, btn.rect.inflate(4, 4), width=2, border_radius=8)

    # Draw statistics section
    stats_y = 350
    screen.blit(font_header.render("3. Số liệu thống kê (Statistics)", True, COLOR_GOLD), (520, stats_y))
    
    stats = [
        ("Trạng thái giải:", stats_status),
        ("Tổng thời gian giải:", stats_time),
        ("Tổng số bước gán (steps):", stats_steps),
        ("Số lần quay lui (backtracks):", stats_backtracks)
    ]
    
    for idx, (label, val) in enumerate(stats):
        lbl_surf = font_text.render(label, True, COLOR_TEXT)
        val_surf = font_bold.render(val, True, COLOR_GOLD if val not in ["-", "Đang giải..."] else COLOR_TEXT)
        screen.blit(lbl_surf, (530, stats_y + 25 + idx * 22))
        screen.blit(val_surf, (730, stats_y + 25 + idx * 22))
        
    # Playback stats (Left Panel)
    playback_desc = f"Bước hiển thị: {playback_index} / {max(0, len(playback_history)-1)}"
    pb_surf = font_bold.render(playback_desc, True, COLOR_TEXT)
    screen.blit(pb_surf, (40, 505))
    
    # 5. Draw Buttons
    for btn in buttons:
        is_active = (btn.text == selected_algo)
        btn.draw(screen, is_active=is_active)
        
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
