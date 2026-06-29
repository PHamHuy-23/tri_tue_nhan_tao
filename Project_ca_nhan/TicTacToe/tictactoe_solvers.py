# Tic-Tac-Toe Adversarial Search Solvers
# Board is represented as a list of 9 integers:
# 1: X (MAX)
# -1: O (MIN)
# 0: Empty

def is_terminal(board):
    win_lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for line in win_lines:
        s = board[line[0]] + board[line[1]] + board[line[2]]
        if s == 3:
            return True, 1
        elif s == -3:
            return True, -1
            
    if 0 not in board:
        return True, 0 # Draw
        
    return False, None

def get_actions(board):
    return [i for i, val in enumerate(board) if val == 0]

# ==========================================
# 1. Minimax
# ==========================================
def minimax(board, depth, is_max, stats):
    stats["nodes"] += 1
    terminal, winner = is_terminal(board)
    if terminal:
        return winner * 10 - depth if winner != 0 else 0, None
        
    actions = get_actions(board)
    best_move = None
    
    if is_max:
        best_val = -float('inf')
        for action in actions:
            new_board = list(board)
            new_board[action] = 1
            val, _ = minimax(new_board, depth + 1, False, stats)
            if val > best_val:
                best_val = val
                best_move = action
        return best_val, best_move
    else:
        best_val = float('inf')
        for action in actions:
            new_board = list(board)
            new_board[action] = -1
            val, _ = minimax(new_board, depth + 1, True, stats)
            if val < best_val:
                best_val = val
                best_move = action
        return best_val, best_move

# ==========================================
# 2. Alpha-Beta Pruning
# ==========================================
def alpha_beta(board, depth, alpha, beta, is_max, stats):
    stats["nodes"] += 1
    terminal, winner = is_terminal(board)
    if terminal:
        return winner * 10 - depth if winner != 0 else 0, None
        
    actions = get_actions(board)
    best_move = None
    
    if is_max:
        best_val = -float('inf')
        for action in actions:
            new_board = list(board)
            new_board[action] = 1
            val, _ = alpha_beta(new_board, depth + 1, alpha, beta, False, stats)
            if val > best_val:
                best_val = val
                best_move = action
            alpha = max(alpha, best_val)
            if beta <= alpha:
                stats["prunes"] += 1
                break
        return best_val, best_move
    else:
        best_val = float('inf')
        for action in actions:
            new_board = list(board)
            new_board[action] = -1
            val, _ = alpha_beta(new_board, depth + 1, alpha, beta, True, stats)
            if val < best_val:
                best_val = val
                best_move = action
            beta = min(beta, best_val)
            if beta <= alpha:
                stats["prunes"] += 1
                break
        return best_val, best_move

# ==========================================
# 3. Expectimax
# ==========================================
def expectimax_X(board, depth, is_max_turn, stats):
    stats["nodes"] += 1
    terminal, winner = is_terminal(board)
    if terminal:
        return winner * 10 - depth if winner != 0 else 0, None
        
    actions = get_actions(board)
    best_move = None
    
    if is_max_turn:
        best_val = -float('inf')
        for action in actions:
            new_board = list(board)
            new_board[action] = 1
            val, _ = expectimax_X(new_board, depth + 1, False, stats)
            if val > best_val:
                best_val = val
                best_move = action
        return best_val, best_move
    else:
        total_val = 0.0
        prob = 1.0 / len(actions)
        for action in actions:
            new_board = list(board)
            new_board[action] = -1
            val, _ = expectimax_X(new_board, depth + 1, True, stats)
            total_val += val * prob
        return total_val, None

def expectimax_O(board, depth, is_min_turn, stats):
    stats["nodes"] += 1
    terminal, winner = is_terminal(board)
    if terminal:
        return winner * 10 - depth if winner != 0 else 0, None
        
    actions = get_actions(board)
    best_move = None
    
    if is_min_turn:
        best_val = float('inf')
        for action in actions:
            new_board = list(board)
            new_board[action] = -1
            val, _ = expectimax_O(new_board, depth + 1, False, stats)
            if val < best_val:
                best_val = val
                best_move = action
        return best_val, best_move
    else:
        total_val = 0.0
        prob = 1.0 / len(actions)
        for action in actions:
            new_board = list(board)
            new_board[action] = 1
            val, _ = expectimax_O(new_board, depth + 1, True, stats)
            total_val += val * prob
        return total_val, None

def expectimax(board, depth, is_max, stats):
    if is_max:
        return expectimax_X(board, depth, True, stats)
    else:
        return expectimax_O(board, depth, True, stats)
