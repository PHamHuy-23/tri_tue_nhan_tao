# CSP Solvers for Map Coloring (Australia Map)
import copy
import random

# Australia Map Variables
VARIABLES = ["WA", "NT", "Q", "NSW", "V", "SA", "T"]
DOMAINS = ["Red", "Green", "Blue"]
NEIGHBORS = {
    "WA": ["NT", "SA"],
    "NT": ["WA", "Q", "SA"],
    "Q": ["NT", "NSW", "SA"],
    "NSW": ["Q", "V", "SA"],
    "V": ["NSW", "SA"],
    "SA": ["WA", "NT", "Q", "NSW", "V"],
    "T": []  # Tasmania is isolated
}

# ==========================================
# 1. Backtracking Search
# ==========================================
def backtracking_search():
    assignment = {}
    stats = {"steps": 0, "backtracks": 0}
    
    def backtrack():
        stats["steps"] += 1
        # Nếu gán xong tất cả các biến -> Thành công
        if len(assignment) == len(VARIABLES):
            return assignment
            
        # Chọn biến chưa được gán (MRV - Minimum Remaining Values hoặc đơn giản là chọn tuần tự)
        unassigned = [v for v in VARIABLES if v not in assignment]
        var = unassigned[0]
        
        for val in DOMAINS:
            # Kiểm tra tính hợp lệ của giá trị (Consistent check)
            consistent = True
            for neighbor in NEIGHBORS[var]:
                if neighbor in assignment and assignment[neighbor] == val:
                    consistent = False
                    break
                    
            if consistent:
                assignment[var] = val
                result = backtrack()
                if result is not None:
                    return result
                # Quay lui
                del assignment[var]
                stats["backtracks"] += 1
                
        return None

    res = backtrack()
    return res, stats["steps"], stats["backtracks"]

# ==========================================
# 2. Forward Checking
# ==========================================
def forward_checking():
    assignment = {}
    # Khởi tạo domains cho tất cả các biến
    domains = {v: list(DOMAINS) for v in VARIABLES}
    stats = {"steps": 0, "backtracks": 0}
    
    def backtrack(local_domains):
        stats["steps"] += 1
        if len(assignment) == len(VARIABLES):
            return assignment
            
        unassigned = [v for v in VARIABLES if v not in assignment]
        var = unassigned[0]
        
        for val in list(local_domains[var]):
            consistent = True
            for neighbor in NEIGHBORS[var]:
                if neighbor in assignment and assignment[neighbor] == val:
                    consistent = False
                    break
            
            if consistent:
                assignment[var] = val
                # Tạo bản sao domains mới để thực hiện Forward Checking
                new_domains = copy.deepcopy(local_domains)
                new_domains[var] = [val]
                
                # Forward checking: Loại bỏ giá trị val khỏi domain của các lân cận chưa gán
                failure = False
                for neighbor in NEIGHBORS[var]:
                    if neighbor not in assignment:
                        if val in new_domains[neighbor]:
                            new_domains[neighbor].remove(val)
                            # Nếu domain của lân cận bị rỗng -> Thất bại ngay
                            if not new_domains[neighbor]:
                                failure = True
                                break
                                
                if not failure:
                    result = backtrack(new_domains)
                    if result is not None:
                        return result
                        
                # Quay lui
                del assignment[var]
                stats["backtracks"] += 1
                
        return None

    res = backtrack(domains)
    return res, stats["steps"], stats["backtracks"]

# ==========================================
# 3. AC-3 (Arc Consistency)
# ==========================================
def ac3(domains):
    """
    Thuật toán AC-3 duy trì tính nhất quán cung trên đồ thị ràng buộc.
    Trả về True nếu nhất quán, False nếu phát hiện mâu thuẫn (domain rỗng).
    """
    queue = []
    # Đưa tất cả các cung (arcs) có hướng vào hàng đợi
    for xi in VARIABLES:
        for xj in NEIGHBORS[xi]:
            queue.append((xi, xj))
            
    while queue:
        xi, xj = queue.pop(0)
        if revise(domains, xi, xj):
            # Nếu domain của xi bị rỗng -> Vô nghiệm
            if not domains[xi]:
                return False
            # Nếu domain của xi bị thay đổi, đưa các cung liên quan trở lại hàng đợi
            for xk in NEIGHBORS[xi]:
                if xk != xj:
                    queue.append((xk, xi))
    return True

def revise(domains, xi, xj):
    """
    Loại bỏ các giá trị trong domain của xi không thỏa mãn ràng buộc với xj.
    """
    revised = False
    for x in list(domains[xi]):
        # Kiểm tra xem có giá trị y nào trong domain của xj thỏa mãn ràng buộc (x != y)
        satisfied = any(x != y for y in domains[xj])
        if not satisfied:
            domains[xi].remove(x)
            revised = True
    return revised

def solve_with_ac3():
    """
    Sử dụng AC-3 để thu hẹp miền giá trị trước khi chạy Backtracking.
    """
    domains = {v: list(DOMAINS) for v in VARIABLES}
    # Chạy AC-3 tiền xử lý
    ac3_ok = ac3(domains)
    if not ac3_ok:
        return None, 0, 0
        
    assignment = {}
    stats = {"steps": 0, "backtracks": 0}
    
    def backtrack(local_domains):
        stats["steps"] += 1
        if len(assignment) == len(VARIABLES):
            return assignment
            
        unassigned = [v for v in VARIABLES if v not in assignment]
        var = unassigned[0]
        
        for val in local_domains[var]:
            consistent = True
            for neighbor in NEIGHBORS[var]:
                if neighbor in assignment and assignment[neighbor] == val:
                    consistent = False
                    break
                    
            if consistent:
                assignment[var] = val
                result = backtrack(local_domains)
                if result is not None:
                    return result
                del assignment[var]
                stats["backtracks"] += 1
        return None
        
    res = backtrack(domains)
    return res, stats["steps"], stats["backtracks"]

# ==========================================
# 4. Min-Conflicts
# ==========================================
def min_conflicts(max_steps=1000):
    """
    Thuật toán Min-Conflicts tìm kiếm cục bộ giải CSP.
    Khởi đầu bằng một gán nhãn đầy đủ ngẫu nhiên, sau đó giảm thiểu xung đột.
    """
    # Khởi tạo ngẫu nhiên toàn bộ
    current = {v: random.choice(DOMAINS) for v in VARIABLES}
    
    def get_conflicted_variables():
        conflicted = []
        for var in VARIABLES:
            for neighbor in NEIGHBORS[var]:
                if current[var] == current[neighbor]:
                    conflicted.append(var)
                    break
        return conflicted
        
    def count_conflicts(var, val):
        count = 0
        for neighbor in NEIGHBORS[var]:
            if current[neighbor] == val:
                count += 1
        return count

    for step in range(max_steps):
        conflicted = get_conflicted_variables()
        if not conflicted:
            return current, step  # Tìm thấy lời giải hợp lệ không xung đột
            
        # Chọn ngẫu nhiên một biến bị xung đột
        var = random.choice(conflicted)
        
        # Chọn giá trị tối thiểu hóa số lượng xung đột
        min_c = float('inf')
        best_vals = []
        for val in DOMAINS:
            c = count_conflicts(var, val)
            if c < min_c:
                min_c = c
                best_vals = [val]
            elif c == min_c:
                best_vals.append(val)
                
        current[var] = random.choice(best_vals)
        
    return None, max_steps
