# Kịch Bản Video Báo Cáo & Demo Đồ Án (5 - 10 Phút)
## Project 2: Griductive Solver - Introduction to Artificial Intelligence (CSC14003)

---

### I. Tổng Quan Yêu Cầu Video (Mục 4.7)
* **Thời lượng:** Từ 5 đến 10 phút.
* **Hình thức nộp:** Tải video lên Google Drive và bật quyền truy cập công khai ("Anyone with the link can view").
* **Kiểm tra quyền:** Mở đường link trên cửa sổ ẩn danh (Incognito/Private window) để chắc chắn người xem không cần đăng nhập vẫn xem được.
* **Lưu ý quan trọng:** **KHÔNG** nộp link YouTube (vi phạm yêu cầu đề bài).
* **Nội dung cần trình bày:**
  1. Giao diện đồ họa (Graphical Interface - 5 điểm)
  2. Trình diễn tính năng (Feature Presentation - 5 điểm):
     - Chơi thủ công (Manual play), xử lý đoán mò / sai luật (NOT_PROVABLE, CONTRADICTED).
     - Chạy thuật toán tự động giải (Auto Solve), tính năng Hint, và kiểm tra tính duy nhất (Uniqueness Check).
     - Chạy thực nghiệm benchmark trên các kích thước 3x3, 4x4, 5x5.

---

### II. Timeline Chi Tiết & Lời Thoại (Kịch Bản Mẫu)

#### [0:00 - 1:00] Phần 1: Giới thiệu nhóm và Đề tài
* **Thao tác màn hình:**
  * Mở Slide đầu hoặc cửa sổ code/giao diện game với tiêu đề:
    `Project 2: Griductive Solver - HCMUS`
  * Hiện danh sách thành viên và phân công công việc (khớp với bảng phân công).
* **Lời thoại mẫu:**
  > "Kính chào Thầy và các bạn trợ giảng. Chúng em là nhóm ..., hôm nay nhóm xin phép trình bày và demo sản phẩm Project 2 môn Nhập môn Trí tuệ Nhân tạo: Griductive Solver.
  >
  > Bài toán yêu cầu xây dựng một hệ thống suy diễn logic mệnh đề và bộ giải SAT DPLL cho trò chơi suy luận lưới Griductive. Mục tiêu cốt lõi là KHÔNG ĐOÁN MÒ (No Guessing): một phán quyết Criminal hay Innocent chỉ được chấp nhận khi nó được suy diễn kéo theo logic từ các manh mối công khai hiện tại.
  >
  > Sau đây, nhóm xin bắt đầu phần demo trực tiếp chương trình."

---

#### [1:00 - 3:00] Phần 2: Giới thiệu Kiến trúc & Giao diện Đồ họa (GUI)
* **Thao tác màn hình:**
  * Chạy lệnh `python main.py` trên terminal.
  * Cửa sổ trình duyệt tự động mở ra với Modern GUI tông màu Dark Espresso chuẩn trò chơi gốc `knotwise.games/games/griductive`.
  * Chỉ trỏ các thành phần:
    - Lưới bài $N \times N$, tọa độ cột (A, B, C...) và hàng (1, 2, 3...).
    - Nhân vật đồ họa vector SVG đa dạng kiểu tóc (dài, ngắn, búi, xoăn), màu tóc, màu da và biểu cảm.
    - Thẻ nhân vật: hiển thị tọa độ, tên, nghề nghiệp.
    - Thẻ úp (Face-down) cho phép nhấp chọn `Criminal` hoặc `Innocent`.
    - Thẻ mở (Face-up) hiển thị mini avatar, nhãn trạng thái và nội dung manh mối logic.
    - Thanh điều khiển trên cùng: chọn màn chơi, Restart, Hint, Auto Solve (Step/All), Check Uniqueness.
    - Cột bên phải: Thống kê trạng thái KB (số biến mệnh đề primary/aux, số mệnh đề CNF) và nhật ký suy diễn (Deduction Trace Drawer).
    - Banner phản hồi: hiển thị kết quả phán quyết hoặc thông báo từ chối.
* **Lời thoại mẫu:**
  > "Giao diện được xây dựng hiện đại với thiết kế Dark Espresso chuẩn trò chơi gốc, kết nối trực tiếp với backend Python HTTP server. Kiến trúc tách biệt hoàn toàn giữa Game Engine (sở hữu lời giải ẩn) và Logic Agent (chỉ nhận Public State gồm các thẻ và manh mối đã lật).
  >
  > Mọi nhân vật đều được render bằng SVG vector thuần với 12 kiểu tóc và 10 màu tóc, bảo đảm tính đa dạng và sắc nét tối đa."
  > Trên bàn chơi, ta có các tọa độ hàng và cột rõ ràng. Ban đầu, có một số thẻ được lật công khai để bắt đầu chuỗi suy luận. Các thẻ còn lại đều úp và tuyệt đối không làm lộ trạng thái bí mật."

---

#### [3:00 - 5:30] Phần 3: Trình diễn Chơi Thủ Công & Luật Phản Hồi (Rejection Handling)
* **Thao tác màn hình:**
  1. **Thử đoán mò một ô chưa có chứng minh:**
     - Bấm chọn một ô ở góc xa (ví dụ ô `C3` khi mới bắt đầu). Bấm nút `+ Criminal` hoặc `- Innocent`.
     - Banner lập tức chuyển màu cam cảnh báo: `REJECTED [NOT_PROVABLE]`. Thẻ vẫn giữ nguyên trạng thái úp.
  2. **Thử đưa ra phán quyết ngược với logic suy ra:**
     - Nếu một ô theo logic phải là Innocent, nhưng người chơi bấm chọn `+ Criminal`.
     - Banner lập tức chuyển màu đỏ: `REJECTED [CONTRADICTED]`.
  3. **Thực hiện phán quyết đúng theo logic:**
     - Nhìn vào manh mối ban đầu (ví dụ: `B1: Row 1 contains exactly 2 criminals` và B1 là Innocent $\implies$ A1 và C1 phải là Criminal).
     - Bấm chọn `+ Criminal` tại ô A1.
     - Phán quyết được **ACCEPTED**: ô A1 lập tức đổi màu đỏ `CRIMINAL`, lật thẻ và hiển thị manh mối mới của A1!
     - Trace log bên phải tự động ghi nhận bước suy diễn.
  4. **Tương tác chọn manh mối để highlight:**
     - Bấm chuột vào manh mối trên thẻ A1.
     - Lưới tự động đổi màu viền vàng (highlight) các ô mà manh mối này tham chiếu tới. Bấm lần nữa để tắt highlight.
  5. **Tính năng Hint (Gợi ý):**
     - Bấm nút `Hint`.
     - Logic Agent chạy thuật toán entailment trên $KB_t$ hiện tại, tìm ra ô tiếp theo bị ép buộc logic, viền ô đó màu xanh Cyan và thông báo rõ tên nhân vật, trạng thái kèm theo các manh mối liên quan.
* **Lời thoại mẫu:**
  > "Đây là tính năng cốt lõi theo chuẩn đề bài: Khi người chơi đoán mò một ô chưa có căn cứ, hệ thống báo NOT_PROVABLE và từ chối. Khi người chơi đoán ngược với logic bị ép buộc, hệ thống báo CONTRADICTED.
  >
  > Chỉ khi phán quyết hoàn toàn kéo theo từ KB hiện tại, hệ thống mới chấp nhận (ACCEPTED), lật thẻ và mở ra manh mối tiếp theo.
  >
  > Ngoài ra, người chơi có thể bấm vào bất kỳ manh mối nào để làm sáng các ô liên quan, hoặc bấm nút 'Hint' để nhận gợi ý ô có thể chứng minh tiếp theo mà không làm lộ trước đáp án ẩn."

---

#### [5:30 - 7:30] Phần 4: Bộ Giải Tự Động (Auto Solve) & Kiểm Tra Nghiệm Duy Nhất
* **Thao tác màn hình:**
  1. Bấm `Restart` để về trạng thái ban đầu.
  2. Bấm `Auto Solve (Step)`: quan sát 1 bước suy diễn diễn ra, 1 ô được chứng minh và lật mở.
  3. Bấm `Auto Solve (All)`: vòng lặp suy diễn tự động chạy với hiệu ứng chuyển tiếp mượt mà. Từng thẻ lần lượt được suy diễn và lật mở cho đến khi hoàn thành 100% bàn cờ mà không cần đoán mò.
  4. Bấm `Check Uniqueness`: hiển thị pop-up xác nhận bộ manh mối hoàn chỉnh có đúng 1 nghiệm duy nhất (UNSAT khi thêm blocking clause).
  5. Đổi sang màn chơi kích thước lớn hơn: `puzzle_4x4_1.json` và `puzzle_5x5_1.json`. Bấm `Auto Solve (All)` để thể hiện thuật toán mở rộng hoàn hảo trên lưới 4x4 và 5x5 stress-test.
* **Lời thoại mẫu:**
  > "Tiếp theo là chế độ Tự động giải (Auto Solve). Logic Agent sử dụng thuật toán DPLL kiểm tra xem $KB_t \land \neg C_i$ có UNSAT hay không. Nếu UNSAT, $C_i$ chắc chắn là Criminal. Ngược lại nếu $KB_t \land C_i$ là UNSAT thì $C_i$ là Innocent.
  >
  > Đại lý chọn các ô bị ép buộc theo thứ tự xác định (row-major order) và lặp lại cho đến khi giải trọn vẹn toàn bộ câu đố.
  >
  > Nút 'Check Uniqueness' cho phép kiểm tra tính duy nhất của toàn bộ câu đố bằng cách tìm nghiệm đầu tiên, tạo mệnh đề chặn (blocking clause) và giải lại để chứng minh không tồn tại nghiệm thứ hai."

---

#### [7:30 - 9:00] Phần 5: Chạy Unit Test & Đánh Giá Thực Nghiệm (Benchmarks)
* **Thao tác màn hình:**
  * Thu nhỏ GUI, mở terminal:
  * Chạy unit tests: `python main.py --test`
    - Toàn bộ 15 test case (DPLL, unit propagation, conflict detection, equivalence encoder vs evaluator 2^k, ví dụ trang 4 trong đề) chạy thành công chỉ trong vài mili-giây.
  * Chạy benchmark: `python main.py --benchmark`
    - Bảng kết quả in ra terminal với đầy đủ 6 chỉ số: số biến primary/aux, số mệnh đề CNF, số lần gọi SAT, decisions/propagations/backtracks, số bước suy diễn và thời gian thực thi (ms).
    - Mở file biểu đồ `experiments/benchmark_plots.png` để thuyết minh về độ phức tạp và khả năng mở rộng của thuật toán từ 3x3 đến 5x5.
* **Lời thoại mẫu:**
  > "Nhóm cũng đã chuẩn bị đầy đủ bộ unit test tự động và kịch bản thực nghiệm benchmark.
  >
  > Toàn bộ các kiểm thử về tính tương đương giữa CNF combinatorial encoding và Semantic Evaluator trên không gian $2^k$ đều vượt qua tuyệt đối.
  >
  > Trong bảng thực nghiệm, thời gian giải câu đố 3x3 chỉ mất khoảng 2.5ms, 4x4 khoảng 13ms và 5x5 stress-case khoảng 50ms, với số lần quay lui (backtracks) gần như bằng 0 nhờ hiệu quả lan truyền đơn vị (unit propagation) mạnh mẽ."

---

#### [9:00 - 9:30] Phần 6: Kết luận & Lời cảm ơn
* **Thao tác màn hình:**
  * Quay lại màn hình chính của ứng dụng hoặc Slide kết.
* **Lời thoại mẫu:**
  > "Như vậy, nhóm đã hoàn thành xuất sắc toàn bộ các yêu cầu của Project 2 Griductive Solver: từ biểu diễn logic, mã hóa CNF, bộ giải DPLL, Logic Agent suy diễn không đoán mò, đến giao diện đồ họa GUI hoàn chỉnh và các thực nghiệm chuyên sâu.
  >
  > Nhóm xin chân thành cảm ơn Thầy và quý Thầy Cô trợ giảng đã theo dõi!"

