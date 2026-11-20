"""
Bộ giải SAT theo thuật toán DPLL (Davis-Putnam-Logemann-Loveland) cho bài toán Griductive.
Đáp ứng đầy đủ các yêu cầu của đề bài (Mục 4.3):
1. Lan truyền đơn vị (Unit propagation)
2. Phát hiện xung đột (Conflict detection)
3. Chọn biến xác định (Deterministic variable selection)
4. Phân nhánh đệ quy và quay lui (Recursive branching & backtracking)
5. Trả về SAT kèm phép gán đầy đủ hoặc UNSAT
6. Thống kê số lần quyết định (decisions), lan truyền (propagations), quay lui (backtracks) và thời gian chạy (runtime)
7. Hỗ trợ giả thiết tạm thời (assumptions / unit literals) phục vụ kiểm tra hệ quả logic
"""

import time
from typing import List, Dict, Optional, Tuple, Set, Any
from dataclasses import dataclass


@dataclass
class DPLLStats:
    """
    Lớp lưu trữ các chỉ số thống kê hiệu năng của một lần chạy bộ giải DPLL:
    - decisions: số lần thuật toán phải chọn giá trị (phân nhánh) cho một biến chưa xác định.
    - propagations: số lần gán giá trị tự động nhờ luật lan truyền đơn vị (unit propagation).
    - backtracks: số lần nhánh tìm kiếm gặp mâu thuẫn và phải quay lui.
    - runtime: tổng thời gian thực thi của hàm solve() tính bằng giây.
    """
    decisions: int = 0
    propagations: int = 0
    backtracks: int = 0
    runtime: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi các chỉ số thống kê sang dạng dictionary để dễ xuất log hoặc lưu CSV."""
        return {
            "decisions": self.decisions,
            "propagations": self.propagations,
            "backtracks": self.backtracks,
            "runtime": self.runtime
        }


class DPLLSolver:
    """
    Bộ giải SAT mệnh đề dựa trên thủ tục DPLL.
    Làm việc với công thức CNF biểu diễn bằng danh sách các mệnh đề số nguyên,
    ví dụ: [[1, -2], [-1, 3]] tương ứng với (x1 ∨ ¬x2) ∧ (¬x1 ∨ x3).
    """

    def __init__(self):
        """Khởi tạo bộ giải với bộ đếm thống kê rỗng và danh sách biến chưa xác định."""
        self.stats = DPLLStats()
        self._all_vars: List[int] = []

    def solve(
        self,
        clauses: List[List[int]],
        num_vars: Optional[int] = None,
        assumptions: Optional[List[int]] = None
    ) -> Tuple[bool, Optional[Dict[int, bool]], DPLLStats]:
        """
        Hàm chính giải bài toán thỏa mãn công thức CNF (có hỗ trợ giả thiết tạm thời).

        Tham số:
            clauses: Danh sách các mệnh đề CNF (mỗi mệnh đề là một list các literal khác 0).
            num_vars: Tổng số biến mệnh đề cần quản lý (1..num_vars), đảm bảo phép gán trả về đầy đủ.
            assumptions: Danh sách các literal giả thiết tạm thời (ví dụ [-v] để kiểm tra KB ∧ ¬C_i).

        Trả về:
            (is_sat, model, stats):
            - Nếu thỏa mãn (SAT): (True, từ điển ánh xạ đầy đủ {var_id: bool}, đối tượng DPLLStats).
            - Nếu không thỏa mãn (UNSAT): (False, None, đối tượng DPLLStats).
        """
        start_time = time.perf_counter()
        self.stats = DPLLStats()

        # Bước 1: Thu thập toàn bộ chỉ số biến xuất hiện trong clauses, assumptions và phạm vi 1..num_vars
        var_set: Set[int] = set()
        for clause in clauses:
            for lit in clause:
                var_set.add(abs(lit))
        if assumptions:
            for lit in assumptions:
                var_set.add(abs(lit))
        if num_vars:
            for v in range(1, num_vars + 1):
                var_set.add(v)

        # Sắp xếp biến tăng dần để đảm bảo việc chọn biến luôn xác định (deterministic)
        self._all_vars = sorted(list(var_set))

        # Bước 2: Tạo bản sao công thức gốc để tránh làm thay đổi dữ liệu bên ngoài,
        # đồng thời thêm các assumptions dưới dạng mệnh đề đơn vị (unit clauses)
        working_clauses = [list(c) for c in clauses]
        if assumptions:
            for lit in assumptions:
                working_clauses.append([lit])

        assignment: Dict[int, bool] = {}

        # Bước 3: Gọi thủ tục đệ quy DPLL để tìm phép gán thỏa mãn
        is_sat, final_assignment = self._dpll(working_clauses, assignment)

        # Ghi nhận tổng thời gian thực thi
        self.stats.runtime = time.perf_counter() - start_time

        if is_sat:
            # Bước 4: Nếu SAT, điền mặc định False cho các biến tự do chưa cần gán
            # để đảm bảo luôn trả về một mô hình (complete assignment) đầy đủ và xác định
            assert final_assignment is not None
            for v in self._all_vars:
                if v not in final_assignment:
                    final_assignment[v] = False
            return True, final_assignment, self.stats
        else:
            return False, None, self.stats

    def _evaluate_clause(self, clause: List[int], assignment: Dict[int, bool]) -> Tuple[Optional[bool], List[int]]:
        """
        Đánh giá trạng thái của một mệnh đề CNF dưới phép gán bộ phận hiện tại.

        Tham số:
            clause: Một mệnh đề gồm các literal (số nguyên dương là khẳng định, âm là phủ định).
            assignment: Phép gán hiện tại {var_id: True/False}.

        Trả về:
            (clause_status, unassigned_literals):
            - (True, []): Mệnh đề đã thỏa mãn (có ít nhất một literal đúng).
            - (False, []): Xung đột / mâu thuẫn (tất cả literal trong mệnh đề đều sai).
            - (None, unassigned): Mệnh đề chưa xác định, kèm danh sách các literal chưa được gán giá trị.
        """
        unassigned = []
        for lit in clause:
            var = abs(lit)
            if var in assignment:
                val = assignment[var]
                # Literal đúng nếu (lit > 0 và biến = True) hoặc (lit < 0 và biến = False)
                if (lit > 0 and val) or (lit < 0 and not val):
                    return True, []
            else:
                unassigned.append(lit)

        if not unassigned:
            # Không có literal nào đúng và cũng không còn literal chưa gán -> phát hiện xung đột
            return False, []
        return None, unassigned

    def _unit_propagate(
        self,
        clauses: List[List[int]],
        assignment: Dict[int, bool]
    ) -> Tuple[bool, Dict[int, bool]]:
        """
        Thực hiện lan truyền đơn vị (Unit Propagation) lặp cho đến khi đạt điểm dừng hoặc gặp xung đột.
        Nếu một mệnh đề chưa thỏa mãn chỉ còn đúng 1 literal chưa gán (unit clause),
        literal đó bắt buộc phải nhận giá trị True để mệnh đề không bị sai.

        Tham số:
            clauses: Danh sách toàn bộ mệnh đề CNF.
            assignment: Phép gán hiện tại trước khi lan truyền.

        Trả về:
            (success, updated_assignment):
            - success = True nếu không có mâu thuẫn, kèm phép gán sau khi đã lan truyền tối đa.
            - success = False nếu phát hiện xung đột (mệnh đề rỗng hoặc gán mâu thuẫn trên cùng 1 biến).
        """
        current_assign = dict(assignment)

        while True:
            unit_found = False
            for clause in clauses:
                status, unassigned = self._evaluate_clause(clause, current_assign)
                if status is False:
                    # Phát hiện xung đột: mọi literal trong mệnh đề đều nhận giá trị False
                    return False, current_assign
                elif status is None and len(unassigned) == 1:
                    # Tìm thấy mệnh đề đơn vị (chỉ còn duy nhất 1 literal chưa gán)
                    unit_lit = unassigned[0]
                    var = abs(unit_lit)
                    val = (unit_lit > 0)
                    if var in current_assign:
                        if current_assign[var] != val:
                            return False, current_assign
                    else:
                        # Gán giá trị bắt buộc cho biến và tăng bộ đếm lan truyền
                        current_assign[var] = val
                        self.stats.propagations += 1
                        unit_found = True
                        break  # Quét lại từ đầu để tiếp tục lan truyền hệ quả mới

            # Dừng vòng lặp khi không còn mệnh đề đơn vị nào nữa
            if not unit_found:
                break

        return True, current_assign

    def _dpll(
        self,
        clauses: List[List[int]],
        assignment: Dict[int, bool]
    ) -> Tuple[bool, Optional[Dict[int, bool]]]:
        """
        Thủ tục đệ quy cốt lõi của thuật toán DPLL:
        1. Chạy lan truyền đơn vị (Unit Propagation) và kiểm tra xung đột.
        2. Kiểm tra điều kiện dừng: nếu tất cả mệnh đề đều thỏa mãn -> trả về SAT.
        3. Chọn biến chưa gán đầu tiên theo thứ tự xác định (Deterministic Variable Selection).
        4. Phân nhánh đệ quy thử lần lượt True rồi False; nếu thất bại thì quay lui (Backtracking).
        """
        # Bước 1: Lan truyền đơn vị; nếu gặp xung đột thì cắt nhánh ngay lập tức
        success, propagated_assignment = self._unit_propagate(clauses, assignment)
        if not success:
            return False, None

        # Bước 2: Kiểm tra xem toàn bộ các mệnh đề đã được thỏa mãn hay chưa
        all_satisfied = True
        for clause in clauses:
            status, _ = self._evaluate_clause(clause, propagated_assignment)
            if status is False:
                return False, None
            if status is not True:
                all_satisfied = False

        if all_satisfied:
            return True, propagated_assignment

        # Bước 3: Chọn biến xác định - lấy biến có ID nhỏ nhất chưa được gán trong _all_vars
        chosen_var = None
        for v in self._all_vars:
            if v not in propagated_assignment:
                chosen_var = v
                break

        if chosen_var is None:
            # Đã gán hết tất cả các biến
            return all_satisfied, propagated_assignment if all_satisfied else None

        # Bước 4: Phân nhánh đệ quy và quay lui
        # Nhánh 1: Thử gán chosen_var = True
        self.stats.decisions += 1
        branch_assign_true = dict(propagated_assignment)
        branch_assign_true[chosen_var] = True
        sat_res, model = self._dpll(clauses, branch_assign_true)
        if sat_res:
            return True, model

        # Nhánh 1 thất bại -> quay lui và thử Nhánh 2: gán chosen_var = False
        self.stats.backtracks += 1
        self.stats.decisions += 1
        branch_assign_false = dict(propagated_assignment)
        branch_assign_false[chosen_var] = False
        sat_res, model = self._dpll(clauses, branch_assign_false)
        if sat_res:
            return True, model

        # Cả hai nhánh đều mâu thuẫn -> quay lui lên mức gọi đệ quy trước đó
        self.stats.backtracks += 1
        return False, None