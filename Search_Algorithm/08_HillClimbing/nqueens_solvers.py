import random
import math

def h_attack(state):
    """
    Hàm heuristic: Đếm số cặp quân hậu tấn công nhau.
    Trạng thái là một list độ dài N, ví dụ [0, 4, 7, 5, 2, 6, 1, 3]
    """
    n = len(state)
    attacks = 0
    for i in range(n):
        for j in range(i + 1, n):
            # Tấn công cùng hàng
            if state[i] == state[j]:
                attacks += 1
            # Tấn công cùng đường chéo
            elif abs(state[i] - state[j]) == abs(i - j):
                attacks += 1
    return attacks

def get_neighbors(state):
    """
    Sinh tất cả các trạng thái lân cận bằng cách di chuyển 1 quân hậu
    trong cột của nó sang dòng khác.
    Tổng số lân cận: N * (N - 1)
    """
    n = len(state)
    neighbors = []
    for col in range(n):
        original_row = state[col]
        for row in range(n):
            if row != original_row:
                neighbor = list(state)
                neighbor[col] = row
                neighbors.append(neighbor)
    return neighbors

# ==========================================
# 1. Simple Hill Climbing (First Choice)
# ==========================================
def simple_hill_climbing(init):
    current = list(init)
    current_h = h_attack(current)
    history = [(current, current_h)]
    steps = 0
    
    while True:
        steps += 1
        neighbors = get_neighbors(current)
        random.shuffle(neighbors) # Tìm ngẫu nhiên lân cận đầu tiên tốt hơn
        found_better = False
        
        for neighbor in neighbors:
            neighbor_h = h_attack(neighbor)
            if neighbor_h < current_h:
                current = neighbor
                current_h = neighbor_h
                history.append((current, current_h))
                found_better = True
                break
                
        if not found_better:
            break
            
    return current, current_h, steps, history

# ==========================================
# 2. Steepest Ascent Hill Climbing
# ==========================================
def steepest_ascent_hill_climbing(init):
    current = list(init)
    current_h = h_attack(current)
    history = [(current, current_h)]
    steps = 0
    
    while True:
        steps += 1
        neighbors = get_neighbors(current)
        best_neighbor = None
        best_h = current_h
        
        for neighbor in neighbors:
            neighbor_h = h_attack(neighbor)
            if neighbor_h < best_h:
                best_h = neighbor_h
                best_neighbor = neighbor
                
        if best_neighbor is not None:
            current = best_neighbor
            current_h = best_h
            history.append((current, current_h))
        else:
            break # Bị kẹt ở cực trị cục bộ
            
    return current, current_h, steps, history

# ==========================================
# 3. Stochastic Hill Climbing
# ==========================================
def stochastic_hill_climbing(init):
    current = list(init)
    current_h = h_attack(current)
    history = [(current, current_h)]
    steps = 0
    
    while True:
        steps += 1
        neighbors = get_neighbors(current)
        # Lọc ra các lân cận tốt hơn trạng thái hiện tại
        better_neighbors = [n for n in neighbors if h_attack(n) < current_h]
        
        if better_neighbors:
            # Chọn ngẫu nhiên 1 trong số các lân cận tốt hơn
            current = random.choice(better_neighbors)
            current_h = h_attack(current)
            history.append((current, current_h))
        else:
            break
            
    return current, current_h, steps, history

# ==========================================
# 4. Random-Restart Hill Climbing
# ==========================================
def random_restart_hill_climbing(n_queens=8, max_restarts=100):
    total_steps = 0
    restarts = 0
    history = []
    
    for i in range(max_restarts):
        restarts = i
        # Khởi tạo trạng thái ngẫu nhiên
        init = [random.randint(0, n_queens - 1) for _ in range(n_queens)]
        current, current_h, steps, run_history = steepest_ascent_hill_climbing(init)
        total_steps += steps
        history.extend(run_history)
        
        if current_h == 0:
            return current, current_h, total_steps, restarts, history
            
    return current, current_h, total_steps, restarts, history

# ==========================================
# 5. Local Beam Search
# ==========================================
def local_beam_search(n_queens=8, k=3, max_steps=100):
    # Khởi tạo k trạng thái ngẫu nhiên
    current_states = [[random.randint(0, n_queens - 1) for _ in range(n_queens)] for _ in range(k)]
    history = []
    
    for step in range(max_steps):
        all_candidates = []
        for state in current_states:
            h = h_attack(state)
            if h == 0:
                return state, 0, step, history
            
            # Sinh tất cả lân cận của từng chùm
            for neighbor in get_neighbors(state):
                all_candidates.append(neighbor)
                
        # Sắp xếp các ứng viên theo độ tốt tăng dần (ít cặp tấn công hơn)
        all_candidates.sort(key=h_attack)
        # Giữ lại k trạng thái tốt nhất
        current_states = all_candidates[:k]
        
        best_state = current_states[0]
        best_h = h_attack(best_state)
        history.append((best_state, best_h))
        
        # Nếu đạt mục tiêu
        if best_h == 0:
            return best_state, 0, step, history
            
    return current_states[0], h_attack(current_states[0]), max_steps, history

# ==========================================
# 6. Simulated Annealing
# ==========================================
def simulated_annealing(init, temp=100.0, alpha=0.95, min_temp=0.01):
    current = list(init)
    current_h = h_attack(current)
    history = [(current, current_h)]
    t = temp
    steps = 0
    
    while t > min_temp and current_h > 0:
        steps += 1
        neighbors = get_neighbors(current)
        neighbor = random.choice(neighbors)
        neighbor_h = h_attack(neighbor)
        
        delta = neighbor_h - current_h
        
        # Nếu lân cận tốt hơn, hoặc chấp nhận lân cận tệ hơn với xác suất p
        if delta < 0:
            current = neighbor
            current_h = neighbor_h
            history.append((current, current_h))
        else:
            p = math.exp(-delta / t)
            if random.random() < p:
                current = neighbor
                current_h = neighbor_h
                history.append((current, current_h))
                
        # Hạ nhiệt
        t *= alpha
        
    return current, current_h, steps, history
