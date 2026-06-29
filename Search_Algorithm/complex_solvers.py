# Complex Environments Solvers for Vacuum Cleaner World

# States are represented as tuples: (position, left_dirt, right_dirt)
# position: 0 (Left), 1 (Right)
# left_dirt: 0 (Clean), 1 (Dirty)
# right_dirt: 0 (Clean), 1 (Dirty)

ALL_STATES = [
    (pos, left, right) 
    for pos in [0, 1] 
    for left in [0, 1] 
    for right in [0, 1]
]

def is_goal_state(state):
    # Trạng thái mục tiêu là cả 2 phòng đều sạch
    return state[1] == 0 and state[2] == 0

def transition(state, action):
    """
    Hàm chuyển trạng thái xác định (Deterministic Transition)
    """
    pos, left, right = state
    if action == "TRÁI":
        return (0, left, right)
    elif action == "PHẢI":
        return (1, left, right)
    elif action == "HÚT":
        if pos == 0:
            return (0, 0, right)
        else:
            return (1, left, 0)
    return state

# ==========================================
# 1. Blind Search (Môi trường không nhìn thấy)
# ==========================================
def predict_belief(belief, action):
    """
    Tính Belief State tiếp theo sau khi thực hiện hành động (không có sensor)
    """
    new_belief = set()
    for state in belief:
        new_belief.add(transition(state, action))
    return frozenset(new_belief)

def is_belief_goal(belief):
    """
    Một Belief State đạt mục tiêu khi TẤT CẢ các trạng thái khả dĩ trong đó đạt mục tiêu.
    """
    if not belief:
        return False
    return all(is_goal_state(s) for s in belief)

def blind_search():
    """
    Tìm kiếm mù sử dụng BFS trên không gian Belief States.
    Khởi đầu: Tác nhân không biết gì cả (Belief State chứa tất cả 8 trạng thái khả dĩ).
    """
    initial_belief = frozenset(ALL_STATES)
    frontier = [ (initial_belief, []) ]
    reached = {initial_belief}
    
    while frontier:
        current_belief, path = frontier.pop(0)
        
        if is_belief_goal(current_belief):
            return path, current_belief
            
        for action in ["TRÁI", "PHẢI", "HÚT"]:
            next_belief = predict_belief(current_belief, action)
            if next_belief not in reached:
                reached.add(next_belief)
                frontier.append((next_belief, path + [action]))
                
    return None, None

# ==========================================
# 2. Partially Observable (Nhìn thấy một phần)
# ==========================================
def get_sensor_percept(state):
    """
    Cảm biến trả về: (vị trí hiện tại, độ sạch của ô hiện tại)
    Ví dụ: (0, 1) nghĩa là đang ở ô Trái (0) và ô Trái bị bẩn (1)
    """
    pos, left, right = state
    current_dirt = left if pos == 0 else right
    return (pos, current_dirt)

def update_belief_partial(belief, action, percept):
    """
    Cập nhật Belief State sau khi hành động và nhận quan sát cảm biến mới.
    """
    # Bước 1: Tiên đoán (Predict)
    predicted = predict_belief(belief, action)
    # Bước 2: Lọc (Filter) theo cảm biến
    filtered = set()
    for state in predicted:
        if get_sensor_percept(state) == percept:
            filtered.add(state)
    return frozenset(filtered)

# ==========================================
# 3. AND-OR Graph Search (Môi trường không xác định)
# ==========================================
# Mô tả hành động không xác định:
# Khi HÚT ở ô bẩn, có 80% cơ hội ô sạch (succeed), 20% ô vẫn bẩn (fail).
# Khi TRÁI/PHẢI, có 90% thành công, 10% bị trượt đứng yên.
def nondeterministic_transition(state, action):
    pos, left, right = state
    results = []
    
    if action == "TRÁI":
        results.append((0, left, right))  # Thành công đi sang trái
        results.append((pos, left, right)) # Bị trượt đứng yên
    elif action == "PHẢI":
        results.append((1, left, right))  # Thành công đi sang phải
        results.append((pos, left, right)) # Bị trượt đứng yên
    elif action == "HÚT":
        if pos == 0:
            results.append((0, 0, right)) # Thành công hút sạch
            results.append((0, 1, right)) # Hút thất bại vẫn bẩn
        else:
            results.append((1, left, 0)) # Thành công
            results.append((1, left, 1)) # Thất bại
            
    # Loại bỏ trạng thái trùng lặp
    return list(set(results))

def and_or_graph_search(init_state):
    """
    Tìm kiếm trên đồ thị AND-OR từ trạng thái ban đầu.
    Trả về một Kế hoạch điều kiện (Conditional Plan) dạng dict/nested list.
    """
    def or_search(state, path):
        if is_goal_state(state):
            return []  # Kế hoạch rỗng
        if state in path:
            return None # Bị lặp chu trình vô hạn
            
        # Thử lần lượt các hành động
        for action in ["TRÁI", "PHẢI", "HÚT"]:
            plan = and_search(nondeterministic_transition(state, action), path + [state])
            if plan is not None:
                return [action, plan]
        return None

    def and_search(states, path):
        # Kế hoạch phải xử lý TẤT CẢ các kết quả đầu ra có thể xảy ra của hành động (nhánh AND)
        plan = {}
        for s in states:
            s_plan = or_search(s, path)
            if s_plan is None:
                return None
            plan[s] = s_plan
        return plan

    return or_search(init_state, [])
