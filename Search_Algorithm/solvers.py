from collections import deque
import heapq
import copy

def state_to_tuple(state):
    return tuple(tuple(row) for row in state)

def find_zero(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j
    return -1, -1

def generate_children(state):
    children = []
    x, y = find_zero(state)
    moves = [
        ("LÊN", -1, 0, 1),
        ("XUỐNG", 1, 0, 1),
        ("TRÁI", 0, -1, 1),
        ("PHẢI", 0, 1, 1)
    ]
    for move_name, dx, dy, cost in moves:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            new_state = copy.deepcopy(state)
            new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
            children.append((move_name, new_state, cost))
    return children

# ==========================================
# BFS (Breadth-First Search)
# ==========================================
def bfs_way_1(init, goal):
    frontier = deque([(init, [])])
    reached = {state_to_tuple(init)}
    steps = 0
    nodes_expanded = 0
    
    while frontier:
        steps += 1
        current, path = frontier.popleft()
        nodes_expanded += 1
        
        if current == goal:
            return path, steps, nodes_expanded, len(reached)
            
        for move, child, _ in generate_children(current):
            child_tuple = state_to_tuple(child)
            if child_tuple not in reached:
                reached.add(child_tuple)
                frontier.append((child, path + [move]))
    return None, steps, nodes_expanded, len(reached)

def bfs_way_2(init, goal):
    if init == goal:
        return [], 0, 0, 1
        
    frontier = deque([(init, [])])
    reached = {state_to_tuple(init)}
    steps = 0
    nodes_expanded = 0
    
    while frontier:
        steps += 1
        current, path = frontier.popleft()
        nodes_expanded += 1
        
        for move, child, _ in generate_children(current):
            if child == goal:
                reached.add(state_to_tuple(child))
                return path + [move], steps, nodes_expanded, len(reached)
                
            child_tuple = state_to_tuple(child)
            if child_tuple not in reached:
                reached.add(child_tuple)
                frontier.append((child, path + [move]))
    return None, steps, nodes_expanded, len(reached)

# ==========================================
# DFS (Depth-First Search)
# ==========================================
def dfs_way_1(init, goal):
    frontier = [(init, [])]
    reached = {state_to_tuple(init)}
    steps = 0
    nodes_expanded = 0
    
    while frontier:
        steps += 1
        current, path = frontier.pop()
        nodes_expanded += 1
        
        if current == goal:
            return path, steps, nodes_expanded, len(reached)
            
        for move, child, _ in reversed(generate_children(current)):
            child_tuple = state_to_tuple(child)
            if child_tuple not in reached:
                reached.add(child_tuple)
                frontier.append((child, path + [move]))
    return None, steps, nodes_expanded, len(reached)

def dfs_way_2(init, goal):
    if init == goal:
        return [], 0, 0, 1
        
    frontier = [(init, [])]
    reached = {state_to_tuple(init)}
    steps = 0
    nodes_expanded = 0
    
    while frontier:
        steps += 1
        current, path = frontier.pop()
        nodes_expanded += 1
        
        for move, child, _ in reversed(generate_children(current)):
            if child == goal:
                reached.add(state_to_tuple(child))
                return path + [move], steps, nodes_expanded, len(reached)
                
            child_tuple = state_to_tuple(child)
            if child_tuple not in reached:
                reached.add(child_tuple)
                frontier.append((child, path + [move]))
    return None, steps, nodes_expanded, len(reached)

# ==========================================
# IDS (Iterative Deepening Search)
# ==========================================
def dls_way_1(state, goal, limit, path, visited_path, stats):
    stats['steps'] += 1
    if state == goal:
        return path, True
    if limit <= 0:
        return "cutoff", False
        
    cutoff_occurred = False
    state_tuple = state_to_tuple(state)
    visited_path.add(state_tuple)
    
    for move, child, _ in generate_children(state):
        child_tuple = state_to_tuple(child)
        if child_tuple not in visited_path:
            res, found = dls_way_1(child, goal, limit - 1, path + [move], visited_path, stats)
            if found:
                return res, True
            if res == "cutoff":
                cutoff_occurred = True
                
    visited_path.remove(state_tuple)
    return "cutoff" if cutoff_occurred else None, False

def ids_way_1(init, goal):
    max_depth = 50
    total_steps = 0
    for depth in range(max_depth):
        stats = {'steps': 0}
        visited = set()
        res, found = dls_way_1(init, goal, depth, [], visited, stats)
        total_steps += stats['steps']
        if found:
            return res, depth, total_steps
        if res != "cutoff":
            break
    return None, -1, total_steps

def dls_way_2(state, goal, limit, path, visited_path, stats):
    stats['steps'] += 1
    if limit <= 0:
        return "cutoff", False
        
    cutoff_occurred = False
    state_tuple = state_to_tuple(state)
    visited_path.add(state_tuple)
    
    for move, child, _ in generate_children(state):
        if child == goal:
            return path + [move], True
            
        child_tuple = state_to_tuple(child)
        if child_tuple not in visited_path:
            res, found = dls_way_2(child, goal, limit - 1, path + [move], visited_path, stats)
            if found:
                return res, True
            if res == "cutoff":
                cutoff_occurred = True
                
    visited_path.remove(state_tuple)
    return "cutoff" if cutoff_occurred else None, False

def ids_way_2(init, goal):
    if init == goal:
        return [], 0, 0
    max_depth = 50
    total_steps = 0
    for depth in range(max_depth):
        stats = {'steps': 0}
        visited = set()
        res, found = dls_way_2(init, goal, depth, [], visited, stats)
        total_steps += stats['steps']
        if found:
            return res, depth, total_steps
        if res != "cutoff":
            break
    return None, -1, total_steps

# ==========================================
# UCS (Uniform Cost Search)
# ==========================================
def ucs(init, goal):
    heap = []
    unique_counter = 0
    heapq.heappush(heap, (0, unique_counter, init, []))
    reached = {state_to_tuple(init): 0}
    steps = 0
    nodes_expanded = 0
    
    while heap:
        steps += 1
        g_cost, _, current, path = heapq.heappop(heap)
        
        if current == goal:
            return path, g_cost, steps, nodes_expanded, len(reached)
            
        current_tuple = state_to_tuple(current)
        if g_cost > reached.get(current_tuple, float('inf')):
            continue
            
        nodes_expanded += 1
        
        for move, child, step_cost in generate_children(current):
            child_tuple = state_to_tuple(child)
            new_g = g_cost + step_cost
            if child_tuple not in reached or new_g < reached[child_tuple]:
                reached[child_tuple] = new_g
                unique_counter += 1
                heapq.heappush(heap, (new_g, unique_counter, child, path + [move]))
                
    return None, float('inf'), steps, nodes_expanded, len(reached)

def get_state_sequence(initial_state, path):
    """
    Tái tạo danh sách các trạng thái đi từ trạng thái ban đầu dựa vào chuỗi nước đi.
    """
    states = [initial_state]
    current = copy.deepcopy(initial_state)
    for move in path:
        # Tìm tọa độ ô số 0
        x, y = find_zero(current)
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
