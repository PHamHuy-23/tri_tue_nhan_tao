"""
Module containing common helper functions and utilities for the AI algorithms and projects.
Provides beautiful HTML-based visualization for Jupyter Notebooks.
"""
import copy
import time
from IPython.display import display, HTML, clear_output

def visualize_puzzle_html(state):
    """
    Trực quan hóa trạng thái 8-puzzle dưới dạng bảng HTML đẹp mắt.
    """
    html = (
        "<table style='border-collapse: collapse; border: 3px solid #2c3e50; "
        "font-family: \"Segoe UI\", Helvetica, Arial, sans-serif; font-size: 24px; "
        "text-align: center; margin: 10px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>"
    )
    for row in state:
        html += "<tr>"
        for val in row:
            if val == 0:
                # Ô trống
                bg = "#ecf0f1"
                color = "#ecf0f1"
                cell_val = ""
            else:
                # Ô số
                bg = "#3498db"
                color = "white"
                cell_val = str(val)
            html += (
                f"<td style='width: 60px; height: 60px; border: 2px solid #bdc3c7; "
                f"background-color: {bg}; color: {color}; font-weight: bold; "
                f"border-radius: 4px; transition: background-color 0.3s;'>{cell_val}</td>"
            )
        html += "</tr>"
    html += "</table>"
    return html

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

def animate_solution(initial_state, path, delay=0.8):
    """
    Tạo hiệu ứng animation từng bước di chuyển trực quan trong Jupyter Notebook.
    """
    states = get_state_sequence(initial_state, path)
    for i, state in enumerate(states):
        clear_output(wait=True)
        if i == 0:
            header = "<h3 style='color: #2c3e50;'>🏁 Trạng thái ban đầu:</h3>"
        else:
            header = f"<h3 style='color: #e67e22;'>Bước {i}: Di chuyển sang [{path[i-1]}]</h3>"
        
        # Render HTML
        display(HTML(header + visualize_puzzle_html(state)))
        time.sleep(delay)
