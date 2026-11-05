# HƯỚNG DẪN CÁCH CHƠI GRIDUCTIVE (GRIDUCTIVE GAMEPLAY GUIDE)

Chào mừng bạn đến với **Griductive** — trò chơi giải đố trinh thám suy luận trên lưới ô vuông (Grid-Deduction Puzzle). 

Trò chơi này không dựa vào may mắn hay đoán mò, mà hoàn toàn dựa trên **suy luận logic toán học thuần túy (Propositional Logic)**. Mỗi bước đi đúng sẽ lật mở thêm một mắt xích thông tin mới cho đến khi toàn bộ vụ án được phá giải.

---

## 1. MỤC TIÊU CỐT LÕI CỦA TRÒ CHƠI

1. **Bàn cờ $N \times N$**:
   - Trò chơi diễn ra trên một lưới ô vuông kích thước $3 \times 3$, $4 \times 4$ hoặc $5 \times 5$.
   - Mỗi ô được đánh tọa độ theo **Cột (A, B, C...)** và **Hàng (1, 2, 3...)**, ví dụ: `A1`, `B2`, `C4`.
   - Mỗi ô là một nhân vật có tên, nghề nghiệp và hình đại diện riêng.

2. **Hai trạng thái nhị phân**:
   - Mỗi nhân vật trong bàn cờ chỉ có duy nhất **1 trong 2 trạng thái**:
     - 🔴 **Criminal (Tội phạm)**
     - 🟢 **Innocent (Vô tội)**
   - Mục tiêu cuối cùng của bạn là **xác định chính xác trạng thái của tất cả các nhân vật trên bàn cờ**.

3. **Chân lý của Manh mối (Clues)**:
   - Các manh mối xuất hiện trên các thẻ **LUÔN LUÔN ĐÚNG 100% SỰ THẬT**, bất kể người sở hữu thẻ đó là Tội phạm hay Vô tội. *(Không có ai nói dối trong trò chơi này)*.

---

## 2. QUY TẮC VÀNG: TUYỆT ĐỐI KHÔNG ĐOÁN MÒ (NO GUESSING)

Đây là điểm làm nên sự hấp dẫn và độ khó đặc trưng của Griductive:

> **Bạn chỉ được phép phán quyết một nhân vật là Criminal hay Innocent khi và chỉ khi điều đó ĐÃ ĐƯỢC CHỨNG MINH CHẮC CHẮN 100% từ các manh mối đang có trên bàn cờ.**

Khi bạn nhấp vào một nghi phạm chưa mở và đưa ra phán quyết:
* ✅ **ACCEPTED (Chấp nhận)**: 
  Phán quyết của bạn hoàn toàn kéo theo từ logic hiện tại ($KB_t \models C_i$ hoặc $KB_t \models \neg C_i$). Thẻ nhân vật sẽ lật mở, hiển thị trạng thái chính thức và **tiết lộ manh mối mới của nhân vật đó**.
* ⚠️ **REJECTED [NOT_PROVABLE] (Từ chối - Đoán mò)**:
  Tại thời điểm này, manh mối trên bàn cờ chưa đủ thông tin để khẳng định chắc chắn 100%. Dù phán đoán của bạn vô tình trùng khớp với đáp án ẩn, trò chơi **vẫn từ chối** vì bạn đang đoán mò.
* ❌ **REJECTED [CONTRADICTED] (Từ chối - Mâu thuẫn)**:
  Phán quyết của bạn đi ngược lại hoàn toàn với những gì logic đã chứng minh (ví dụ: người đó chắc chắn Vô tội nhưng bạn lại gọi là Tội phạm).

---

## 3. CÁC DẠNG MANH MỐI TRONG GAME & CÁCH GIẢI MÃ

Khi một thẻ được lật mở, nó sẽ cung cấp một manh mối thuộc các dạng sau:

| Dạng manh mối | Ví dụ câu chữ trong game | Ý nghĩa logic |
| :--- | :--- | :--- |
| **FACT** | `Clara is INNOCENT.` | Nhân vật này trực tiếp là Vô tội (hoặc Tội phạm). |
| **SAME** | `Fern and Gina have the SAME status.` | Cả hai cùng là Tội phạm, HOẶC cả hai cùng là Vô tội ($A \iff B$). |
| **DIFFERENT** | `Paul and Noah have DIFFERENT statuses.` | Một người là Tội phạm, người kia là Vô tội ($A \oplus B$). |
| **EXACTLY** | `Row 2 contains exactly 2 criminals.` | Trong hàng 2 có chính xác 2 người là Tội phạm. |
| **AT LEAST** | `Row 3 has at least 1 criminal.` | Trong hàng 3 có ít nhất 1 Tội phạm (tức $\ge 1$). |
| **AT MOST** | `Column A has at most 2 criminals.` | Trong cột A có nhiều nhất 2 Tội phạm (tức $\le 2$). |
| **PARITY** | `Column C criminal count is ODD.` | Số tội phạm trong cột C là số lẻ (1 hoặc 3). *(Nếu EVEN thì là số chẵn: 0, 2)* |
| **COMPARE** | `Row 1 has more criminals than Row 2.` | Số tội phạm ở Hàng 1 lớn hơn Hàng 2. |

> [!NOTE]
> **Khái niệm "Neighbors" (Hàng xóm / Láng giềng)**:
> Hàng xóm của một ô là **8 ô xung quanh** nó (trên, dưới, trái, phải và 4 đường chéo). Các ô ở góc bàn cờ sẽ có 3 hàng xóm, ô ở mép biên có 5 hàng xóm, và ô ở giữa có 8 hàng xóm.

---

## 4. VÍ DỤ MỘT QUÁ TRÌNH SUY LUẬN MẪU (BÀN 3x3)

Hãy xem cách một thám tử logic suy luận giải một ván cờ:

```
      A         B         C
  ┌─────────┬─────────┬─────────┐
1 │  Abel   │  [B1]   │  Clara  │    [B1] được mở sẵn từ đầu:
  ├─────────┼─────────┼─────────┤    "Abel (A1) and Clara (C1)
2 │  Derek  │  Eliza  │  Franz  │     are both CRIMINALS"
  ├─────────┼─────────┼─────────┤
3 │  Grant  │ Hannah  │   Ivy   │
  └─────────┴─────────┴─────────┘
```

1. **Bước 1**:
   - Manh mối ban đầu tại `B1` cho biết: *Abel (A1) và Clara (C1) đều là Criminals*.
   - **Hành động**: Nhấp vào `A1` gọi **Criminal** ➔ Hệ thống: `ACCEPTED`!
   - Thẻ `A1` lật mở, lộ manh mối mới: *"Abel (A1) and Derek (A2) have DIFFERENT statuses"*.

2. **Bước 2**:
   - Ta đã biết chắc chắn `A1` là **Criminal**.
   - Manh mối `A1` nói rằng `A1` và `A2` có trạng thái **DIFFERENT** (khác nhau).
   - Suy ra ngay lập tức: **`A2` (Derek) bắt buộc phải là INNOCENT**!
   - **Hành động**: Nhấp vào `A2` gọi **Innocent** ➔ Hệ thống: `ACCEPTED`!
   - Thẻ `A2` lật mở, lộ manh mối mới: *"Derek (A2) and Franz (C2) have the SAME status"*.

3. **Bước 3**:
   - `A2` là **Innocent**, và `A2` có **SAME status** với `C2`.
   - Suy ra: **`C2` (Franz) bắt buộc là INNOCENT**!
   - Tiếp tục lặp lại quá trình này theo dây chuyền cho đến khi toàn bộ 9 ô được giải xong!

---

## 5. CÁC TÍNH NĂNG VÀ THAO TÁC TRÊN GIAO DIỆN WEB

Khi mở giao diện web (`python main.py`), bạn sẽ có các công cụ trợ giúp đắc lực:

1. **Nhấp vào thẻ chưa mở**:
   - Hộp thoại xuất hiện cho phép bạn ra phán quyết:
     - Nút đỏ: **Criminal** (Tội phạm)
     - Nút xanh: **Innocent** (Vô tội)
     - Nút nháp: **Pencil Mark** (Ghi chú suy đoán tạm thời của bạn lên góc thẻ mà không kích hoạt kiểm tra logic).

2. **Nhấp vào thẻ đã mở (Inspect Clue)**:
   - Khi bạn nhấp vào một thẻ đã lật, **tất cả các ô mà manh mối đó tham chiếu tới sẽ được viền vàng rực rỡ** trên bàn cờ. Tính năng này giúp bạn dễ dàng nhìn ra vùng quan sát mà không sợ nhìn nhầm tọa độ.

3. **Nút "Hint" (Bóng đèn gợi ý)**:
   - Nếu bạn bị bí nước đi, hãy bấm **Hint**.
   - Hệ thống Logic Agent sẽ rà soát cơ sở tri thức hiện tại và **khoanh vùng xanh dương nhấp nháy** vào ô tiếp theo đã đủ bằng chứng để chứng minh, kèm theo manh mối gợi ý, **tuyệt đối không làm lộ đáp án**.

4. **Nút "Auto Solve" (AI tự giải)**:
   - `Auto Step`: Yêu cầu Logic Agent tự chứng minh và giải thay bạn đúng **1 bước tiếp theo**.
   - `Auto Solve (All)`: Kích hoạt AI tự động giải liên tục từ đầu đến cuối bàn cờ.

5. **Nút "Trace" (Nhật ký suy luận logic)**:
   - Mở ngăn kéo bên phải hiển thị toàn bộ phép toán SAT đằng sau: bước này đã truy vấn mệnh đề nào, thời gian xử lý bao nhiêu mili-giây, và biến nào bị ép buộc giá trị.

6. **Nút "Unique" (Kiểm tra nghiệm duy nhất)**:
   - Yêu cầu DPLL Solver chứng minh rằng câu đố này được thiết kế chuẩn mực, chỉ có duy nhất **1 nghiệm đúng**, không bao giờ bị đa nghiệm mập mờ.

---

## 6. MẸO CHƠI GIÚP BẠN NHANH CHÓNG PHÁ ĐẢO

* **Ưu tiên các manh mối trực tiếp trước (`FACT`, `SAME`, `DIFFERENT`)**: Khi một nhân vật đã biết trạng thái, mọi liên kết `SAME` hoặc `DIFFERENT` với người đó sẽ lập tức xác định được người còn lại.
* **Đếm số lượng trong Hàng / Cột (`EXACTLY`)**: 
  - Nếu một hàng có 4 người, manh mối bảo *có đúng 1 tội phạm*, mà bạn đã tìm ra 1 tội phạm rồi ➔ **Tất cả 3 người còn lại trong hàng đó chắc chắn là Innocent**!
  - Ngược lại, nếu hàng có 4 người, có 2 tội phạm, mà bạn đã tìm ra 2 người Innocent ➔ **2 người còn lại chắc chắn là Criminal**!
* **Dùng chức năng Highlight**: Luôn nhấp vào các manh mối để xem viền vàng làm sáng các ô liên quan, giúp bạn kết hợp nhiều manh mối cùng một lúc rất nhanh.
* **Không bao giờ "liều mạng" bấm thử**: Nhớ rằng mỗi lần đoán mò đều bị từ chối `NOT_PROVABLE`. Hãy tập trung tìm mối dây liên kết logic!

