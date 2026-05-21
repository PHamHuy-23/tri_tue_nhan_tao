from .bfs import bfs
from .bfs_goal_on_generate import bfs_goal_on_generate
from .dfs import dfs
from .dfs_goal_on_generate import dfs_goal_on_generate

GOAL_PUZZLE = (1, 2, 3, 4, 5, 6, 7, 8, 0)


def run_algorithm(algorithm_name, start_state, goal_state, get_next_states, max_steps=None):
    algorithms = {
        "bfs1": bfs,
        "bfs2": bfs_goal_on_generate,
        "dfs1": dfs,
        "dfs2": dfs_goal_on_generate,
    }
    return algorithms[algorithm_name](start_state, goal_state, get_next_states, max_steps=max_steps)


def get_puzzle_next_states(state):
    state = list(state)
    empty = state.index(0)
    row = empty // 3
    col = empty % 3
    next_indexes = []

    if row > 0:
        next_indexes.append(empty - 3)
    if row < 2:
        next_indexes.append(empty + 3)
    if col > 0:
        next_indexes.append(empty - 1)
    if col < 2:
        next_indexes.append(empty + 1)

    next_states = []
    for index in next_indexes:
        new_state = state.copy()
        new_state[empty], new_state[index] = new_state[index], new_state[empty]
        next_states.append(tuple(new_state))

    return next_states


def run_puzzle_search(algorithm_name, board):
    start_state = tuple(board)
    return run_algorithm(algorithm_name, start_state, GOAL_PUZZLE, get_puzzle_next_states, max_steps=5000)


def point_to_grid(x, y, room_x, room_y, cell_size):
    return (int((x - room_x) // cell_size), int((y - room_y) // cell_size))


def grid_to_point(cell, room_x, room_y, cell_size):
    col, row = cell
    return (
        room_x + col * cell_size + cell_size / 2,
        room_y + row * cell_size + cell_size / 2,
    )


def get_vacuum_next_states(state, cols, rows):
    col, row = state
    candidates = [
        (col, row - 1),
        (col - 1, row),
        (col + 1, row),
        (col, row + 1),
    ]

    return [
        (next_col, next_row)
        for next_col, next_row in candidates
        if 0 <= next_col < cols and 0 <= next_row < rows
    ]


def find_nearest_dirty_cell(robot_cell, dirt_cells):
    if not dirt_cells:
        return None

    return min(
        dirt_cells,
        key=lambda cell: abs(robot_cell[0] - cell[0]) + abs(robot_cell[1] - cell[1]),
    )


def run_vacuum_search(algorithm_name, robot_x, robot_y, dirt, room_x, room_y, room_w, room_h, cell_size):
    cols = int(room_w // cell_size)
    rows = int(room_h // cell_size)
    start_state = point_to_grid(robot_x, robot_y, room_x, room_y, cell_size)

    dirt_cells = {
        point_to_grid(spot["x"], spot["y"], room_x, room_y, cell_size)
        for spot in dirt
        if not spot["clean"]
    }
    goal_state = find_nearest_dirty_cell(start_state, dirt_cells)

    if goal_state is None:
        return []

    return run_algorithm(
        algorithm_name,
        start_state,
        goal_state,
        lambda state: get_vacuum_next_states(state, cols, rows),
        max_steps=3000,
    )
