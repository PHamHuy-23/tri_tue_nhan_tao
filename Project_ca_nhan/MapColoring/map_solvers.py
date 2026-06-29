import copy
import random

def get_colors(num_colors):
    all_colors = ["Red", "Green", "Blue", "Yellow", "Orange", "Purple"]
    return all_colors[:num_colors]

# ==========================================
# 1. Backtracking Search (Step Recording)
# ==========================================
def solve_backtracking(nodes, adj, num_colors):
    assignment = {}
    history = [] # Lưu các bước gán/thu hồi để trực quan hóa
    stats = {"steps": 0, "backtracks": 0}
    colors = get_colors(num_colors)
    
    def backtrack():
        stats["steps"] += 1
        history.append(copy.deepcopy(assignment))
        
        if len(assignment) == len(nodes):
            return assignment
            
        unassigned = [n for n in nodes if n not in assignment]
        # Thử chọn biến bằng Heuristic MRV (Minimum Remaining Values - Số màu hợp lệ ít nhất)
        unassigned.sort(key=lambda var: len([c for c in colors if is_consistent(var, c)]))
        var = unassigned[0]
        
        for val in colors:
            if is_consistent(var, val):
                assignment[var] = val
                history.append(copy.deepcopy(assignment))
                
                result = backtrack()
                if result is not None:
                    return result
                    
                del assignment[var]
                stats["backtracks"] += 1
                history.append(copy.deepcopy(assignment))
                
        return None

    def is_consistent(var, val):
        for neighbor in adj.get(var, []):
            if neighbor in assignment and assignment[neighbor] == val:
                return False
        return True

    res = backtrack()
    return res, stats["steps"], stats["backtracks"], history

# ==========================================
# 2. Forward Checking (Step Recording)
# ==========================================
def solve_forward_checking(nodes, adj, num_colors):
    assignment = {}
    history = []
    stats = {"steps": 0, "backtracks": 0}
    colors = get_colors(num_colors)
    domains = {n: list(colors) for n in nodes}
    
    def backtrack(local_domains):
        stats["steps"] += 1
        history.append(copy.deepcopy(assignment))
        
        if len(assignment) == len(nodes):
            return assignment
            
        unassigned = [n for n in nodes if n not in assignment]
        # MRV heuristic
        unassigned.sort(key=lambda var: len(local_domains[var]))
        var = unassigned[0]
        
        for val in list(local_domains[var]):
            consistent = True
            for neighbor in adj.get(var, []):
                if neighbor in assignment and assignment[neighbor] == val:
                    consistent = False
                    break
                    
            if consistent:
                assignment[var] = val
                history.append(copy.deepcopy(assignment))
                
                new_domains = copy.deepcopy(local_domains)
                new_domains[var] = [val]
                
                # Forward checking
                failure = False
                for neighbor in adj.get(var, []):
                    if neighbor not in assignment:
                        if val in new_domains[neighbor]:
                            new_domains[neighbor].remove(val)
                            if not new_domains[neighbor]:
                                failure = True
                                break
                                
                if not failure:
                    result = backtrack(new_domains)
                    if result is not None:
                        return result
                        
                del assignment[var]
                stats["backtracks"] += 1
                history.append(copy.deepcopy(assignment))
                
        return None

    res = backtrack(domains)
    return res, stats["steps"], stats["backtracks"], history

# ==========================================
# 3. AC-3 (Step Recording)
# ==========================================
def solve_ac3(nodes, adj, num_colors):
    colors = get_colors(num_colors)
    domains = {n: list(colors) for n in nodes}
    
    # AC-3 preprocessing
    queue = []
    for xi in nodes:
        for xj in adj.get(xi, []):
            queue.append((xi, xj))
            
    while queue:
        xi, xj = queue.pop(0)
        # Revise
        revised = False
        for x in list(domains[xi]):
            satisfied = any(x != y for y in domains[xj])
            if not satisfied:
                domains[xi].remove(x)
                revised = True
        if revised:
            if not domains[xi]:
                return None, 0, 0, [] # Mâu thuẫn vô nghiệm
            for xk in adj.get(xi, []):
                if xk != xj:
                    queue.append((xk, xi))
                    
    # Chạy Backtracking với miền giá trị đã thu hẹp
    assignment = {}
    history = []
    stats = {"steps": 0, "backtracks": 0}
    
    def backtrack(local_domains):
        stats["steps"] += 1
        history.append(copy.deepcopy(assignment))
        
        if len(assignment) == len(nodes):
            return assignment
            
        unassigned = [n for n in nodes if n not in assignment]
        unassigned.sort(key=lambda var: len(local_domains[var]))
        var = unassigned[0]
        
        for val in local_domains[var]:
            consistent = True
            for neighbor in adj.get(var, []):
                if neighbor in assignment and assignment[neighbor] == val:
                    consistent = False
                    break
                    
            if consistent:
                assignment[var] = val
                history.append(copy.deepcopy(assignment))
                
                result = backtrack(local_domains)
                if result is not None:
                    return result
                    
                del assignment[var]
                stats["backtracks"] += 1
                history.append(copy.deepcopy(assignment))
        return None
        
    res = backtrack(domains)
    return res, stats["steps"], stats["backtracks"], history

# ==========================================
# 4. Min-Conflicts (Step Recording)
# ==========================================
def solve_min_conflicts(nodes, adj, num_colors, max_steps=1000):
    colors = get_colors(num_colors)
    if not nodes:
        return {}, 0, []
        
    current = {n: random.choice(colors) for n in nodes}
    history = [copy.deepcopy(current)]
    
    def get_conflicted():
        conflicted = []
        for var in nodes:
            for neighbor in adj.get(var, []):
                if current[var] == current[neighbor]:
                    conflicted.append(var)
                    break
        return conflicted
        
    def count_conflicts(var, val):
        count = 0
        for neighbor in adj.get(var, []):
            if current[neighbor] == val:
                count += 1
        return count

    for step in range(max_steps):
        conflicted = get_conflicted()
        if not conflicted:
            return current, step, history
            
        var = random.choice(conflicted)
        min_c = float('inf')
        best_vals = []
        
        for val in colors:
            c = count_conflicts(var, val)
            if c < min_c:
                min_c = c
                best_vals = [val]
            elif c == min_c:
                best_vals.append(val)
                
        current[var] = random.choice(best_vals)
        history.append(copy.deepcopy(current))
        
    return None, max_steps, history
