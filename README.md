<h1 align="center">Trí Tuệ Nhân Tạo</h1>

## Giới thiệu

Repository này lưu trữ mã nguồn, bài tập về nhà và bài tập trên lớp liên quan đến môn học **Trí Tuệ Nhân Tạo (252ARIN330585_06)**.

Mục tiêu cốt lõi của repository là hiện thực hóa các giải thuật tìm kiếm, tối ưu hóa, lập luận logic và các mô hình học máy cơ bản từ lý thuyết vào mã nguồn thực tế.

### Thông tin cá nhân

* **Họ và tên:** Nguyễn Đình Khanh ([@qilskcter](https://github.com/qilskcter))
* **Mã số sinh viên:** 24110244
* **Ngôn ngữ lập trình:** Python 3.14.3
* **Môi trường phát triển:** Jupyter Notebook, VS Code, v.v.

---

## Project cá nhân

### Bài toán máy hút bụi

#### Tính năng

* Sử dụng các giải thuật đã học như:

  * BFS
  * DFS
  * IDS
  * UCS
  * Greedy
  * A*
  * IDA*
  * Hill Climbing

* Có giao diện trực quan (Visualizer).

* Hiển thị log và từng bước thực hiện.

* Hỗ trợ theo dõi quá trình tìm kiếm theo thời gian thực.

---

### Bài toán tô màu bản đồ

#### Tính năng

* Sử dụng các giải thuật đã học như:

  * Backtracking
  * Forward Checking
  * AC-3
  * Min-Conflicts

* Có giao diện trực quan (Visualizer).

* Hiển thị log và từng bước thực hiện.

---

### Bài toán trò chơi Tic-Tac-Toe

#### Tính năng

* Sử dụng các giải thuật đã học như:

  * Minimax
  * Alpha-Beta Pruning
  * Expectimax

* Có thể tương tác được với trò chơi.

* Có giao diện trực quan (Visualizer).

* Hiển thị log và từng bước thực hiện.

---

### Liên kết Project

[Project cá nhân](./Project_ca_nhan/)

---

## Các thuật toán

## 1. Tìm kiếm mù (Uninformed Search)

### BFS (Breadth-First Search)

Phát triển tất cả các nút ở độ sâu $d$ trước khi chuyển xuống độ sâu $d+1$. Thuật toán sử dụng cấu trúc dữ liệu **Queue (FIFO)**.

#### Các cách tiếp cận

* **Cách 1:** BFS truyền thống với Goal-test khi lấy nút ra khỏi hàng đợi.
* **Cách 2 (Early Goal Check):** Tối ưu bằng cách kiểm tra Goal-test ngay khi sinh nút con.

---

### DFS (Depth-First Search)

Ưu tiên phát triển nút ở độ sâu lớn nhất hiện tại. Thuật toán sử dụng **Stack (LIFO)** hoặc đệ quy.

#### Các cách tiếp cận

* **Cách 1:** DFS cơ bản (Graph Search) với Closed Set.
* **Cách 2 (Early Goal Check):** Kiểm tra Goal-test ngay khi sinh nút con.

---

### IDS (Iterative Deepening Search)

Kết hợp tính tối ưu của BFS và hiệu quả bộ nhớ của DFS bằng cách lặp DFS với giới hạn độ sâu tăng dần.

#### Các cách tiếp cận

* **Cách 1:** Tăng tuyến tính giới hạn độ sâu sau mỗi vòng lặp.
* **Cách 2 (Early Goal Check):** Kiểm tra Goal-test ngay khi sinh nút con.

---

### UCS (Uniform Cost Search)

Mở rộng các nút dựa trên chi phí đường đi nhỏ nhất từ nút gốc:

$$
f(n) = g(n)
$$

Trong đó:

* $g(n)$ là chi phí thực tế từ nút gốc đến nút hiện tại.

Thuật toán sử dụng **Priority Queue** và đảm bảo tìm được đường đi tối ưu trên đồ thị có trọng số không âm.

---

## 2. Tìm kiếm có thông tin (Informed Search)

### Greedy Best-First Search

Lựa chọn phát triển nút có giá trị heuristic nhỏ nhất:

$$
f(n) = h(n)
$$

Trong đó:

* $h(n)$ là chi phí ước lượng từ nút hiện tại đến đích.

Thuật toán có tốc độ nhanh nhưng không đảm bảo tìm được đường đi tối ưu.

---

### A* Search

Thuật toán tìm kiếm tối ưu toàn cục dựa trên hàm đánh giá:

$$
f(n) = g(n) + h(n)
$$

Trong đó:

* $g(n)$ là chi phí thực tế từ nút gốc đến nút hiện tại.
* $h(n)$ là chi phí ước lượng từ nút hiện tại đến đích.

A* đảm bảo tính tối ưu và hoàn chỉnh nếu heuristic admissible.

---

### IDA* (Iterative Deepening A*)

Kết hợp giữa Iterative Deepening DFS và heuristic của A*.

#### Hàm đánh giá

$$
f(n) = g(n) + h(n)
$$

Trong đó:

* $g(n)$ là chi phí thực tế từ trạng thái ban đầu đến nút hiện tại.
* $h(n)$ là chi phí ước lượng từ nút hiện tại đến đích.

IDA* thực hiện tìm kiếm theo từng ngưỡng $f(n)$ tăng dần thay vì lưu toàn bộ frontier như A*, giúp tiết kiệm bộ nhớ đáng kể.

Thuật toán vẫn đảm bảo tính tối ưu nếu heuristic admissible, tuy nhiên có thể phải duyệt lại nhiều nút.

---

## 3. Tìm kiếm cục bộ (Local Search)

### Simple Hill Climbing

Thuật toán leo đồi cơ bản hoạt động bằng cách chọn trạng thái kế tiếp đầu tiên có heuristic tốt hơn trạng thái hiện tại.

#### Hàm heuristic

$$
f(n) = h(n)
$$

Trong đó:

* $h(n)$ biểu diễn mức độ "xấu" của trạng thái hiện tại.

Nếu không tồn tại trạng thái tốt hơn, thuật toán sẽ dừng lại.

#### Đặc điểm

* Đơn giản.
* Tốc độ nhanh.
* Dễ mắc kẹt tại:

  * Local Optimum
  * Plateau
  * Ridge

---

### Steepest Ascent Hill Climbing

Biến thể cải tiến của Hill Climbing.

Tại mỗi bước, thuật toán sẽ đánh giá toàn bộ các trạng thái lân cận và chọn trạng thái có heuristic tốt nhất.

#### Hàm heuristic

$$
f(n) = h(n)
$$

#### Đặc điểm

* Chất lượng kết quả tốt hơn Simple Hill Climbing.
* Chi phí tính toán cao hơn do phải duyệt toàn bộ neighbor.
* Không đảm bảo tìm được nghiệm tối ưu toàn cục.

---

### Stochastic Hill Climbing

Thuật toán lựa chọn ngẫu nhiên một trạng thái tốt hơn trong số các neighbor khả thi thay vì luôn chọn trạng thái tốt nhất.

#### Hàm heuristic

$$
f(n) = h(n)
$$

#### Đặc điểm

* Tăng khả năng thoát khỏi local optimum.
* Tạo sự đa dạng trong quá trình tìm kiếm.
* Kết quả có thể khác nhau giữa các lần chạy.

---

### Random-Restart Hill Climbing

Biến thể của Hill Climbing cho phép khởi động lại từ nhiều trạng thái ngẫu nhiên khác nhau khi thuật toán bị mắc kẹt.

#### Hàm heuristic

$$
f(n) = h(n)
$$

#### Đặc điểm

* Tăng xác suất tìm được nghiệm tốt.
* Hiệu quả trên không gian trạng thái lớn.
* Giảm ảnh hưởng của local optimum.

---

### Local Beam Search

Thuật toán tìm kiếm chùm cục bộ mở rộng từ Hill Climbing bằng cách duy trì và theo dõi đồng thời $k$ trạng thái thay vì chỉ một trạng thái duy nhất.

#### Hàm đánh giá

$$
f(n) = h(n)
$$

Trong đó:

* $h(n)$ biểu diễn chi phí ước lượng, ví dụ số lượng vết bụi còn lại trên cấu trúc lưới.

#### Nguyên lý hoạt động

1. Khởi tạo một tập hợp gồm $k$ trạng thái xuất phát ngẫu nhiên.
2. Tại mỗi bước lặp, sinh ra toàn bộ các trạng thái lân cận của tất cả $k$ trạng thái hiện tại.
3. Kiểm tra xem có trạng thái nào đạt mục tiêu hay chưa. Nếu có, kết thúc và trả về đường đi.
4. Nếu chưa đạt mục tiêu, sắp xếp toàn bộ các trạng thái lân cận theo thứ tự độ tốt tăng dần của hàm mục tiêu.
5. Chọn ra $k$ trạng thái tốt nhất để làm chùm mới cho bước tiếp theo.

#### Đặc điểm

* Hiệu quả hơn Hill Climbing thông thường nhờ chia sẻ thông tin giữa các luồng tìm kiếm song song.
* Tiết kiệm bộ nhớ hơn các thuật toán duyệt đồ thị toàn cục như A* hoặc BFS.
* Vẫn có khả năng bị kẹt vào tối ưu cục bộ nếu tất cả $k$ trạng thái cùng hội tụ về một vùng hẹp.

---

### Simulated Annealing

Thuật toán mô phỏng luyện kim kết hợp giữa tìm kiếm leo đồi và bước đi ngẫu nhiên dựa trên nguyên lý hạ nhiệt vật lý của kim loại nhằm tìm kiếm tối ưu toàn cục.

#### Hàm đánh giá và điều kiện dịch chuyển

$$
\Delta = h(\text{next state}) - h(\text{current state})
$$

* Nếu $\Delta < 0$, trạng thái kế tiếp tốt hơn nên thuật toán luôn chấp nhận dịch chuyển sang trạng thái mới.
* Nếu $\Delta \ge 0$, trạng thái kế tiếp tệ hơn nhưng thuật toán vẫn có thể chấp nhận với xác suất $p$:

$$
p = e^{-\frac{\Delta}{T}}
$$

Trong đó:

* $T$ là nhiệt độ hiện tại của hệ thống.
* $T$ giảm dần sau mỗi bước theo hệ số hạ nhiệt $\alpha$:

$$
T = \alpha \times T
$$

#### Đặc điểm

* Có khả năng thoát khỏi local optimum nhờ chấp nhận một số bước đi tệ hơn.
* Đường đi tìm kiếm có thể dài do tính ngẫu nhiên cao.
* Kết quả phụ thuộc vào nhiệt độ ban đầu $T_0$, ngưỡng dừng $T_{\min}$ và tốc độ giảm nhiệt $\alpha$.

---

## 4. Nhóm thuật toán tìm kiếm trong môi trường phức tạp

Trong các bài toán tìm kiếm cơ bản, tác nhân thường được giả định là biết rõ trạng thái hiện tại của môi trường và kết quả của từng hành động. Tuy nhiên, trong thực tế, môi trường có thể phức tạp hơn do tác nhân không quan sát được đầy đủ thông tin hoặc không chắc chắn về kết quả hành động.

Nhóm thuật toán tìm kiếm trong môi trường phức tạp được dùng để xử lý các trường hợp như:

* Môi trường không nhìn thấy.
* Môi trường chỉ nhìn thấy một phần.
* Môi trường không xác định kết quả hành động.
* Tác nhân phải lập kế hoạch dựa trên nhiều trạng thái có thể xảy ra.

---

### Tìm kiếm trong môi trường không nhìn thấy

Tìm kiếm trong môi trường không nhìn thấy là bài toán mà tác nhân không thể quan sát trực tiếp trạng thái hiện tại của môi trường. Tác nhân không biết chính xác mình đang ở đâu, nhưng vẫn có thể thực hiện hành động dựa trên tập các trạng thái có thể xảy ra.

Trong trường hợp này, thay vì lưu một trạng thái duy nhất, tác nhân cần duy trì một **Belief State**.

#### Belief State

**Belief State** là tập hợp tất cả các trạng thái mà tác nhân cho rằng mình có thể đang ở trong đó.

Ví dụ, nếu robot nằm trong một lưới 3x3 nhưng không có cảm biến, ban đầu robot có thể ở bất kỳ ô nào trong 9 ô. Khi đó:

$$
BeliefState = {s_1, s_2, s_3, ..., s_9}
$$

Mỗi hành động của robot sẽ làm thay đổi toàn bộ tập trạng thái khả dĩ này.

#### Belief Start

**Belief Start** là trạng thái niềm tin ban đầu của tác nhân.

Trong môi trường không nhìn thấy, tác nhân không biết chính xác vị trí ban đầu của mình, nên Belief Start thường là tập hợp nhiều trạng thái có thể xảy ra.

Ví dụ:

$$
BeliefStart = {(1,1), (1,2), (1,3), ..., (3,3)}
$$

Điều này có nghĩa là robot có thể đang ở bất kỳ vị trí nào trong lưới.

#### Belief Goal

**Belief Goal** là điều kiện mục tiêu được xác định trên Belief State.

Một kế hoạch được xem là thành công nếu sau khi thực hiện chuỗi hành động, tất cả các trạng thái có thể xảy ra đều thuộc nhóm trạng thái mục tiêu hoặc đều thỏa mãn điều kiện cần đạt.

Ví dụ, robot cần chắc chắn rằng dù ban đầu ở đâu thì sau chuỗi hành động, nó cũng đến được vị trí đích hoặc hoàn thành nhiệm vụ.

#### Đặc điểm

* Tác nhân không biết trạng thái hiện tại chính xác.
* Không sử dụng cảm biến để cập nhật trực tiếp vị trí.
* Phải suy luận dựa trên hành động đã thực hiện.
* Không gian tìm kiếm lớn hơn vì mỗi node là một tập trạng thái thay vì một trạng thái đơn.

---

### Tìm kiếm trong môi trường nhìn thấy một phần

Tìm kiếm trong môi trường nhìn thấy một phần là bài toán mà tác nhân có thể quan sát môi trường, nhưng thông tin quan sát được không đầy đủ.

Khác với môi trường không nhìn thấy hoàn toàn, trong môi trường nhìn thấy một phần, tác nhân vẫn có cảm biến hoặc dữ liệu quan sát, nhưng các thông tin đó chỉ phản ánh một phần trạng thái thật.

#### Belief State trong môi trường nhìn thấy một phần

Trong môi trường nhìn thấy một phần, Belief State vẫn được dùng để biểu diễn tập các trạng thái có thể xảy ra. Tuy nhiên, tập trạng thái này sẽ được cập nhật dựa trên hai yếu tố:

* Hành động mà tác nhân đã thực hiện.
* Thông tin quan sát được từ môi trường.

Ví dụ, robot chỉ có thể nhìn thấy các ô xung quanh nó nhưng không thấy toàn bộ bản đồ. Khi robot quan sát được có tường ở bên trái, các trạng thái không phù hợp với quan sát đó sẽ bị loại khỏi Belief State.

#### Belief Start based on Partial Environment

**Belief Start based on Partial Environment** là trạng thái niềm tin ban đầu được xây dựng dựa trên phần môi trường mà tác nhân có thể quan sát được.

Thay vì giả định tác nhân có thể ở mọi trạng thái, thuật toán sẽ loại bỏ những trạng thái không phù hợp với thông tin quan sát ban đầu.

Ví dụ:

* Nếu robot biết mình đang ở một ô không có tường bên phải.
* Những vị trí có tường bên phải sẽ bị loại khỏi Belief Start.
* Belief Start chỉ còn các vị trí phù hợp với quan sát ban đầu.

#### Belief Goal based on Partial Environment

**Belief Goal based on Partial Environment** là điều kiện mục tiêu được xác định dựa trên thông tin quan sát không đầy đủ.

Tác nhân không nhất thiết phải biết chính xác toàn bộ môi trường, nhưng cần đạt đến một trạng thái mà theo thông tin hiện có, mục tiêu được xem là thỏa mãn.

Ví dụ, robot cần tìm đến vùng sạch trong bản đồ, nhưng chỉ nhìn thấy một phần khu vực. Khi đó, mục tiêu có thể được xác định dựa trên vùng mà robot đã quan sát và xác nhận.

#### Đặc điểm

* Tác nhân có thông tin quan sát nhưng không đầy đủ.
* Belief State được cập nhật sau mỗi hành động và quan sát.
* Giúp tác nhân loại bỏ các trạng thái không còn phù hợp.
* Phù hợp với robot, hệ thống tự hành, trò chơi ẩn thông tin và môi trường có cảm biến giới hạn.

---

### Tìm kiếm trong môi trường không xác định

Tìm kiếm trong môi trường không xác định là bài toán mà tác nhân biết trạng thái hiện tại, nhưng không chắc chắn hành động sẽ tạo ra kết quả nào.

Một hành động có thể dẫn đến nhiều trạng thái khác nhau. Vì vậy, tác nhân cần xây dựng kế hoạch có khả năng xử lý nhiều tình huống xảy ra sau hành động.

#### Ví dụ

Một robot thực hiện hành động đi lên:

* Trong môi trường xác định, robot chắc chắn đi lên một ô.
* Trong môi trường không xác định, robot có thể đi lên thành công, bị trượt sang trái hoặc đứng yên do va chạm.

Vì vậy, thuật toán cần xét tất cả các kết quả có thể xảy ra của hành động.

---

### AND-OR Graph Search

AND-OR Graph Search là thuật toán dùng để lập kế hoạch trong môi trường không xác định.

Thuật toán biểu diễn bài toán bằng cây hoặc đồ thị gồm hai loại node chính:

* **OR node:** tác nhân được chọn một hành động trong nhiều hành động có thể.
* **AND node:** môi trường có thể tạo ra nhiều kết quả khác nhau từ một hành động, và kế hoạch phải xử lý được tất cả các kết quả đó.

#### Ý nghĩa của OR node

OR node biểu diễn trạng thái mà tác nhân có quyền lựa chọn hành động.

Ví dụ, tại một vị trí, robot có thể chọn:

* Đi lên.
* Đi xuống.
* Đi trái.
* Đi phải.

Tác nhân chỉ cần chọn một hành động tốt nhất trong các hành động này.

#### Ý nghĩa của AND node

AND node biểu diễn tình huống một hành động có thể sinh ra nhiều kết quả khác nhau.

Ví dụ, khi robot chọn hành động đi lên, kết quả có thể là:

* Robot đi lên thành công.
* Robot bị trượt sang trái.
* Robot đứng yên.

Kế hoạch chỉ được xem là hợp lệ nếu nó có thể xử lý tất cả các kết quả có thể xảy ra.

#### Nguyên lý hoạt động

1. Bắt đầu từ trạng thái ban đầu.
2. Nếu trạng thái hiện tại là goal, trả về kế hoạch rỗng.
3. Nếu là OR node, chọn một hành động có thể dẫn đến lời giải.
4. Nếu hành động sinh ra nhiều kết quả, tạo AND node.
5. Với mỗi kết quả có thể xảy ra, tiếp tục tìm kế hoạch con tương ứng.
6. Nếu tất cả các nhánh kết quả đều có lời giải, kế hoạch được xem là thành công.
7. Nếu có một nhánh không có lời giải, cần thử hành động khác.

#### Đặc điểm

* Phù hợp với môi trường không xác định.
* Tạo ra kế hoạch điều kiện thay vì một chuỗi hành động cố định.
* Có thể xử lý nhiều kết quả khác nhau của cùng một hành động.
* Chi phí tìm kiếm cao hơn do phải xét nhiều nhánh kết quả.

#### Ví dụ kế hoạch điều kiện

Thay vì tạo kế hoạch cố định như:

```text
Đi phải → Đi phải → Đi xuống
```

AND-OR Graph Search có thể tạo kế hoạch dạng:

```text
Thực hiện hành động A.
Nếu kết quả là trạng thái S1 thì làm kế hoạch P1.
Nếu kết quả là trạng thái S2 thì làm kế hoạch P2.
Nếu kết quả là trạng thái S3 thì làm kế hoạch P3.
```

Điều này giúp tác nhân thích nghi tốt hơn trong môi trường không chắc chắn.

---

### Tổng kết nhóm thuật toán

Nhóm thuật toán tìm kiếm trong môi trường phức tạp giúp tác nhân giải quyết các bài toán khó hơn so với môi trường tìm kiếm thông thường.

* Trong môi trường không nhìn thấy, tác nhân dùng Belief State để biểu diễn tập trạng thái có thể xảy ra.
* Trong môi trường nhìn thấy một phần, Belief State được cập nhật dựa trên hành động và quan sát.
* Trong môi trường không xác định, AND-OR Graph Search giúp xây dựng kế hoạch có thể xử lý nhiều kết quả khác nhau.

Nhóm thuật toán này đặc biệt quan trọng trong các hệ thống robot, tác nhân tự động, lập kế hoạch thông minh và các bài toán ra quyết định trong môi trường thiếu thông tin.

---

## 5. Nhóm thuật toán tìm kiếm trong môi trường có ràng buộc

Tìm kiếm trong môi trường có ràng buộc là nhóm bài toán mà trạng thái cần tìm phải thỏa mãn một tập các điều kiện nhất định. Các bài toán dạng này thường được mô hình hóa dưới dạng **Constraint Satisfaction Problem (CSP)**.

Một bài toán CSP thường gồm:

* **Biến (Variables):** các đối tượng cần gán giá trị.
* **Miền giá trị (Domains):** tập giá trị có thể gán cho từng biến.
* **Ràng buộc (Constraints):** điều kiện giữa các biến cần được thỏa mãn.

#### Ví dụ

Trong bài toán tô màu bản đồ:

* Mỗi tỉnh/thành là một biến.
* Mỗi màu là một giá trị trong domain.
* Hai vùng kề nhau không được có cùng màu là ràng buộc.

---

### Backtracking

Backtracking là thuật toán tìm kiếm theo chiều sâu dùng để giải các bài toán CSP bằng cách thử gán giá trị cho từng biến.

Nếu tại một bước gán, trạng thái hiện tại vi phạm ràng buộc, thuật toán sẽ quay lui để thử giá trị khác.

#### Nguyên lý hoạt động

1. Chọn một biến chưa được gán giá trị.
2. Thử lần lượt các giá trị trong domain của biến đó.
3. Kiểm tra xem việc gán giá trị có vi phạm ràng buộc hay không.
4. Nếu hợp lệ, tiếp tục gán cho biến kế tiếp.
5. Nếu không còn giá trị hợp lệ, quay lui về bước trước đó.

#### Đặc điểm

* Dễ cài đặt và dễ hiểu.
* Phù hợp với các bài toán có không gian trạng thái vừa phải.
* Có thể tốn nhiều thời gian nếu số lượng biến và domain lớn.
* Hiệu quả hơn khi kết hợp với các kỹ thuật chọn biến và kiểm tra ràng buộc.

---

### Forward Checking

Forward Checking là cải tiến của Backtracking. Sau mỗi lần gán giá trị cho một biến, thuật toán sẽ kiểm tra trước các biến chưa được gán và loại bỏ những giá trị không còn hợp lệ trong domain của chúng.

#### Nguyên lý hoạt động

1. Gán giá trị cho một biến.
2. Kiểm tra các biến có liên quan đến biến vừa gán.
3. Loại bỏ các giá trị trong domain của biến khác nếu chúng vi phạm ràng buộc.
4. Nếu domain của một biến nào đó bị rỗng, thuật toán quay lui ngay.
5. Nếu không có lỗi, tiếp tục tìm kiếm.

#### Đặc điểm

* Phát hiện sai sớm hơn Backtracking thông thường.
* Giảm số lượng nhánh cần duyệt.
* Tốn thêm chi phí để cập nhật domain sau mỗi bước gán.
* Phù hợp với các bài toán CSP như tô màu bản đồ, xếp lịch, phân công tài nguyên.

---

### AC-3

AC-3 là thuật toán dùng để duy trì tính nhất quán cung trong bài toán CSP.

Một cung $(X_i, X_j)$ được gọi là nhất quán nếu với mỗi giá trị của $X_i$, luôn tồn tại ít nhất một giá trị của $X_j$ sao cho ràng buộc giữa hai biến được thỏa mãn.

#### Nguyên lý hoạt động

1. Đưa tất cả các cung ràng buộc vào hàng đợi.
2. Lấy từng cung $(X_i, X_j)$ ra để kiểm tra.
3. Nếu có giá trị trong domain của $X_i$ không còn giá trị tương ứng hợp lệ trong domain của $X_j$, loại bỏ giá trị đó.
4. Nếu domain của $X_i$ bị thay đổi, đưa các cung liên quan trở lại hàng đợi.
5. Lặp lại cho đến khi hàng đợi rỗng hoặc phát hiện domain bị rỗng.

#### Đặc điểm

* Giúp thu hẹp domain trước hoặc trong quá trình tìm kiếm.
* Có thể phát hiện sớm trường hợp bài toán vô nghiệm.
* Không trực tiếp tìm nghiệm hoàn chỉnh, mà thường dùng để hỗ trợ Backtracking.
* Hiệu quả trong các bài toán có nhiều ràng buộc giữa các biến.

---

### Min-Conflicts

Min-Conflicts là thuật toán tìm kiếm cục bộ dùng cho bài toán CSP. Thuật toán bắt đầu từ một trạng thái đầy đủ, có thể chưa hợp lệ, sau đó liên tục sửa các biến đang gây xung đột.

#### Hàm đánh giá

$$
h(n) = \text{số lượng ràng buộc đang bị vi phạm}
$$

Mục tiêu là giảm giá trị $h(n)$ về 0.

#### Nguyên lý hoạt động

1. Khởi tạo một trạng thái ban đầu bằng cách gán giá trị cho tất cả các biến.
2. Kiểm tra các biến đang vi phạm ràng buộc.
3. Chọn một biến đang bị xung đột.
4. Gán lại giá trị cho biến đó sao cho số lượng xung đột là nhỏ nhất.
5. Lặp lại cho đến khi không còn xung đột hoặc đạt số bước giới hạn.

#### Đặc điểm

* Phù hợp với các bài toán CSP lớn.
* Tốc độ nhanh trong nhiều trường hợp thực tế.
* Không đảm bảo luôn tìm được nghiệm nếu bị kẹt trong trạng thái xấu.
* Kết quả có thể phụ thuộc vào trạng thái khởi tạo ban đầu.

---

## 6. Nhóm thuật toán tìm kiếm trong môi trường đối kháng

Tìm kiếm trong môi trường đối kháng là nhóm thuật toán thường được sử dụng trong các trò chơi có nhiều người chơi, đặc biệt là các trò chơi hai người có tính cạnh tranh.

Trong môi trường này, mỗi người chơi đều cố gắng chọn hành động tốt nhất cho mình, đồng thời làm giảm lợi thế của đối thủ.

#### Ví dụ

Các bài toán thường gặp:

* Tic-Tac-Toe
* Cờ caro
* Cờ vua
* Cờ tướng
* Các trò chơi chiến thuật theo lượt

Trong đó:

* **MAX** là người chơi cần tối đa hóa điểm số.
* **MIN** là đối thủ, cố gắng giảm điểm số của MAX.
* Trạng thái trò chơi được biểu diễn bằng cây tìm kiếm.
* Mỗi nước đi tạo ra một trạng thái con trong cây.

---

### Minimax

Minimax là thuật toán tìm kiếm đối kháng cơ bản dùng trong trò chơi hai người. Thuật toán giả định rằng cả hai người chơi đều chơi tối ưu.

MAX sẽ chọn nước đi có giá trị lớn nhất, còn MIN sẽ chọn nước đi có giá trị nhỏ nhất.

#### Hàm đánh giá

$$
Utility(s)
$$

Trong đó:

* $s$ là trạng thái trò chơi.
* $Utility(s)$ là điểm số đánh giá trạng thái đó.
* Trạng thái có lợi cho MAX sẽ có điểm cao.
* Trạng thái có lợi cho MIN sẽ có điểm thấp.

#### Nguyên lý hoạt động

1. Xây dựng cây trò chơi từ trạng thái hiện tại.
2. Duyệt các trạng thái con đến khi gặp trạng thái kết thúc hoặc đạt độ sâu giới hạn.
3. Tính điểm cho các trạng thái lá bằng hàm đánh giá.
4. Nếu là lượt MAX, chọn giá trị lớn nhất trong các trạng thái con.
5. Nếu là lượt MIN, chọn giá trị nhỏ nhất trong các trạng thái con.
6. Trả về nước đi tốt nhất cho người chơi hiện tại.

#### Đặc điểm

* Đảm bảo chọn nước đi tối ưu nếu duyệt hết cây trò chơi.
* Phù hợp với các trò chơi có số lượng trạng thái nhỏ như Tic-Tac-Toe.
* Tốn nhiều thời gian khi không gian trạng thái lớn.
* Thường cần giới hạn độ sâu và dùng heuristic trong các trò chơi phức tạp.

---

### Alpha-Beta Pruning

Alpha-Beta Pruning là phiên bản tối ưu của Minimax. Thuật toán giúp cắt bỏ những nhánh không cần xét mà vẫn giữ nguyên kết quả như Minimax.

#### Hai giá trị chính

* $\alpha$: giá trị tốt nhất hiện tại mà MAX có thể đảm bảo.
* $\beta$: giá trị tốt nhất hiện tại mà MIN có thể đảm bảo.

Nếu trong quá trình duyệt cây phát hiện:

$$
\alpha \ge \beta
$$

thì nhánh hiện tại có thể bị cắt bỏ vì nó không còn ảnh hưởng đến quyết định cuối cùng.

#### Nguyên lý hoạt động

1. Duyệt cây trò chơi giống Minimax.
2. Cập nhật $\alpha$ khi gặp lựa chọn tốt hơn cho MAX.
3. Cập nhật $\beta$ khi gặp lựa chọn tốt hơn cho MIN.
4. Nếu $\alpha \ge \beta$, dừng duyệt nhánh hiện tại.
5. Trả về nước đi tốt nhất giống như Minimax.

#### Đặc điểm

* Cho kết quả giống Minimax.
* Giảm đáng kể số lượng node cần duyệt.
* Hiệu quả phụ thuộc vào thứ tự xét nước đi.
* Phù hợp với các trò chơi có không gian trạng thái lớn như cờ caro, cờ vua hoặc cờ tướng.

---

### Expectimax

Expectimax là thuật toán mở rộng từ Minimax, dùng cho các môi trường có yếu tố ngẫu nhiên hoặc đối thủ không luôn chơi tối ưu.

Thay vì giả định đối thủ luôn chọn nước đi tốt nhất cho họ như Minimax, Expectimax tính giá trị kỳ vọng dựa trên xác suất xảy ra của các hành động.

#### Hàm đánh giá

$$
ExpectedValue(s) = \sum_i P(s_i) \times Utility(s_i)
$$

Trong đó:

* $s_i$ là trạng thái con có thể xảy ra.
* $P(s_i)$ là xác suất xảy ra trạng thái đó.
* $Utility(s_i)$ là điểm đánh giá của trạng thái đó.

#### Nguyên lý hoạt động

1. Xây dựng cây trò chơi từ trạng thái hiện tại.
2. Với node MAX, chọn giá trị lớn nhất trong các node con.
3. Với node Chance, tính trung bình có trọng số dựa trên xác suất.
4. Trả về hành động có giá trị kỳ vọng cao nhất.

#### Đặc điểm

* Phù hợp với môi trường có yếu tố may rủi.
* Không giả định đối thủ luôn chơi tối ưu.
* Có thể dùng trong các trò chơi có xúc xắc, bốc bài hoặc hành động ngẫu nhiên.
* Chi phí tính toán cao nếu số lượng trạng thái ngẫu nhiên lớn.

---

## Tổng kết

Repository này đóng vai trò như một bộ sưu tập thực hành các giải thuật AI cơ bản, giúp:

* Hiểu rõ nguyên lý hoạt động của từng thuật toán.
* So sánh ưu nhược điểm giữa các phương pháp tìm kiếm.
* Trực quan hóa quá trình tìm kiếm thông qua visualizer.
* Ứng dụng lý thuyết AI vào các bài toán thực tế.
