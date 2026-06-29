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


# ==========================================
# HEURISTIC FUNCTIONS
# ==========================================

def h_hamming(state, goal):
    """
    Hamming Heuristic (Misplaced tiles - ignoring empty tile 0)
    """
    count = 0
    for r in range(3):
        for c in range(3):
            val = state[r][c]
            if val != 0 and val != goal[r][c]:
                count += 1
    return count

def h_manhattan(state, goal):
    """
    Manhattan Distance Heuristic (ignoring empty tile 0)
    """
    goal_pos = {}
    for r in range(3):
        for c in range(3):
            goal_pos[goal[r][c]] = (r, c)
            
    dist = 0
    for r in range(3):
        for c in range(3):
            val = state[r][c]
            if val != 0:
                gr, gc = goal_pos[val]
                dist += abs(r - gr) + abs(c - gc)
    return dist

def h_euclidean(state, goal):
    """
    Euclidean Distance Heuristic (ignoring empty tile 0)
    """
    goal_pos = {}
    for r in range(3):
        for c in range(3):
            goal_pos[goal[r][c]] = (r, c)
            
    dist = 0.0
    for r in range(3):
        for c in range(3):
            val = state[r][c]
            if val != 0:
                gr, gc = goal_pos[val]
                dist += math.sqrt((r - gr)**2 + (c - gc)**2)
    return dist

# ==========================================
# INFORMED SEARCH ALGORITHMS
# ==========================================

def greedy(init, goal, h_func):
    """
    Greedy Best-First Search
    """
    heap = []
    unique_counter = 0
    h_init = h_func(init, goal)
    heapq.heappush(heap, (h_init, unique_counter, init, []))
    reached = {state_to_tuple(init)}
    steps = 0
    nodes_expanded = 0
    
    while heap:
        steps += 1
        h_cost, _, current, path = heapq.heappop(heap)
        
        if current == goal:
            return path, steps, nodes_expanded, len(reached)
            
        nodes_expanded += 1
        for move, child, _ in generate_children(current):
            child_tuple = state_to_tuple(child)
            if child_tuple not in reached:
                reached.add(child_tuple)
                unique_counter += 1
                h_val = h_func(child, goal)
                heapq.heappush(heap, (h_val, unique_counter, child, path + [move]))
    return None, steps, nodes_expanded, len(reached)

def astar(init, goal, h_func):
    """
    A* Search
    """
    heap = []
    unique_counter = 0
    h_init = h_func(init, goal)
    heapq.heappush(heap, (h_init, unique_counter, init, [], 0))
    reached = {state_to_tuple(init): 0}
    steps = 0
    nodes_expanded = 0
    
    while heap:
        steps += 1
        f_cost, _, current, path, g_cost = heapq.heappop(heap)
        
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
                f_val = new_g + h_func(child, goal)
                heapq.heappush(heap, (f_val, unique_counter, child, path + [move], new_g))
    return None, float('inf'), steps, nodes_expanded, len(reached)

def idastar(init, goal, h_func):
    """
    IDA* Search
    """
    def search(path, g, f_limit, visited, stats):
        stats['steps'] += 1
        current = path[-1]
        f = g + h_func(current, goal)
        if f > f_limit:
            return f, False, None
        if current == goal:
            return f, True, path
            
        min_val = float('inf')
        state_tuple = state_to_tuple(current)
        visited.add(state_tuple)
        
        for move, child, step_cost in generate_children(current):
            child_tuple = state_to_tuple(child)
            if child_tuple not in visited:
                res_f, found, res_path = search(path + [child], g + step_cost, f_limit, visited, stats)
                if found:
                    return res_f, True, res_path
                if res_f < min_val:
                    min_val = res_f
                    
        visited.remove(state_tuple)
        return min_val, False, None

    if init == goal:
        return [], 0, 1
        
    f_limit = h_func(init, goal)
    total_steps = 0
    max_iterations = 100
    
    for _ in range(max_iterations):
        stats = {'steps': 0}
        visited = set()
        res_f, found, res_path = search([init], 0, f_limit, visited, stats)
        total_steps += stats['steps']
        if found:
            # Reconstruct path of moves from states path
            move_path = []
            for idx in range(len(res_path) - 1):
                curr = res_path[idx]
                nxt = res_path[idx+1]
                for m, child, _ in generate_children(curr):
                    if child == nxt:
                        move_path.append(m)
                        break
            return move_path, f_limit, total_steps
        if res_f == float('inf'):
            break
        f_limit = res_f
    return None, -1, total_steps
