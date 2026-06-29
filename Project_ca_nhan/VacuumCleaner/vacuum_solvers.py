import heapq
from collections import deque
import copy
import time

def get_neighbors(state, grid_size, obstacles):
    """
    Sinh các lân cận của trạng thái hiện tại.
    Trạng thái: (robot_pos, dirt_set)
    robot_pos: (r, c)
    dirt_set: frozenset of (r, c)
    Trả về danh sách các tuple: (action, next_state, step_cost)
    """
    pos, dirt_set = state
    r, c = pos
    rows, cols = grid_size
    neighbors = []
    
    # 1. Hành động HÚT (Suck)
    if pos in dirt_set:
        next_dirt = frozenset(dirt_set - {pos})
        neighbors.append(("HÚT", (pos, next_dirt), 1))
        
    # 2. Hành động di chuyển
    moves = [
        ("LÊN", -1, 0),
        ("XUỐNG", 1, 0),
        ("TRÁI", 0, -1),
        ("PHẢI", 0, 1)
    ]
    for action, dr, dc in moves:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            if (nr, nc) not in obstacles:
                neighbors.append((action, ((nr, nc), dirt_set), 1))
                
    return neighbors

def is_goal(state):
    # Đích đạt được khi tập hợp vết bẩn bị rỗng
    return len(state[1]) == 0

# ==========================================
# HEURISTIC FUNCTIONS
# ==========================================
def h_remaining_dirt(state):
    # Số lượng vết bẩn còn lại (Hamming-like)
    return len(state[1])

def h_manhattan_nearest(state):
    """
    Ước lượng chi phí: Khoảng cách Manhattan đến vết bẩn gần nhất + Số vết bẩn còn lại
    """
    pos, dirt_set = state
    if not dirt_set:
        return 0
    r, c = pos
    min_dist = float('inf')
    for dr, dc in dirt_set:
        dist = abs(r - dr) + abs(c - dc)
        if dist < min_dist:
            min_dist = dist
    return min_dist + len(dirt_set) - 1

# ==========================================
# 1. BFS
# ==========================================
def bfs(init_state, grid_size, obstacles):
    frontier = deque([(init_state, [])])
    reached = {init_state}
    steps = 0
    
    while frontier:
        steps += 1
        current, path = frontier.popleft()
        
        if is_goal(current):
            return path, steps, len(reached)
            
        for action, next_state, _ in get_neighbors(current, grid_size, obstacles):
            if next_state not in reached:
                reached.add(next_state)
                frontier.append((next_state, path + [action]))
    return None, steps, len(reached)

# ==========================================
# 2. DFS
# ==========================================
def dfs(init_state, grid_size, obstacles):
    frontier = [(init_state, [])]
    reached = {init_state}
    steps = 0
    
    while frontier:
        steps += 1
        current, path = frontier.pop()
        
        if is_goal(current):
            return path, steps, len(reached)
            
        for action, next_state, _ in reversed(get_neighbors(current, grid_size, obstacles)):
            if next_state not in reached:
                reached.add(next_state)
                frontier.append((next_state, path + [action]))
    return None, steps, len(reached)

# ==========================================
# 3. IDS
# ==========================================
def dls(state, limit, path, visited, grid_size, obstacles, stats):
    stats["steps"] += 1
    if is_goal(state):
        return path, True
    if limit <= 0:
        return "cutoff", False
        
    cutoff_occurred = False
    visited.add(state)
    
    for action, next_state, _ in get_neighbors(state, grid_size, obstacles):
        if next_state not in visited:
            res, found = dls(next_state, limit - 1, path + [action], visited, grid_size, obstacles, stats)
            if found:
                return res, True
            if res == "cutoff":
                cutoff_occurred = True
                
    visited.remove(state)
    return "cutoff" if cutoff_occurred else None, False

def ids(init_state, grid_size, obstacles, max_depth=100):
    total_steps = 0
    for depth in range(max_depth):
        stats = {"steps": 0}
        visited = set()
        res, found = dls(init_state, depth, [], visited, grid_size, obstacles, stats)
        total_steps += stats["steps"]
        if found:
            return res, depth, total_steps
        if res != "cutoff":
            break
    return None, -1, total_steps

# ==========================================
# 4. UCS
# ==========================================
def ucs(init_state, grid_size, obstacles):
    heap = []
    unique_counter = 0
    heapq.heappush(heap, (0, unique_counter, init_state, []))
    reached = {init_state: 0}
    steps = 0
    
    while heap:
        steps += 1
        g_cost, _, current, path = heapq.heappop(heap)
        
        if is_goal(current):
            return path, g_cost, steps, len(reached)
            
        if g_cost > reached.get(current, float('inf')):
            continue
            
        for action, next_state, step_cost in get_neighbors(current, grid_size, obstacles):
            new_g = g_cost + step_cost
            if new_g < reached.get(next_state, float('inf')):
                reached[next_state] = new_g
                unique_counter += 1
                heapq.heappush(heap, (new_g, unique_counter, next_state, path + [action]))
    return None, float('inf'), steps, len(reached)

# ==========================================
# 5. Greedy
# ==========================================
def greedy(init_state, grid_size, obstacles, h_func=h_manhattan_nearest):
    heap = []
    unique_counter = 0
    h_val = h_func(init_state)
    heapq.heappush(heap, (h_val, unique_counter, init_state, []))
    reached = {init_state}
    steps = 0
    
    while heap:
        steps += 1
        h_cost, _, current, path = heapq.heappop(heap)
        
        if is_goal(current):
            return path, steps, len(reached)
            
        for action, next_state, _ in get_neighbors(current, grid_size, obstacles):
            if next_state not in reached:
                reached.add(next_state)
                unique_counter += 1
                h_next = h_func(next_state)
                heapq.heappush(heap, (h_next, unique_counter, next_state, path + [action]))
    return None, steps, len(reached)

# ==========================================
# 6. A*
# ==========================================
def astar(init_state, grid_size, obstacles, h_func=h_manhattan_nearest):
    heap = []
    unique_counter = 0
    h_val = h_func(init_state)
    heapq.heappush(heap, (h_val, unique_counter, init_state, [], 0))
    reached = {init_state: 0}
    steps = 0
    
    while heap:
        steps += 1
        f_cost, _, current, path, g_cost = heapq.heappop(heap)
        
        if is_goal(current):
            return path, g_cost, steps, len(reached)
            
        if g_cost > reached.get(current, float('inf')):
            continue
            
        for action, next_state, step_cost in get_neighbors(current, grid_size, obstacles):
            new_g = g_cost + step_cost
            if new_g < reached.get(next_state, float('inf')):
                reached[next_state] = new_g
                unique_counter += 1
                f_val = new_g + h_func(next_state)
                heapq.heappush(heap, (f_val, unique_counter, next_state, path + [action], new_g))
    return None, float('inf'), steps, len(reached)

# ==========================================
# 7. IDA*
# ==========================================
def idastar(init_state, grid_size, obstacles, h_func=h_manhattan_nearest):
    def search(path, g, f_limit, visited, stats):
        stats["steps"] += 1
        current = path[-1]
        f = g + h_func(current)
        if f > f_limit:
            return f, False, None
        if is_goal(current):
            return f, True, path
            
        min_val = float('inf')
        visited.add(current)
        
        for action, next_state, step_cost in get_neighbors(current, grid_size, obstacles):
            if next_state not in visited:
                res_f, found, res_path = search(path + [next_state], g + step_cost, f_limit, visited, stats)
                if found:
                    return res_f, True, res_path
                if res_f < min_val:
                    min_val = res_f
                    
        visited.remove(current)
        return min_val, False, None

    if is_goal(init_state):
        return [], 0, 1
        
    f_limit = h_func(init_state)
    total_steps = 0
    max_iterations = 100
    
    for _ in range(max_iterations):
        stats = {"steps": 0}
        visited = set()
        res_f, found, res_path = search([init_state], 0, f_limit, visited, stats)
        total_steps += stats["steps"]
        if found:
            # Tái tạo chuỗi hành động từ danh sách các trạng thái
            move_path = []
            for idx in range(len(res_path) - 1):
                curr = res_path[idx]
                nxt = res_path[idx+1]
                for action, next_s, _ in get_neighbors(curr, grid_size, obstacles):
                    if next_s == nxt:
                        move_path.append(action)
                        break
            return move_path, f_limit, total_steps
        if res_f == float('inf'):
            break
        f_limit = res_f
    return None, -1, total_steps

# ==========================================
# 8. Hill Climbing (Greedy Local Path)
# ==========================================
# Vì Hill Climbing là tìm kiếm cục bộ không quay lui, 
# ta mô phỏng một tác nhân di chuyển leo đồi đi tìm ô bẩn gần nhất cho tới khi hết bẩn hoặc kẹt.
def hill_climbing(init_state, grid_size, obstacles, h_func=h_manhattan_nearest):
    current = init_state
    path = []
    steps = 0
    visited = {init_state}
    
    while not is_goal(current):
        steps += 1
        neighbors = get_neighbors(current, grid_size, obstacles)
        best_neighbor = None
        best_h = h_func(current)
        best_action = None
        
        for action, next_state, _ in neighbors:
            # Tránh lặp chu trình
            if next_state not in visited:
                next_h = h_func(next_state)
                if next_h < best_h:
                    best_h = next_h
                    best_neighbor = next_state
                    best_action = action
                    
        if best_neighbor is not None:
            current = best_neighbor
            visited.add(current)
            path.append(best_action)
        else:
            break # Bị kẹt ở cực trị cục bộ (Local Optimum)
            
    return path, is_goal(current), steps, len(visited)
