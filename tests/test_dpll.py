"""
Bộ kiểm thử đơn vị (Unit Tests) cho Bộ giải SAT theo thuật toán DPLL (sat/dpll.py).
Kiểm tra toàn diện các yêu cầu cốt lõi của đề bài:
1. Công thức rỗng và trả về phép gán đầy đủ (complete model)
2. Phát hiện xung đột (conflict detection)
3. Lan truyền đơn vị (unit propagation) và thống kê số lần lan truyền
4. Ví dụ suy diễn hệ quả logic KB trong Mục 3.4 (trang 4) của đề bài với assumptions
5. Phân nhánh đệ quy (branching) và quay lui (backtracking)
6. Công thức UNSAT nhiều biến kèm kiểm tra bộ đếm quay lui (backtracks)
"""

import unittest
from sat.dpll import DPLLSolver


class TestDPLLSolver(unittest.TestCase):
    """Lớp kiểm thử các tính năng cốt lõi của DPLLSolver."""

    def setUp(self):
        """Khởi tạo một đối tượng DPLLSolver mới trước mỗi ca kiểm thử để đảm bảo độc lập."""
        self.solver = DPLLSolver()

    def test_empty_formula(self):
        """
        Kiểm tra công thức rỗng (không có mệnh đề nào):
        - Phải luôn thỏa mãn (SAT).
        - Phải trả về phép gán đầy đủ chứa tất cả các biến từ 1 đến num_vars.
        """
        is_sat, model, stats = self.solver.solve([], num_vars=2)
        self.assertTrue(is_sat)
        self.assertIsNotNone(model)
        self.assertIn(1, model)
        self.assertIn(2, model)

    def test_simple_conflict(self):
        """
        Kiểm tra phát hiện xung đột trực tiếp:
        Công thức (x1) ∧ (¬x1) mâu thuẫn ngay lập tức -> phải trả về UNSAT và model = None.
        """
        clauses = [[1], [-1]]
        is_sat, model, stats = self.solver.solve(clauses, num_vars=1)
        self.assertFalse(is_sat)
        self.assertIsNone(model)

    def test_unit_propagation(self):
        """
        Kiểm tra cơ chế lan truyền đơn vị theo chuỗi (chain unit propagation):
        Công thức: (x1) ∧ (¬x1 ∨ x2) ∧ (¬x2 ∨ x3).
        Từ x1 = True sẽ lan truyền liên tiếp suy ra x2 = True, sau đó suy ra x3 = True.
        Đồng thời kiểm tra bộ đếm thống kê stats.propagations ghi nhận đúng số lần lan truyền.
        """
        clauses = [[1], [-1, 2], [-2, 3]]
        is_sat, model, stats = self.solver.solve(clauses, num_vars=3)
        self.assertTrue(is_sat)
        self.assertTrue(model[1])
        self.assertTrue(model[2])
        self.assertTrue(model[3])
        self.assertGreaterEqual(stats.propagations, 2)

    def test_pdf_example_page_4(self):
        """
        Kiểm chứng ví dụ cơ sở tri thức (KB) tại Mục 3.4 (trang 4) của đề bài:
        KB = (C_A ∨ C_B) ∧ (¬C_A ∨ C_B), ánh xạ C_A = 1, C_B = 2.
        - KB là SAT (ví dụ C_A = False, C_B = True).
        - KB ∧ ¬C_B là UNSAT => suy ra KB |= C_B (nhân vật B chắc chắn là Criminal).
        - Cả KB ∧ C_A và KB ∧ ¬C_A đều SAT => trạng thái của A là UNKNOWN (không được đoán).
        """
        kb_clauses = [[1, 2], [-1, 2]]

        # 1. Kiểm tra tính nhất quán: KB ban đầu phải thỏa mãn (SAT)
        is_sat, model, _ = self.solver.solve(kb_clauses, num_vars=2)
        self.assertTrue(is_sat)

        # 2. Giả sử B vô tội (assumptions=[-2]): KB ∧ ¬C_B phải mâu thuẫn (UNSAT)
        is_sat_neg_b, _, _ = self.solver.solve(kb_clauses, num_vars=2, assumptions=[-2])
        self.assertFalse(is_sat_neg_b, "KB /\ -CB should be UNSAT")

        # 3. Giả sử B là tội phạm (assumptions=[2]): KB ∧ C_B phải thỏa mãn (SAT)
        is_sat_pos_b, _, _ = self.solver.solve(kb_clauses, num_vars=2, assumptions=[2])
        self.assertTrue(is_sat_pos_b, "KB /\ CB should be SAT")

        # => Kết luận: B bắt buộc phải là True (Criminal)

        # 4. Kiểm tra biến C_A (var 1) với cả hai giả thiết True và False
        is_sat_pos_a, _, _ = self.solver.solve(kb_clauses, num_vars=2, assumptions=[1])
        is_sat_neg_a, _, _ = self.solver.solve(kb_clauses, num_vars=2, assumptions=[-1])
        self.assertTrue(is_sat_pos_a, "KB /\ CA should be SAT")
        self.assertTrue(is_sat_neg_a, "KB /\ -CA should be SAT")
        # => Kết luận: Cả 2 trường hợp đều thỏa mãn nên A có trạng thái UNKNOWN

    def test_branching_and_backtracking(self):
        """
        Kiểm tra phân nhánh trên công thức có nghiệm duy nhất:
        (x1 ∨ x2) ∧ (¬x1 ∨ x2) ∧ (x1 ∨ ¬x2).
        Nghiệm duy nhất thỏa mãn cả 3 mệnh đề là x1 = True, x2 = True.
        """
        clauses = [[1, 2], [-1, 2], [1, -2]]
        is_sat, model, stats = self.solver.solve(clauses, num_vars=2)
        self.assertTrue(is_sat)
        self.assertTrue(model[1])
        self.assertTrue(model[2])

    def test_unsat_3vars(self):
        """
        Kiểm tra công thức vô nghiệm (UNSAT) trên 3 biến bắt buộc phải phân nhánh và quay lui:
        Liệt kê toàn bộ 2^3 = 8 mệnh đề loại trừ mọi tổ hợp chân trị có thể của (x1, x2, x3).
        Phải trả về UNSAT, model = None và ghi nhận số lần quay lui stats.backtracks > 0.
        """
        # Toàn bộ 8 tổ hợp chân trị của 3 biến đều bị cấm:
        clauses = [
            [1, 2, 3],
            [1, 2, -3],
            [1, -2, 3],
            [1, -2, -3],
            [-1, 2, 3],
            [-1, 2, -3],
            [-1, -2, 3],
            [-1, -2, -3]
        ]
        is_sat, model, stats = self.solver.solve(clauses, num_vars=3)
        self.assertFalse(is_sat)
        self.assertIsNone(model)
        self.assertGreater(stats.backtracks, 0)


if __name__ == "__main__":
    unittest.main()