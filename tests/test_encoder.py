"""
Kiểm thử đơn vị đối chiếu Bộ mã hóa CNF (CNF Encoder) và Bộ đánh giá ngữ nghĩa trực tiếp (Semantic Evaluator).
Thực hiện kiểm tra tương đương vét cạn (brute-force) trên toàn bộ 2^k và 2^9 phép gán chân trị
cho tất cả mẫu manh mối chuẩn, phần mở rộng (PARITY, COMPARE, vùng nâng cao), KnowledgeBase và VariableMap.
"""

import unittest
import itertools
from typing import List, Dict
from engine.region import Region, get_all_cells
from engine.clue import Clue
from engine.evaluator import evaluate_clue, evaluate_all
from logic.var_map import VariableMap
from logic.encoder import CNFEncoder
from logic.kb import KnowledgeBase, build_kb


def check_cnf_satisfaction(clauses: List[List[int]], assignment: Dict[int, bool]) -> bool:
    """Đánh giá độc lập công thức CNF có thỏa mãn dưới một phép gán hay không (không qua DPLL)."""
    for clause in clauses:
        clause_satisfied = False
        for lit in clause:
            var = abs(lit)
            val = assignment.get(var, False)
            if (lit > 0 and val) or (lit < 0 and not val):
                clause_satisfied = True
                break
        if not clause_satisfied:
            return False
    return True


class TestEncoderVsEvaluator(unittest.TestCase):
    """Bộ kiểm thử đối chiếu tính tương đương logic giữa CNFEncoder và Semantic Evaluator."""

    def setUp(self):
        self.n = 3
        self.cells = get_all_cells(self.n)
        self.var_map = VariableMap(self.cells)
        self.encoder = CNFEncoder(self.var_map, self.n)

    def _verify_clue_equivalence(self, clue: Clue, relevant_cells: List[str]):
        """
        Kiểm tra vét cạn 2^k phép gán trên các ô liên quan của một clue:
        kết quả evaluate_clue phải trùng khớp tuyệt đối với check_cnf_satisfaction.
        """
        clauses = self.encoder.encode_clue(clue)
        num_cells = len(relevant_cells)

        for bits in itertools.product([False, True], repeat=num_cells):
            # Tạo phép gán cho các ô liên quan
            cell_assignment = {cell: bits[i] for i, cell in enumerate(relevant_cells)}
            # Điền False cho các ô còn lại trên lưới
            full_assignment = {c: False for c in self.cells}
            full_assignment.update(cell_assignment)

            # Chuyển sang phép gán theo ID biến SAT
            var_assignment = {self.var_map.coord_to_var(c): full_assignment[c] for c in self.cells}

            eval_res = evaluate_clue(clue, full_assignment, self.n)
            cnf_res = check_cnf_satisfaction(clauses, var_assignment)

            self.assertEqual(
                eval_res, cnf_res,
                f"Mismatch for clue {clue.clue_type} with assignment {cell_assignment}: eval={eval_res}, cnf={cnf_res}"
            )

    def test_fact_criminal(self):
        """Kiểm tra clue FACT với trạng thái CRIMINAL."""
        clue = Clue(id="c1", clue_type="FACT", params={"target": "A1", "status": "CRIMINAL"})
        self._verify_clue_equivalence(clue, ["A1"])

    def test_fact_innocent(self):
        """Kiểm tra clue FACT với trạng thái INNOCENT."""
        clue = Clue(id="c2", clue_type="FACT", params={"target": "B2", "status": "INNOCENT"})
        self._verify_clue_equivalence(clue, ["B2"])

    def test_same(self):
        """Kiểm tra clue SAME trên tất cả 2^2 phép gán."""
        clue = Clue(id="c3", clue_type="SAME", params={"target1": "A1", "target2": "B2"})
        self._verify_clue_equivalence(clue, ["A1", "B2"])

    def test_different(self):
        """Kiểm tra clue DIFFERENT trên tất cả 2^2 phép gán."""
        clue = Clue(id="c4", clue_type="DIFFERENT", params={"target1": "A1", "target2": "B2"})
        self._verify_clue_equivalence(clue, ["A1", "B2"])

    def test_exactly_row(self):
        """Kiểm tra clue EXACTLY trên vùng ROW với k từ 0 đến 3."""
        region = Region(region_type="ROW", param=1)  # A1, B1, C1
        for k in range(0, 4):
            clue = Clue(id=f"c_ex_{k}", clue_type="EXACTLY", params={"k": k, "region": region})
            self._verify_clue_equivalence(clue, ["A1", "B1", "C1"])

    def test_at_least_col(self):
        """Kiểm tra clue AT_LEAST trên vùng COL với k từ 0 đến 3."""
        region = Region(region_type="COL", param="B")  # B1, B2, B3
        for k in range(0, 4):
            clue = Clue(id=f"c_al_{k}", clue_type="AT_LEAST", params={"k": k, "region": region})
            self._verify_clue_equivalence(clue, ["B1", "B2", "B3"])

    def test_at_most_neighbors(self):
        """Kiểm tra clue AT_MOST trên vùng NEIGHBORS với k từ 0 đến 3."""
        region = Region(region_type="NEIGHBORS", param="A1")  # A2, B1, B2 (3 ô)
        for k in range(0, 4):
            clue = Clue(id=f"c_am_{k}", clue_type="AT_MOST", params={"k": k, "region": region})
            self._verify_clue_equivalence(clue, region.resolve(self.n))

    def test_parity_even_and_odd(self):
        """Kiểm tra mở rộng PARITY cho cả EVEN và ODD."""
        region = Region(region_type="ROW", param=2)  # A2, B2, C2
        for parity in ("EVEN", "ODD"):
            clue = Clue(id=f"c_par_{parity}", clue_type="PARITY", params={"parity": parity, "region": region})
            self._verify_clue_equivalence(clue, ["A2", "B2", "C2"])

    def test_compare_regions(self):
        """Kiểm tra mở rộng COMPARE giữa 2 vùng với các toán tử >, <, =."""
        r1 = Region(region_type="EXPLICIT", param=["A1", "A2"])
        r2 = Region(region_type="EXPLICIT", param=["B1", "B2"])
        for op in (">", "<", "="):
            clue = Clue(id=f"c_cmp_{op}", clue_type="COMPARE", params={"region1": r1, "region2": r2, "op": op})
            self._verify_clue_equivalence(clue, ["A1", "A2", "B1", "B2"])

    def test_full_board_2_pow_9_kb_equivalence(self):
        """
        Brute-force toàn bộ 2^9 = 512 phép gán trên lưới 3x3:
        Kiểm tra KB_t (gồm nhiều clue + proved verdicts qua build_kb)
        khớp hoàn toàn với đánh giá trực tiếp evaluate_all.
        """
        clues = [
            Clue(id="c1", clue_type="EXACTLY", params={"k": 2, "region": Region("ROW", 1)}),
            Clue(id="c2", clue_type="DIFFERENT", params={"target1": "A1", "target2": "B2"}),
            Clue(id="c3", clue_type="PARITY", params={"parity": "ODD", "region": Region("CORNERS")}),
        ]
        proved = {"B1": "INNOCENT", "C3": "CRIMINAL"}

        kb = build_kb(clues, proved, self.var_map, self.n)
        clauses = kb.get_clauses()

        # Duyệt toàn bộ 2^9 = 512 cấu hình của bàn cờ 3x3
        for bits in itertools.product([False, True], repeat=len(self.cells)):
            cell_assignment = {cell: bits[i] for i, cell in enumerate(self.cells)}
            var_assignment = {
                self.var_map.coord_to_var(c): cell_assignment[c]
                for c in self.cells
            }

            # Kết quả ngữ nghĩa trực tiếp: thỏa mọi clue VÀ đúng mọi verdict đã chứng minh
            expected_proved = (
                cell_assignment["B1"] is False and cell_assignment["C3"] is True
            )
            eval_res = expected_proved and evaluate_all(clues, cell_assignment, self.n)
            cnf_res = check_cnf_satisfaction(clauses, var_assignment)

            self.assertEqual(
                eval_res, cnf_res,
                f"Full-board mismatch at {cell_assignment}: eval={eval_res}, cnf={cnf_res}"
            )

    def test_advanced_regions_equivalence(self):
        """Brute-force 2^m kiểm tra các vùng nâng cao: CORNERS, BOUNDARY, COMMON_NEIGHBORS, BETWEEN."""
        regions = [
            ("corners", Region("CORNERS"), "EXACTLY", {"k": 2}),
            ("boundary", Region("BOUNDARY"), "AT_LEAST", {"k": 3}),
            ("common_nb", Region("COMMON_NEIGHBORS", ("A1", "C1")), "AT_MOST", {"k": 1}),
            ("between", Region("BETWEEN", ("A1", "C3")), "PARITY", {"parity": "ODD"}),
        ]
        for tag, reg, ctype, extra in regions:
            params = dict(extra)
            params["region"] = reg
            clue = Clue(id=f"adv_{tag}", clue_type=ctype, params=params)
            self._verify_clue_equivalence(clue, reg.resolve(self.n))

    def test_validation_and_kb_guards(self):
        """Kiểm tra validate_clue và KnowledgeBase bắt đúng các trường hợp dữ liệu lỗi."""
        # 1. k > |R| (A1 chỉ có 3 hàng xóm trên lưới 3x3)
        bad_k = Clue(id="bad_k", clue_type="EXACTLY", params={"k": 4, "region": Region("NEIGHBORS", "A1")})
        with self.assertRaises(ValueError):
            self.encoder.encode_clue(bad_k)

        # 2. Tọa độ ngoài biên lưới 3x3
        bad_coord = Clue(id="bad_c", clue_type="FACT", params={"target": "Z9", "status": "CRIMINAL"})
        with self.assertRaises(ValueError):
            self.encoder.encode_clue(bad_coord)

        # 3. k kiểu bool phải bị từ chối
        bool_k = Clue(id="bool_k", clue_type="AT_MOST", params={"k": True, "region": Region("ROW", 1)})
        with self.assertRaises(ValueError):
            self.encoder.encode_clue(bool_k)

        # 4. KnowledgeBase từ chối status sai và verdict mâu thuẫn
        kb = KnowledgeBase(self.var_map, self.n)
        with self.assertRaises(ValueError):
            kb.add_verdict("A1", "UNKNOWN")

        kb.add_verdict("A1", "CRIMINAL")
        with self.assertRaises(ValueError):
            kb.add_verdict("A1", "INNOCENT")

        stats = kb.get_stats()
        self.assertEqual(stats["num_primary_vars"], 9)
        self.assertEqual(stats["num_aux_vars"], 0)
        self.assertEqual(stats["num_clauses"], 1)

    def test_variable_map_determinism_and_aux(self):
        """Kiểm tra ánh xạ row-major xác định, tra cứu theo tên nhân vật và quản lý biến phụ."""
        shuffled = ["C3", "A1", "B2", "C1", "A3", "B1", "A2", "C2", "B3"]
        vm = VariableMap(shuffled, character_names={"A1": "Abel", "B2": "Eliza"})

        # Dù đầu vào xáo trộn vẫn ánh xạ đúng thứ tự row-major (A1=1, B1=2, ..., C3=9)
        self.assertEqual(vm.coord_to_var("A1"), 1)
        self.assertEqual(vm.coord_to_var("B1"), 2)
        self.assertEqual(vm.coord_to_var("C1"), 3)
        self.assertEqual(vm.coord_to_var("B2"), 5)
        self.assertEqual(vm.coord_to_var("C3"), 9)

        # Tra cứu theo tên nhân vật và giải mã ngược literal âm
        self.assertEqual(vm.coord_to_var("Abel"), 1)
        self.assertEqual(vm.var_to_coord(-5), "B2")

        # Kiểm tra cấp phát và reset biến phụ tách biệt khỏi biến chính
        aux_id = vm.alloc_aux_var("tmp_xor")
        self.assertEqual(aux_id, 10)
        self.assertFalse(vm.is_primary(aux_id))
        self.assertTrue(vm.is_primary(1))
        self.assertEqual(vm.num_primary, 9)
        self.assertEqual(vm.num_aux, 1)
        self.assertEqual(vm.total_vars, 10)

        vm.reset_aux()
        self.assertEqual(vm.num_aux, 0)
        self.assertEqual(vm.total_vars, 9)


if __name__ == "__main__":
    unittest.main()
