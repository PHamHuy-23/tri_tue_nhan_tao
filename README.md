# 🤖 Trí Tuệ Nhân Tạo (Artificial Intelligence)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.14+-blue.svg?style=flat-edge&logo=python" alt="Python Version">
  <img src="https://img.shields.io/badge/Environment-Jupyter%20%7C%20VS%20Code-orange.svg?style=flat-edge" alt="Environment">
  <img src="https://img.shields.io/badge/Status-In%20Progress-yellow.svg?style=flat-edge" alt="Status">
</p>

## 📌 Giới thiệu

Repository này lưu trữ mã nguồn, bài tập về nhà và các đồ án môn học thuộc học phần **Trí Tuệ Nhân Tạo (252ARIN330585_06)**.

Mục tiêu cốt lõi của repository là hiện thực hóa các giải thuật tìm kiếm, tối ưu hóa, lập luận logic và các mô hình học máy cơ bản từ lý thuyết vào mã nguồn thực tế, có kèm theo minh họa trực quan.

### 👤 Thông tin cá nhân

* **Họ và tên:** Phạm Quốc Huy ([@PHamHuy-23](https://github.com/PHamHuy-23))
* **Mã số sinh viên:** 24110226
* **Ngôn ngữ lập trình:** Python (3.14+)
* **Môi trường phát triển:** Jupyter Notebook, VS Code, v.v.

---

## 🏆 Đồ án cá nhân (Personal Projects)

### 🧹 1. Bài toán máy hút bụi (Vacuum Cleaner World)
* **Thuật toán áp dụng:**
  * Tìm kiếm mù: BFS, DFS, IDS, UCS
  * Tìm kiếm có thông tin: Greedy Best-First Search, A\*, IDA\*
  * Tìm kiếm cục bộ: Hill Climbing (các biến thể)
* **Tính năng:**
  * Giao diện trực quan (Visualizer).
  * Hiển thị chi tiết log và từng bước thực hiện.
  * Hỗ trợ theo dõi quá trình tìm kiếm theo thời gian thực.

---

### 🎨 2. Bài toán tô màu bản đồ (Map Coloring)
* **Thuật toán áp dụng:**
  * Backtracking Search
  * Forward Checking
  * AC-3 (Arc Consistency)
  * Min-Conflicts
* **Tính năng:**
  * Giao diện đồ thị trực quan hiển thị quá trình gán màu.
  * Hiển thị log từng bước và số bước quay lui (backtracks).

---

### ❌ 3. Trò chơi Tic-Tac-Toe (Tic-Tac-Toe Game)
* **Thuật toán áp dụng:**
  * Minimax
  * Alpha-Beta Pruning
  * Expectimax
* **Tính năng:**
  * Tương tác chơi trực tiếp (Người vs AI, AI vs AI).
  * Giao diện trực quan sống động.
  * Hiển thị log phân tích nước đi và điểm lượng giá (utility).

---
---

## 🚀 Hướng dẫn chạy ứng dụng trực quan hợp nhất (AI Launcher Hub)

Để mang lại trải nghiệm tiện lợi nhất, toàn bộ 5 bài toán trực quan hóa tương tác lớn đã được gộp chung vào một ứng dụng chạy duy nhất **`main.py`** sử dụng thư viện đồ họa **Pygame**.

### 🛠️ Cài đặt thư viện yêu cầu:
Trước khi chạy, hãy đảm bảo bạn đã cài đặt các thư viện cần thiết bằng lệnh:
```bash
pip install -r requirements.txt
```

### 🎮 Khởi chạy Launcher:
Chỉ cần chạy lệnh sau tại thư mục gốc của repository:
```bash
python main.py
```

Khi ứng dụng mở lên, bạn sẽ thấy giao diện **Menu Launcher hiện đại** cho phép chuyển đổi nhanh qua lại giữa cả 5 ứng dụng trực quan (8-Puzzle, N-Queens, Vacuum Grid, Map Coloring, Tic-Tac-Toe) bằng các cú click chuột mà không cần tắt chương trình.

---

## 🧠 Các giải thuật triển khai (Algorithms)

### 1. Tìm kiếm mù (Uninformed Search)

#### 🔹 BFS (Breadth-First Search)
Duyệt tất cả các nút ở độ sâu $d$ trước khi xuống độ sâu $d+1$. Sử dụng hàng đợi **Queue (FIFO)**.
* **Cách 1 (Standard):** Goal-test khi lấy nút ra khỏi hàng đợi.
* **Cách 2 (Early Goal Check):** Kiểm tra Goal-test ngay khi sinh nút con (Tối ưu số lượng nút duyệt).

#### 🔹 DFS (Depth-First Search)
Ưu tiên duyệt nhánh sâu nhất trước. Sử dụng cấu trúc **Stack (LIFO)** hoặc đệ quy.
* **Cách 1 (Standard):** DFS cơ bản sử dụng Closed Set để tránh lặp trạng thái.
* **Cách 2 (Early Goal Check):** Kiểm tra Goal-test ngay khi sinh nút con.

#### 🔹 IDS (Iterative Deepening Search)
Kết hợp ưu điểm bộ nhớ của DFS và tính tối ưu của BFS bằng cách chạy DFS giới hạn độ sâu tăng dần.
* **Cách 1 (Standard):** Tăng tuyến tính giới hạn độ sâu sau mỗi vòng lặp.
* **Cách 2 (Early Goal Check):** Kiểm tra Goal-test sớm khi sinh nút con.

#### 🔹 UCS (Uniform Cost Search)
Mở rộng nút có chi phí đường đi thấp nhất từ nút gốc:
$$f(n) = g(n)$$
* **Đặc điểm:** Sử dụng **Priority Queue**; đảm bảo tìm được đường đi ngắn nhất trên đồ thị có trọng số không âm.

---

### 2. Tìm kiếm có thông tin (Informed Search)

#### 🔹 Greedy Best-First Search
Lựa chọn nút có giá trị heuristic tốt nhất:
$$f(n) = h(n)$$
* **Đặc điểm:** Tốc độ tìm kiếm nhanh nhưng không đảm bảo tính tối ưu.

#### 🔹 A* Search
Tìm kiếm tối ưu toàn cục kết hợp giữa chi phí thực tế và ước lượng:
$$f(n) = g(n) + h(n)$$
* **Đặc điểm:** Đảm bảo tối ưu và hoàn chỉnh nếu hàm heuristic $h(n)$ là admissible (không đánh giá vượt quá chi phí thực tế).

#### 🔹 IDA* (Iterative Deepening A*)
Sự kết hợp giữa IDS và hàm đánh giá của A*.
* **Đặc điểm:** Thực hiện tìm kiếm theo từng ngưỡng $f(n)$ tăng dần thay vì lưu toàn bộ frontier, giúp tiết kiệm bộ nhớ đáng kể.

---

### 3. Tìm kiếm cục bộ (Local Search)

* **Simple Hill Climbing:** Chọn trạng thái lân cận đầu tiên có giá trị tốt hơn trạng thái hiện tại.
* **Steepest Ascent Hill Climbing:** Đánh giá toàn bộ các lân cận và chọn trạng thái tốt nhất.
* **Stochastic Hill Climbing:** Chọn ngẫu nhiên một trạng thái tốt hơn từ tập lân cận khả thi.
* **Random-Restart Hill Climbing:** Khởi động lại nhiều lần từ các trạng thái ngẫu nhiên khi bị kẹt để tìm cực trị toàn cục.
* **Local Beam Search:** Theo dõi đồng thời $k$ trạng thái. Tại mỗi bước, sinh ra tất cả các trạng thái lân cận và chỉ giữ lại $k$ trạng thái tốt nhất.
* **Simulated Annealing:** Mô phỏng quá trình luyện kim. Chấp nhận các bước đi tệ hơn với xác suất giảm dần theo nhiệt độ $T$:
$$p = e^{-\frac{\Delta}{T}}$$

---

### 4. Tìm kiếm trong môi trường phức tạp (Complex Environments)

Phù hợp cho các môi trường thực tế không hoàn hảo:

* **Môi trường không nhìn thấy (Unobservable):** Tác nhân sử dụng **Belief State** (tập hợp tất cả các trạng thái khả dĩ) để lập kế hoạch không cần cảm biến.
* **Môi trường nhìn thấy một phần (Partially Observable):** Cập nhật **Belief State** dựa trên hành động đã thực hiện và thông tin thu nhận từ cảm biến.
* **Môi trường không xác định (Nondeterministic):** Cài đặt thuật toán **AND-OR Graph Search** để tạo kế hoạch điều kiện (Conditional Plan) đối phó với nhiều kết quả có thể xảy ra của một hành động.

---

### 5. Bài toán thỏa mãn ràng buộc (CSP)

Tìm kiếm các trạng thái thỏa mãn một tập hợp điều kiện cho trước:
* **Backtracking Search:** Thuật toán đệ quy gán giá trị và quay lui khi gặp xung đột.
* **Forward Checking:** Dự đoán sớm xung đột bằng cách loại bỏ các giá trị không hợp lệ trong miền của các biến chưa gán kề với biến vừa gán.
* **AC-3 (Arc Consistency):** Duy trì tính nhất quán cung trên toàn bộ đồ thị ràng buộc trước/trong khi tìm kiếm để thu hẹp đáng kể miền giá trị.
* **Min-Conflicts:** Thuật toán tìm kiếm cục bộ gán giá trị đầy đủ và liên tục thay đổi giá trị gây ít xung đột nhất.

---

### 6. Tìm kiếm đối kháng (Adversarial Search)

Áp dụng cho các trò chơi hai người đối kháng trực tiếp:
* **Minimax:** Giả định đối thủ chơi tối ưu; MAX chọn nước đi lớn nhất và MIN chọn nước đi nhỏ nhất.
* **Alpha-Beta Pruning:** Cắt tỉa các nhánh không ảnh hưởng đến quyết định cuối cùng giúp tối ưu thời gian duyệt cây:
$$\alpha \ge \beta$$
* **Expectimax:** Thay thế các nút đối thủ bằng các nút cơ hội (Chance nodes) tính giá trị kỳ vọng khi đối thủ chơi ngẫu nhiên hoặc có yếu tố xúc xắc.

---

## 📈 Tổng kết
Repository này được xây dựng nhằm cung cấp cái nhìn chi tiết từ lý thuyết đến thực hành của các thuật toán AI cốt lõi, giúp người học dễ dàng tiếp cận và ứng dụng thực tế.
