# Project 2: Griductive Solver
### Môn học: Nhập môn Trí tuệ Nhân tạo (CSC14003) - Khoa CNTT, ĐHKHTN (VNU-HCM)

---

## 1. Giới Thiệu Đồ Án (Introduction)

**Griductive** là trò chơi suy luận dạng lưới (grid-deduction game) trong đó mỗi nhân vật bí mật mang một trong hai trạng thái: **Criminal** (Tội phạm) hoặc **Innocent** (Vô tội). Các manh mối khi được lật mở luôn đúng sự thật, và người chơi cần xác định danh tính từng nhân vật **từng bước một bằng chứng minh logic hình thức**.

Quy tắc cốt lõi của trò chơi: **TUYỆT ĐỐI KHÔNG ĐOÁN MÒ (NO GUESSING)**. Một phán quyết chỉ được hệ thống chấp nhận khi và chỉ khi nó là hệ quả logic kéo theo từ cơ sở tri thức công khai hiện tại:
$$KB_t \models C_i \quad \text{hoặc} \quad KB_t \models \neg C_i$$

### Điểm nổi bật của đồ án:
1. **100% Pure Python**: Toàn bộ mô hình hóa logic mệnh đề, bộ giải SAT DPLL, cơ chế lan truyền đơn vị, quay lui, tác tử suy luận và công cụ kiểm chứng nghiệm duy nhất được lập trình từ đầu (from scratch) bằng Python thuần, **hoàn toàn không sử dụng thư viện SAT bên thứ ba** (không dùng PySAT, Z3, Minisat,...).
2. **Kiến trúc phân tầng chuyên nghiệp**: Phân định rõ ràng giữa Game Engine (quản trị luật chơi và che giấu đáp án bí mật), Logic Agent (chỉ đọc thông tin công khai), DPLL Solver và Giao diện người dùng.
3. **Bộ kiểm thử toàn diện**: 19/19 unit test tự động (bao gồm đối chiếu tương đương ngữ nghĩa $2^k$ giữa CNF Encoder và Evaluator, kiểm chứng ví dụ lý thuyết trang 4 của đề bài).
4. **Giao diện Web hiện đại**: Ứng dụng web React kết nối với máy chủ Python HTTP API, hỗ trợ đầy đủ các thao tác chơi thủ công, highlight manh mối trực quan, gợi ý spotlight (Hint), tự động giải (Auto Step, Auto Solve) và xem toàn bộ nhật ký chứng minh (Deduction Trace Drawer).

---

## 2. Bảng Phân Công Nhiệm Vụ (Team & Task Distribution)

| Thành viên | MSSV | Vai trò & Nhiệm vụ chính | Chi tiết công việc thực hiện | File thực hiện |
| :--- | :---: | :--- | :--- | :--- |
| **Lương Nguyễn Hoàng Vũ**<br>*(Trưởng nhóm)* | `24120493` | **Logic Agent & Quản trị dự án** | • Cài đặt tác tử logic phân loại kéo theo (entailment): kiểm tra $KB_t \land \neg C_i$ và $KB_t \land C_i$ trả về `CRIMINAL`, `INNOCENT`, `UNKNOWN`, `INCONSISTENT`.<br>• Vòng lặp suy luận từng bước (deduction loop), nhật ký suy luận (Deduction Trace).<br>• Kiểm tra tính nghiệm duy nhất (Uniqueness Check) và thuật toán gợi ý (Hint).<br>• Điểm khởi chạy trung tâm `main.py`, quản lý Git, hoàn thiện tài liệu `README.md`. | `agent/agent.py`<br>`agent/trace.py`<br>`agent/uniqueness.py`<br>`main.py`<br>`README.md`<br>`requirements.txt`<br>`.gitignore` |
| **Trần Minh Tiến** | `24120465` | **Bộ giải SAT (DPLL) & Thực nghiệm** | • Cài đặt thuật toán giải SAT DPLL: lan truyền đơn vị (unit propagation), phát hiện mâu thuẫn (conflict detection), chọn biến rẽ nhánh xác định, đệ quy và quay lui (backtracking).<br>• Hỗ trợ gán giả định (Assumptions) phục vụ truy vấn entailment.<br>• Thu thập thống kê thực nghiệm (decisions, propagations, backtracks, runtime).<br>• Viết unit test DPLL (kể cả ví dụ trang 4) và script benchmark trên bộ câu đố. | `sat/dpll.py`<br>`tests/test_dpll.py`<br>`experiments/run_benchmarks.py`<br>`experiments/benchmark_results.csv`<br>`experiments/benchmark_plots.png` |
| **Huỳnh Chí Thoại** | `24120457` | **CNF Encoder** | • Ánh xạ biến xác định row-major ($C_i$) và cấp phát biến phụ trợ ($Aux$).<br>• Mã hóa trực tiếp 6 dạng manh mối chuẩn (`FACT`, `SAME`, `DIFFERENT`, `EXACTLY`, `AT_LEAST`, `AT_MOST`) và 2 dạng mở rộng (`PARITY`, `COMPARE`).<br>• Bổ sung unit clause cho phán quyết đã biết, hàm xây dựng $KB_t$.<br>• Viết unit test đối chiếu tương đương tuyệt đối $2^k$ giữa Encoder và Evaluator. | `logic/var_map.py`<br>`logic/encoder.py`<br>`logic/kb.py`<br>`tests/test_encoder.py` |
| **Đỗ Trung Kiên** | `24120350` | **Game Engine & Thiết kế Puzzle** | • Cấu trúc dữ liệu `Clue`, `Region` (row, col, neighbors, explicit, corners), bộ đọc JSON.<br>• Bộ đánh giá ngữ nghĩa độc lập (Semantic Evaluator).<br>• GameEngine quản lý bí mật, giao thức lật thẻ và phản hồi phán quyết (`ACCEPTED`, `NOT_PROVABLE`, `CONTRADICTED`).<br>• Thiết kế và thẩm định bộ câu đố 3×3, 4×4, 5×5 đảm bảo 100% nghiệm duy nhất và giải được từng bước bằng logic. | `engine/clue.py`<br>`engine/region.py`<br>`engine/evaluator.py`<br>`engine/game_engine.py`<br>`puzzles/*.json` |
| **Lê Phạm Đăng Khiêm** | `24120341` | **Giao diện Web (GUI)** | • Xây dựng Modern Web GUI bằng React + Tailwind CSS với hệ thống procedural avatar vector SVG (đa dạng kiểu tóc, màu da, trang phục).<br>• Main Menu chọn màn chơi, xem luật chơi và thông tin thành viên nhóm.<br>• Tương tác bàn cờ: gọi Criminal/Innocent, highlight ô liên quan khi chọn clue, các nút tiện ích (Restart, Hint, Auto Step, Auto Solve, Uniqueness, Trace Drawer).<br>• Kết nối giao diện với Engine và Agent qua Python HTTP API Server (`gui/web_server.py`). | `gui/web_server.py`<br>`gui/app.py`<br>`web/` *(toàn bộ mã nguồn & bản build React)* |

---

## 3. Cấu Trúc Thư Mục Dự Án (Project Structure)

```text
Project2/
├── agent/                      # Tác tử suy luận logic
│   ├── agent.py                # LogicAgent: phân loại entailment, deduction loop, Hint
│   ├── trace.py                # DeductionTrace & cấu trúc lưu vết chứng minh
│   └── uniqueness.py           # Kiểm tra tính nghiệm duy nhất (DPLL blocking clause + brute-force)
├── engine/                     # Game Engine & mô hình trò chơi
│   ├── clue.py                 # Dataclass Clue và chuyển đổi hiển thị
│   ├── region.py               # Định nghĩa các vùng: ROW, COL, NEIGHBORS, EXPLICIT, CORNERS
│   ├── evaluator.py            # Direct Semantic Evaluator (đánh giá chân trị không qua CNF)
│   └── game_engine.py          # Quản trị luật chơi, cô lập secret truth, kiểm duyệt phán quyết
├── experiments/                # Thực nghiệm & Benchmark
│   ├── run_benchmarks.py       # Script chạy thực nghiệm tự động trên toàn bộ câu đố
│   ├── benchmark_results.csv   # Dữ liệu đo đạc 6 chỉ số lưu dạng CSV
│   └── benchmark_plots.png     # Biểu đồ trực quan hóa 4 thông số hiệu năng
├── gui/                        # Tầng kết nối Giao diện
│   ├── app.py                  # Điểm khởi chạy GUI tiện lợi
│   └── web_server.py           # Python HTTP API Server phục vụ Web GUI và REST API
├── logic/                      # Biểu diễn Logic mệnh đề & CNF Encoder
│   ├── var_map.py              # Ánh xạ xác định tọa độ (r, c) <-> Biến SAT 1..N^2
│   ├── encoder.py              # Thuật toán chuyển đổi 8 dạng manh mối sang CNF
│   └── kb.py                   # Quản lý cơ sở tri thức tăng dần KB_t
├── puzzles/                    # Bộ câu đố chuẩn hóa (3x3, 4x4, 5x5)
│   ├── puzzle_3x3_1.json       # Lưới 3x3 - Mức độ cơ bản
│   ├── puzzle_3x3_2.json       # Lưới 3x3 - Manh mối Parity / So sánh
│   ├── puzzle_4x4_1.json       # Lưới 4x4 - Tiêu chuẩn Knotwise
│   ├── puzzle_4x4_2.json       # Lưới 4x4 - Ràng buộc Exact row/col
│   ├── puzzle_4x4_3.json       # Lưới 4x4 - Suy luận láng giềng chuỗi
│   └── puzzle_5x5_1.json       # Lưới 5x5 - Thử thách mở rộng (Stress test)
├── sat/                        # Bộ giải SAT từ đầu
│   ├── solver_interface.py     # Interface trừu tượng cho SAT Solver
│   └── dpll.py                 # Thuật toán DPLL thuần túy (Unit Prop, Backtracking, Assumptions)
├── tests/                      # Bộ kiểm thử tự động
│   ├── test_dpll.py            # Unit test thuật toán DPLL & ví dụ Mục 3.4 đề bài
│   └── test_encoder.py         # Kiểm thử đối chiếu vét cạn 2^k giữa Encoder và Evaluator
├── web/                        # Mã nguồn ứng dụng Web GUI (React, Tailwind CSS, Vite)
│   ├── dist/                   # Bản build đóng gói sẵn (chạy ngay mà không cần cài Node.js)
│   └── src/                    # Mã nguồn React components & avatars
├── main.py                     # Entry point trung tâm của toàn bộ dự án
├── requirements.txt            # Danh sách thư viện phụ trợ (matplotlib)
├── .gitignore                  # Cấu hình Git sạch sẽ
└── README.md                   # Báo cáo tổng quan dự án
```

---

## 4. Cơ Sở Lý Thuyết & Thuật Toán (Theoretical Formulation)

### 4.1. Biến mệnh đề (Propositional Variables)
Với mỗi nhân vật tại tọa độ ô $(r, c)$ trên lưới $N \times N$, hệ thống định nghĩa một biến mệnh đề logic cơ bản:
$$C_i = \begin{cases} \text{True} & \text{nếu nhân vật } i \text{ là Criminal (Tội phạm)} \\ \text{False} & \text{nếu nhân vật } i \text{ là Innocent (Vô tội)} \end{cases}$$
Hàm ánh xạ song ánh xác định: $\text{var}(r, c) = r \cdot N + c + 1 \in [1, N^2]$. Các biến phụ trợ ($Aux$) nếu phát sinh sẽ được đánh số từ $N^2 + 1$ trở đi và tách biệt hoàn toàn.

### 4.2. Ngữ nghĩa Manh Mối & Mã hóa CNF (Clue Semantics & CNF Encoding)
Hệ thống hỗ trợ 6 dạng manh mối bắt buộc cùng các phần mở rộng:
1. **FACT**: $C_i$ (nếu là Criminal) hoặc $\neg C_i$ (nếu là Innocent) $\implies$ Đưa trực tiếp thành unit clause $[C_i]$ hoặc $[-C_i]$.
2. **SAME**: $C_i \leftrightarrow C_j \implies (\neg C_i \lor C_j) \land (C_i \lor \neg C_j) \implies [-C_i, C_j], [C_i, -C_j]$.
3. **DIFFERENT**: $C_i \oplus C_j \implies (C_i \lor C_j) \land (\neg C_i \lor \neg C_j) \implies [C_i, C_j], [-C_i, -C_j]$.
4. **EXACTLY $k$**: Tổng số tội phạm trong vùng $R$ bằng đúng $k$. Mã hóa kết hợp: $\text{AtLeast}(R, k) \land \text{AtMost}(R, k)$.
5. **AT\_LEAST $k$**: Trong mọi tập con gồm $|R| - k + 1$ phần tử của $R$, phải có ít nhất 1 tội phạm:
   $$\bigwedge_{S \subseteq R, |S| = |R| - k + 1} \left( \bigvee_{v \in S} v \right)$$
6. **AT\_MOST $k$**: Trong mọi tập con gồm $k + 1$ phần tử của $R$, không thể tất cả đều là tội phạm:
   $$\bigwedge_{S \subseteq R, |S| = k + 1} \left( \bigvee_{v \in S} \neg v \right)$$
7. **PARITY (Mở rộng)**: Tính chẵn/lẻ số lượng tội phạm trong vùng.
8. **COMPARE (Mở rộng)**: So sánh số tội phạm giữa hai vùng $R_1$ và $R_2$ ($>$, $<$, $=$).

### 4.3. Xây dựng Cơ sở Tri thức ($KB_t$)
Tại bước suy luận $t$, tri thức công khai bao gồm các manh mối đã lộ và các phán quyết đã chứng minh:
$$KB_t = \left( \bigwedge_{\text{clue} \in \text{RevealedClues}_t} \text{CNF}(\text{clue}) \right) \land \left( \bigwedge_{(c, \text{status}) \in \text{ProvedVerdicts}_t} \text{UnitClause}(c, \text{status}) \right)$$
*Nguyên tắc bất khả xâm phạm: $KB_t$ tuyệt đối không chứa manh mối của các ô đang úp hay đáp án ngầm của Game Engine.*

### 4.4. Kiểm tra Kéo theo Ngữ nghĩa (Entailment via SAT)
Để phân loại một ô chưa giải $C_i$ mà không đoán mò:
* **Chứng minh $C_i$ là Criminal**: Kiểm tra $KB_t \models C_i \iff KB_t \land \neg C_i \text{ là UNSAT}$.
* **Chứng minh $C_i$ là Innocent**: Kiểm tra $KB_t \models \neg C_i \iff KB_t \land C_i \text{ là UNSAT}$.
* **Trường hợp Unknown**: Nếu cả $KB_t \land \neg C_i$ và $KB_t \land C_i$ đều SAT $\implies$ Chưa đủ thông tin chứng minh, tuyệt đối không đoán.
* **Trường hợp Inconsistent**: Nếu cả hai đều UNSAT $\implies$ Cơ sở tri thức mâu thuẫn.

---

## 5. Hướng Dẫn Cài Đặt & Sử Dụng (How to Run)

### 5.1. Yêu cầu môi trường
* **Python**: Khuyến nghị Python 3.9 trở lên (đã kiểm thử ổn định 100% trên Python 3.10 và 3.11).
* **Cài đặt thư viện phụ trợ**:
  ```bash
  pip install -r requirements.txt
  ```
  *(Lưu ý: `matplotlib` là thư viện duy nhất dùng để vẽ biểu đồ benchmark; toàn bộ logic và GUI đều chạy bằng thư viện chuẩn của Python).*

---

### 5.2. Chế độ Giao diện Đồ họa (Web GUI Mode)

Chỉ cần gõ lệnh sau từ thư mục gốc của đồ án, hệ thống sẽ tự động khởi động server tích hợp và mở trình duyệt:
```bash
python main.py
```
Hoặc:
```bash
python gui/app.py
```

* Ứng dụng web hiển thị tại địa chỉ: `http://localhost:8000`.
* **Bản phân phối web đã được biên dịch sẵn** trong thư mục `web/dist/`, cho phép người dùng khởi chạy lập tức mà **không cần cài đặt Node.js hay chạy npm**.

**Các thao tác chính trên GUI:**
1. **Khám phá vụ án**: Tại Main Menu, chọn 1 trong các màn chơi câu đố (3×3, 4×4, 5×5) và bấm *Investigate Case*.
2. **Chơi thủ công**: Nhấp vào thẻ nhân vật đang úp, chọn `Call CRIMINAL` hoặc `Call INNOCENT`.
   * Nếu được chứng minh: Nhận nhãn `ACCEPTED`, thẻ lật ra hiển thị manh mối mới.
   * Nếu đoán mò: Cảnh báo `REJECTED [NOT_PROVABLE]`.
   * Nếu đoán ngược suy luận: Cảnh báo `REJECTED [CONTRADICTED]`.
3. **Highlight manh mối**: Nhấp chuột vào bất kỳ manh mối nào trên thẻ đã mở, các ô mà manh mối đó tham chiếu tới sẽ được viền vàng nổi bật.
4. **Gợi ý (Hint)**: Bấm `Hint` để tìm ra ô tiếp theo bị ép buộc logic kèm manh mối công khai liên quan (không làm lộ đáp án ẩn).
5. **Tự động giải (Auto Solve)**:
   * `Auto Step (Logic Agent)`: Chạy đúng 1 bước suy luận kế tiếp.
   * `Auto Solve (All)`: Tự động chạy toàn bộ chuỗi suy luận cho đến khi giải xong toàn bộ bàn cờ.
6. **Kiểm tra nghiệm duy nhất (Unique)**: Bấm `Unique` để DPLL kiểm tra xem câu đố có đúng 1 mô hình thỏa mãn duy nhất hay không.
7. **Xem nhật ký suy luận (Trace)**: Bấm nút `Trace` góc trên bên phải để xem toàn bộ lịch sử các bước chứng minh kèm truy vấn SAT.

---

### 5.3. Chế độ Dòng lệnh (CLI Mode)

Chạy bộ giải trực tiếp trên terminal với output dạng văn bản chi tiết:
```bash
python main.py --cli --puzzle puzzles/puzzle_3x3_1.json
```
Output sẽ in rõ ràng: kết quả kiểm tra nghiệm duy nhất, từng bước suy diễn, các truy vấn SAT, thời gian chạy và phán quyết tương ứng.

---

### 5.4. Chạy Bộ Kiểm Thử Tự Động (Unit Tests)

Thực thi bộ 19 unit test tự động:
```bash
python main.py --test
```
* Kiểm tra đầy đủ các thành phần DPLL: Lan truyền đơn vị theo chuỗi, phát hiện xung đột, phân nhánh, quay lui, và **bài toán mẫu trang 4 của đề bài**.
* Kiểm tra đối chiếu tương đương ngữ nghĩa $2^k$ giữa CNF Encoder và Semantic Evaluator cho toàn bộ các dạng manh mối và các vùng nâng cao (`CORNERS`, `COMMON_NEIGHBORS`, `BETWEEN`).

---

### 5.5. Chạy Đánh Giá Hiệu Năng (Benchmarks)

Thực hiện đo đạc thực nghiệm tự động trên toàn bộ các câu đố chuẩn:
```bash
python main.py --benchmark
```
Lệnh sẽ tự động:
1. In bảng tổng hợp chi tiết 6 chỉ số ra màn hình console.
2. Xuất dữ liệu ra file bảng tính [`experiments/benchmark_results.csv`](experiments/benchmark_results.csv).
3. Vẽ và lưu đồ thị so sánh hiệu năng trực quan ra file [`experiments/benchmark_plots.png`](experiments/benchmark_plots.png).

---

## 6. Kết Quả Thực Nghiệm (Benchmark Results)

Kết quả đo đạc thực tế trên hệ thống bộ câu đố (được nâng độ khó, xuất hiện cả phân nhánh và quay lui để kiểm chứng toàn diện bộ giải DPLL):

| Câu đố (Puzzle) | Kích thước | Trạng thái | Biến SAT ($P+A$) | Số Mệnh đề CNF | Số lần gọi SAT | Decisions / Props / Backtracks | Thời gian (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `puzzle_3x3_1.json` | 3×3 | **SUCCESS** | 9 + 0 | 32 | 30 | 0 / 220 / 0 | **5.77 ms** |
| `puzzle_3x3_2.json` | 3×3 | **SUCCESS** | 9 + 0 | 33 | 34 | 1 / 166 / 0 | **3.41 ms** |
| `puzzle_4x4_1.json` | 4×4 | **SUCCESS** | 16 + 0 | 76 | 124 | 130 / 993 / 0 | **23.40 ms** |
| `puzzle_4x4_2.json` | 4×4 | **SUCCESS** | 16 + 0 | 93 | 132 | 216 / 1276 / 90 | **38.67 ms** |
| `puzzle_4x4_3.json` | 4×4 | **SUCCESS** | 16 + 0 | 94 | 148 | 185 / 1256 / 6 | **40.00 ms** |
| `puzzle_5x5_1.json` | 5×5 | **SUCCESS** | 25 + 0 | 160 | 256 | 2379 / 3216 / 74 | **187.68 ms** |

### Nhận xét & Đánh giá:
* **Tỷ lệ giải thành công**: **100% (6/6 câu đố)** đạt trạng thái `SUCCESS`, không có trường hợp nào bị timeout hay thất bại.
* **Thời gian thực thi**: Bộ giải DPLL viết bằng Python thuần đạt tốc độ ấn tượng: giải quyết lưới 3×3 dưới **6 ms**, lưới 4×4 dưới **40 ms**, và lưới 5×5 phức tạp (25 biến, 160 clause) chỉ mất khoảng **187 ms**.
* **Khả năng quay lui (Backtracking)**: Tại các câu đố nâng cao như `puzzle_4x4_2.json` (90 backtracks) và `puzzle_5x5_1.json` (74 backtracks), bộ giải thể hiện chính xác khả năng dò tìm không gian trạng thái, phát hiện xung đột và quay lui để tìm ra nghiệm duy nhất một cách hoàn hảo.

---
*Dự án hoàn thành phục vụ môn học Nhập môn Trí tuệ Nhân tạo (CSC14003) - Khoa Công nghệ Thông tin, Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM.*
