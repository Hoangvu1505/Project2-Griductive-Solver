# Project 2: Griductive Solver
### Môn học: Nhập môn Trí tuệ Nhân tạo (CSC14003) - Khoa CNTT, ĐHKHTN (VNU-HCM)

---

## 1. Giới Thiệu Đồ Án (Introduction)

**Griductive** là trò chơi suy luận lưới (grid-deduction game) trong đó mỗi nhân vật là **Criminal** (Tội phạm) hoặc **Innocent** (Vô tội). Các manh mối được lật mở luôn đúng sự thật, và người chơi phải xác định trạng thái của từng nhân vật **từng bước một bằng chứng minh logic**. 

Quy tắc cốt lõi: **TUYỆT ĐỐI KHÔNG ĐOÁN MÒ (NO GUESSING)**. Một phán quyết chỉ được hệ thống chấp nhận khi và chỉ khi nó được suy diễn kéo theo logic ($KB_t \models C_i$ hoặc $KB_t \models \neg C_i$) từ các thông tin công khai hiện tại.

> 📖 **Hướng dẫn chi tiết**: Xem luật chơi, ý nghĩa các loại manh mối và ví dụ một ván suy luận mẫu tại file [**`cachchoi.md`**](cachchoi.md).

Dự án này triển khai toàn diện:
1. **Mã hóa logic mệnh đề & CNF Encoder**: chuyển đổi tự động 6 dạng manh mối chuẩn (`FACT`, `SAME`, `DIFFERENT`, `EXACTLY`, `AT_LEAST`, `AT_MOST`) cùng các phần mở rộng (`PARITY`, `COMPARE`, vùng nâng cao `CORNERS`, `COMMON_NEIGHBORS`).
2. **Bộ giải SAT DPLL**: thuật toán Davis-Putnam-Logemann-Loveland hoàn chỉnh với lan truyền đơn vị (unit propagation), phát hiện xung đột (conflict detection), chọn biến xác định, đệ quy & quay lui, ghi nhận thống kê.
3. **Logic Agent suy diễn tự động**: phân loại `CRIMINAL`, `INNOCENT`, `UNKNOWN`, `INCONSISTENT`, nhật ký suy diễn `DeductionTrace`, kiểm tra nghiệm duy nhất (`Uniqueness Check`) và tính năng gợi ý `Hint`.
4. **Game Engine**: quản lý trạng thái bí mật, độc lập hoàn toàn với Logic Agent, kiểm duyệt phán quyết (`ACCEPTED`, `NOT_PROVABLE`, `CONTRADICTED`).
5. **Giao diện đồ họa (GUI)**: ứng dụng desktop trực quan, hỗ trợ chơi thủ công, highlight ô liên quan khi chọn clue, gợi ý và tự động giải.

---

## 2. Phân Công Công Việc & Cấu Trúc File (Task Distribution)

Cấu trúc file tuân thủ chính xác 100% theo bảng phân công công việc của nhóm:

| Thành viên | Nhiệm vụ chính | Chi tiết công việc | Danh sách File thực hiện |
| :--- | :--- | :--- | :--- |
| **Trưởng nhóm / TV A** | Logic Agent, tích hợp hệ thống & quản lý nhóm | Cài đặt agent phân loại entailment bằng $KB \land \neg C_i$ và $KB \land C_i$, vòng lặp suy diễn (deduction loop), deduction trace, kiểm tra uniqueness, Hint. Chốt interface chung giữa các module. Tạo repo Git, `README.md`, `requirements.txt`, `main.py`, `.gitignore`. | `agent/agent.py`<br>`agent/trace.py`<br>`agent/uniqueness.py`<br>`main.py`<br>`README.md`<br>`requirements.txt`<br>`.gitignore` |
| **Thành viên B** | Bộ giải SAT (DPLL) & Thực nghiệm | Cài đặt DPLL gồm unit propagation, conflict detection, chọn biến xác định, đệ quy và backtracking, hỗ trợ assumptions, thống kê decisions / propagations / backtracks / runtime. Viết unit test (kể cả ví dụ trang 4). Viết script benchmark trên puzzle 3x3, 4x4, 5x5, xuất CSV và biểu đồ. | `sat/dpll.py`<br>`tests/test_dpll.py`<br>`experiments/run_benchmarks.py` |
| **Thành viên C** | CNF Encoder | Ánh xạ biến $C_i$ xác định, validate clue, mã hoá 6 clue sang CNF bằng direct combinatorial encoding, cài 2 extension (PARITY, COMPARE, CORNERS), thêm unit clause cho verdict đã biết, hàm `build_kb(t)`, thống kê biến và clause. Test encoder so với evaluator bằng brute force $2^n$ assignment. | `logic/var_map.py`<br>`logic/encoder.py`<br>`logic/kb.py`<br>`tests/test_encoder.py` |
| **Thành viên D** | Game Engine, Clue model & Bộ puzzle | Dataclass `Clue` và `Region` (row, col, neighbors, explicit, corners), parser JSON, semantic evaluator cho 6 clue và extension, GameEngine (`submit_verdict` trả ACCEPTED / NOT_PROVABLE / CONTRADICTED, reveal), PublicState. Tạo bộ puzzle 3x3, 4x4, 5x5 và kiểm tra nghiệm duy nhất. | `engine/clue.py`<br>`engine/region.py`<br>`engine/evaluator.py`<br>`engine/game_engine.py`<br>`puzzles/*.json` |
| **Thành viên E** | GUI & Video demo | Dựng Modern GUI hiển thị lưới, toạ độ, tên và nghề, thẻ úp/lật chuẩn đồ họa gốc (Dark theme, procedural SVG avatars). Cho phép gọi CRIMINAL / INNOCENT, hiển thị NOT_PROVABLE / CONTRADICTED, chọn clue và highlight ô liên quan, các nút Load / Restart / Hint / Auto Solve, nối GUI với Engine và Agent qua Python API server. Kịch bản quay video demo 5-10 phút. | `web/` (React Modern GUI)<br>`gui/app.py`<br>`gui/web_server.py`<br>`demo_script.md` |

---

## 3. Cài Đặt & Môi Trường Chạy (Installation)

### 3.1. Yêu cầu hệ thống
* **Python**: Khuyến nghị Python 3.9 trở lên (đã kiểm thử tương thích hoàn hảo trên Python 3.11).
* **Matplotlib**: Dùng để vẽ biểu đồ trực quan hóa kết quả thực nghiệm benchmark.
* **Web Client**: Đã được biên dịch sẵn trong `web/dist`, chạy trực tiếp thông qua Python HTTP server mà không bắt buộc cài đặt Node.js hay npm.

### 3.2. Cài đặt thư viện
Mở terminal tại thư mục gốc của project và chạy lệnh:
```bash
pip install -r requirements.txt
```

---

## 4. Hướng Dẫn Sử Dụng (How to Run)

### 4.1. Khởi chạy Giao diện Đồ họa (GUI Mode)

Chỉ cần chạy lệnh sau từ thư mục gốc, hệ thống sẽ tự động khởi động máy chủ API tích hợp trong Python và mở giao diện người dùng trên trình duyệt:
```bash
python main.py
```
Hoặc:
```bash
python gui/app.py
```
Ứng dụng web hiển thị tại: `http://localhost:8000` với đồ họa chuẩn theo phiên bản gốc `knotwise.games/games/griductive`:
* Tông màu Dark Espresso thanh lịch, thẻ bo tròn sang trọng.
* 100% vector SVG procedural avatar với kiểu tóc (ngắn, dài, búi, xoăn, spiky, bob), màu tóc, màu da, áo và biểu cảm phong phú.
* Hoạt ảnh lật thẻ mượt mà, hiệu ứng spotlight hint và thanh công cụ tiện ích đầy đủ.

*Nếu muốn phát triển / chạy hot-reload React dev server:*
```bash
cd web
npm run dev
```

**Các thao tác trên GUI:**
* **Chơi thủ công:** Nhấp vào `+ Criminal` hoặc `- Innocent` trên các thẻ chưa lật. Hệ thống sẽ kiểm tra logic:
  * Nếu phán quyết được chứng minh: chấp nhận (`ACCEPTED`), lật thẻ hiển thị nhãn và manh mối mới.
  * Nếu đoán mò (chưa chứng minh được): cảnh báo `REJECTED [NOT_PROVABLE]` màu vàng-cam.
  * Nếu đoán ngược với suy luận: cảnh báo `REJECTED [CONTRADICTED]` màu đỏ.
* **Highlight manh mối:** Nhấp chuột vào bất kỳ manh mối nào trên thẻ đã mở. Các ô trên bàn cờ được manh mối này tham chiếu tới sẽ được viền vàng nổi bật.
* **Gợi ý (Hint):** Nhấn nút `Hint` để tìm ra ô tiếp theo bị ép buộc logic kèm manh mối gợi ý (không làm lộ đáp án ẩn).
* **Tự động giải:** 
  * `Auto Solve (Step)`: thực hiện đúng 1 bước suy luận tiếp theo.
  * `Auto Solve (All)`: tự động chạy vòng lặp suy diễn từng bước cho đến khi giải xong toàn bộ bàn cờ.
* **Kiểm tra nghiệm duy nhất:** Nhấn nút `Check Uniqueness` để xác minh câu đố chỉ có đúng 1 nghiệm.

---

### 4.2. Chạy Chế độ Dòng lệnh (CLI Mode)
Chạy trực tiếp thuật toán suy diễn trên terminal mà không cần mở GUI:
```bash
python main.py --cli --puzzle puzzles/puzzle_3x3_1.json
```
Lệnh sẽ in ra toàn bộ `Deduction Trace`: từng bước suy diễn, manh mối kích hoạt, các truy vấn SAT, phán quyết thu được và manh mối mới lộ diện.

---

### 4.3. Chạy Kiểm Thử Tự Động (Unit Tests)
Chạy bộ kiểm thử tự động toàn diện:
```bash
python main.py --test
```
* Kiểm tra bộ giải DPLL: unit propagation, conflict detection, branching, ví dụ trang 4 trong đề bài.
* Kiểm tra tương đương tuyệt đối: Brute-force $2^k$ trường hợp giữa **CNF Combinatorial Encoder** và **Direct Semantic Evaluator** cho tất cả các mẫu manh mối (`FACT`, `SAME`, `DIFFERENT`, `EXACTLY`, `AT_LEAST`, `AT_MOST`, `PARITY`, `COMPARE`).

---

### 4.4. Chạy Thực Nghiệm & Đánh Giá Hiệu Năng (Benchmarks)
Chạy đánh giá benchmark trên toàn bộ các bộ câu đố 3x3, 4x4, 5x5:
```bash
python main.py --benchmark
```
Kết quả sẽ:
1. In bảng tổng hợp 6 chỉ số ra màn hình.
2. Xuất dữ liệu bảng ra file `experiments/benchmark_results.csv`.
3. Tự động vẽ và lưu biểu đồ so sánh 4 thông số ra file `experiments/benchmark_plots.png`.

---

## 5. Kết Quả Thực Nghiệm (Benchmark Results)

Kết quả đo đạc thực tế trên bộ câu đố chuẩn:

| Câu đố | Lưới | Trạng thái | Biến SAT (Primary/Aux) | Mệnh đề CNF | Lần gọi SAT | Decisions / Propagations / Backtracks | Thời gian (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `puzzle_3x3_1.json` | 3x3 | SUCCESS | 9 / 0 | 28 | 16 | 0 / 102 / 0 | 2.55 ms |
| `puzzle_3x3_2.json` | 3x3 | SUCCESS | 9 / 0 | 36 | 14 | 0 / 84 / 0 | 2.48 ms |
| `puzzle_4x4_1.json` | 4x4 | SUCCESS | 16 / 0 | 76 | 76 | 0 / 746 / 0 | 13.01 ms |
| `puzzle_4x4_2.json` | 4x4 | SUCCESS | 16 / 0 | 77 | 42 | 0 / 418 / 0 | 12.99 ms |
| `puzzle_5x5_1.json` | 5x5 | SUCCESS | 25 / 0 | 146 | 64 | 1 / 998 / 0 | 50.66 ms |

*Biểu đồ trực quan hóa chi tiết được lưu trữ tại:* `experiments/benchmark_plots.png`.

---

## 6. Kịch Bản Demo Video (Demonstration Script)

Chi tiết kịch bản quay video mẫu 5 - 10 phút đáp ứng trọn vẹn tiêu chí mục 4.7 của đề bài (gồm thời lượng từng phân đoạn, thao tác cần quay, lời thoại tiếng Việt) được lưu tại:
👉 [`demo_script.md`](file:///demo_script.md)

