"""
Module containing common helper functions and utilities for the AI algorithms and projects.
Provides Pygame-based GUI visualizer for 8-puzzle solutions.
"""
import copy
import time

def get_state_sequence(initial_state, path):
    """
    Tái tạo danh sách các trạng thái đi từ trạng thái ban đầu dựa vào chuỗi nước đi.
    """
    states = [initial_state]
    current = copy.deepcopy(initial_state)
    for move in path:
        # Tìm tọa độ ô số 0
        x, y = -1, -1
        for i in range(3):
            for j in range(3):
                if current[i][j] == 0:
                    x, y = i, j
                    break
        dx, dy = 0, 0
        if move == "LÊN":
            dx, dy = -1, 0
        elif move == "XUỐNG":
            dx, dy = 1, 0
        elif move == "TRÁI":
            dx, dy = 0, -1
        elif move == "PHẢI":
            dx, dy = 0, 1
            
        nx, ny = x + dx, y + dy
        current[x][y], current[nx][ny] = current[nx][ny], current[x][y]
        states.append(copy.deepcopy(current))
    return states

def visualize_puzzle_pygame(initial_state, path, delay=0.8):
    """
    Trực quan hóa trạng thái 8-puzzle và từng bước giải bằng Pygame.
    Hỗ trợ:
      - Tự động chạy với thời gian chờ (delay).
      - Nhấn phím SPACE để tạm dừng / tiếp tục.
      - Nhấn phím MŨI TÊN TRÁI / PHẢI để xem từng bước thủ công.
      - Nhấn phím R để quay lại trạng thái ban đầu.
    """
    import pygame
    
    # Khởi tạo Pygame
    pygame.init()
    
    # Tải chuỗi trạng thái
    states = get_state_sequence(initial_state, path)
    
    # Kích thước màn hình
    WINDOW_SIZE = 450
    GRID_SIZE = 3
    CELL_SIZE = WINDOW_SIZE // GRID_SIZE
    FOOTER_HEIGHT = 60
    
    # Bảng màu hiện đại (Modern Material Palette)
    BG_COLOR = (30, 39, 46)        # Dark Charcoal
    TILE_COLOR = (9, 132, 227)     # Blue
    EMPTY_COLOR = (47, 53, 66)     # Dark Gray
    TEXT_COLOR = (255, 255, 255)   # White
    FOOTER_BG = (47, 53, 66)       # Dark Gray for footer
    HIGHLIGHT_COLOR = (241, 196, 15) # Gold
    
    # Khởi tạo cửa sổ
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + FOOTER_HEIGHT))
    pygame.display.set_caption("8-Puzzle Solver Visualizer (Pygame)")
    
    # Khởi tạo font chữ
    try:
        font = pygame.font.SysFont("Segoe UI", 64, bold=True)
        footer_font = pygame.font.SysFont("Segoe UI", 20, bold=True)
    except:
        font = pygame.font.Font(None, 80)
        footer_font = pygame.font.Font(None, 24)
        
    clock = pygame.time.Clock()
    
    current_index = 0
    running = True
    paused = False
    last_update_time = time.time()
    
    while running:
        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    current_index = 0
                elif event.key == pygame.K_RIGHT:
                    if current_index < len(states) - 1:
                        current_index += 1
                        paused = True # Chuyển sang chế độ xem thủ công khi tương tác
                elif event.key == pygame.K_LEFT:
                    if current_index > 0:
                        current_index -= 1
                        paused = True # Chuyển sang chế độ xem thủ công khi tương tác
        
        # Tự động chuyển bước nếu không tạm dừng
        if not paused and current_index < len(states) - 1:
            current_time = time.time()
            if current_time - last_update_time >= delay:
                current_index += 1
                last_update_time = current_time
                
        # Vẽ giao diện
        screen.fill(BG_COLOR)
        
        # Lấy trạng thái hiện tại
        state = states[current_index]
        
        # Vẽ các ô vuông
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                val = state[r][c]
                rect = pygame.Rect(c * CELL_SIZE + 6, r * CELL_SIZE + 6, CELL_SIZE - 12, CELL_SIZE - 12)
                
                if val == 0:
                    # Ô trống vẽ màu sẫm
                    pygame.draw.rect(screen, EMPTY_COLOR, rect, border_radius=15)
                else:
                    # Ô số vẽ màu xanh dương có bo góc
                    pygame.draw.rect(screen, TILE_COLOR, rect, border_radius=15)
                    
                    # Vẽ số lên ô vuông
                    text_surf = font.render(str(val), True, TEXT_COLOR)
                    text_rect = text_surf.get_rect(center=rect.center)
                    screen.blit(text_surf, text_rect)
                    
        # Vẽ thanh Footer bên dưới hiển thị thông tin
        footer_rect = pygame.Rect(0, WINDOW_SIZE, WINDOW_SIZE, FOOTER_HEIGHT)
        pygame.draw.rect(screen, FOOTER_BG, footer_rect)
        
        # Trạng thái văn bản
        if current_index == 0:
            status_text = "Trạng thái ban đầu"
        else:
            status_text = f"Bước {current_index}/{len(states)-1}: Di chuyển [{path[current_index-1]}]"
            
        if paused:
            status_text += " (TẠM DỪNG)"
            
        status_surf = footer_font.render(status_text, True, HIGHLIGHT_COLOR)
        status_rect = status_surf.get_rect(center=footer_rect.center)
        screen.blit(status_surf, status_rect)
        
        pygame.display.flip()
        clock.tick(30)
        
    pygame.quit()
