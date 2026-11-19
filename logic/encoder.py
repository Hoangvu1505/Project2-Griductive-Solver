"""
Bộ mã hóa CNF (CNF Encoder) cho các manh mối Griductive.
Kiểm tra tính hợp lệ và chuyển đổi các manh mối có cấu trúc sang dạng chuẩn hội (CNF)
bằng phương pháp mã hóa tổ hợp trực tiếp (direct combinatorial encoding).
"""

from typing import List, Dict, Any, Optional
import itertools
from engine.clue import Clue
from engine.region import Region, coord_to_rc
from logic.var_map import VariableMap


def _validate_coord(
    target: str,
    n: int,
    clue_id: str,
    name_to_coord: Optional[Dict[str, str]] = None
) -> str:
    """
    Chuẩn hóa tên nhân vật/tọa độ và kiểm tra tọa độ có nằm trong lưới n x n không.
    Trả về tọa độ viết hoa (ví dụ 'A1'), ném ValueError nếu sai định dạng hoặc ngoài lưới.
    """
    item = str(target).strip()
    if name_to_coord and item in name_to_coord:
        item = name_to_coord[item]
    coord = item.upper()

    if len(coord) < 2 or not coord[0].isalpha() or not coord[1:].isdigit():
        raise ValueError(f"Clue {clue_id}: Invalid coordinate '{target}'")

    row_idx, col_idx = coord_to_rc(coord)
    if not (0 <= row_idx < n and 0 <= col_idx < n):
        raise ValueError(
            f"Clue {clue_id}: Coordinate '{coord}' out of bounds for {n}x{n} grid"
        )
    return coord


def _validate_and_resolve_region(
    region: Any,
    n: int,
    clue_id: str,
    name_to_coord: Optional[Dict[str, str]] = None
) -> List[str]:
    """
    Kiểm tra region hợp lệ (đúng kiểu Region, tham số không vượt biên lưới n x n)
    và trả về danh sách các ô đã được phân giải.
    """
    if not isinstance(region, Region):
        raise ValueError(f"Clue {clue_id}: Missing or invalid Region object")

    rtype = region.region_type.upper()
    if rtype == 'NEIGHBORS':
        _validate_coord(str(region.param), n, clue_id, name_to_coord)
    elif rtype in ('COMMON_NEIGHBORS', 'BETWEEN'):
        if not isinstance(region.param, (list, tuple)) or len(region.param) != 2:
            raise ValueError(f"Clue {clue_id}: {rtype} requires 2 coordinates")
        _validate_coord(str(region.param[0]), n, clue_id, name_to_coord)
        _validate_coord(str(region.param[1]), n, clue_id, name_to_coord)

    cells = region.resolve(n, name_to_coord)
    for cell in cells:
        _validate_coord(cell, n, clue_id, name_to_coord)
    return cells


def validate_clue(clue: Clue, n: int, name_to_coord: Optional[Dict[str, str]] = None) -> None:
    """
    Kiểm tra toàn diện tham số và vùng tham chiếu của một Clue.
    Ném ValueError hoặc KeyError nếu phát hiện dữ liệu không hợp lệ.
    """
    if n <= 0:
        raise ValueError(f"Grid size n must be positive, got {n}")

    ctype = clue.clue_type.upper()

    if ctype == 'FACT':
        target = clue.params.get("target") or clue.params.get("cell")
        if not target:
            raise ValueError(f"Clue {clue.id}: FACT missing target")
        _validate_coord(target, n, clue.id, name_to_coord)

        status = str(clue.params.get("status", "")).upper()
        if status not in ('CRIMINAL', 'INNOCENT'):
            raise ValueError(f"Clue {clue.id}: Invalid status '{status}'")

    elif ctype in ('SAME', 'DIFFERENT'):
        t1 = clue.params.get("target1") or clue.params.get("cell1")
        t2 = clue.params.get("target2") or clue.params.get("cell2")
        if not t1 or not t2:
            raise ValueError(f"Clue {clue.id}: {ctype} requires target1 and target2")
        _validate_coord(t1, n, clue.id, name_to_coord)
        _validate_coord(t2, n, clue.id, name_to_coord)

    elif ctype in ('EXACTLY', 'AT_LEAST', 'AT_MOST'):
        if "k" not in clue.params:
            raise ValueError(f"Clue {clue.id}: Missing parameter 'k'")
        raw_k = clue.params["k"]
        if isinstance(raw_k, bool) or not isinstance(raw_k, int):
            raise ValueError(f"Clue {clue.id}: 'k' must be an integer, got {raw_k!r}")

        cells = _validate_and_resolve_region(
            clue.params.get("region"), n, clue.id, name_to_coord
        )
        m = len(cells)
        if raw_k < 0 or raw_k > m:
            raise ValueError(f"Clue {clue.id}: k={raw_k} out of range [0, {m}] for region")

    elif ctype == 'PARITY':
        parity = str(clue.params.get("parity", "")).upper()
        if parity not in ('EVEN', 'ODD'):
            raise ValueError(f"Clue {clue.id}: Parity must be 'EVEN' or 'ODD'")
        _validate_and_resolve_region(
            clue.params.get("region"), n, clue.id, name_to_coord
        )

    elif ctype == 'COMPARE':
        op = clue.params.get("op", "")
        if op not in ('>', '<', '=', '==', '>=', '<='):
            raise ValueError(f"Clue {clue.id}: Invalid comparison operator '{op}'")
        _validate_and_resolve_region(
            clue.params.get("region1"), n, clue.id, name_to_coord
        )
        _validate_and_resolve_region(
            clue.params.get("region2"), n, clue.id, name_to_coord
        )

    else:
        raise ValueError(f"Unknown clue type '{ctype}'")


class CNFEncoder:
    """
    Chuyển đổi các đối tượng Clue của Griductive sang danh sách mệnh đề CNF.
    Định dạng clause: danh sách số nguyên, ví dụ [-1, 2] biểu diễn (¬C_1 ∨ C_2).
    """

    def __init__(self, var_map: VariableMap, n: int):
        self.var_map = var_map
        self.n = n

    def encode_fact(self, target: str, status: str) -> List[List[int]]:
        """
        Mã hóa clue FACT thành 1 unit clause:
        - CRIMINAL => C_v  => [[v]]
        - INNOCENT => ¬C_v => [[-v]]
        """
        v = self.var_map.coord_to_var(target)
        status_upper = status.upper()
        if status_upper == 'CRIMINAL':
            return [[v]]
        elif status_upper == 'INNOCENT':
            return [[-v]]
        else:
            raise ValueError(f"Unknown status: {status}")

    def encode_same(self, t1: str, t2: str) -> List[List[int]]:
        """
        Mã hóa clue SAME (v1 ↔ v2):
        (v1 ↔ v2) ≡ (¬v1 ∨ v2) ∧ (v1 ∨ ¬v2).
        """
        v1 = self.var_map.coord_to_var(t1)
        v2 = self.var_map.coord_to_var(t2)
        return [[-v1, v2], [v1, -v2]]

    def encode_different(self, t1: str, t2: str) -> List[List[int]]:
        """
        Mã hóa clue DIFFERENT (v1 ⊕ v2):
        (v1 ⊕ v2) ≡ (v1 ∨ v2) ∧ (¬v1 ∨ ¬v2).
        """
        v1 = self.var_map.coord_to_var(t1)
        v2 = self.var_map.coord_to_var(t2)
        return [[v1, v2], [-v1, -v2]]

    def encode_at_most(self, k: int, vars_list: List[int]) -> List[List[int]]:
        """
        Mã hóa trực tiếp sum(vars_list) <= k (AT_MOST k).
        Với mọi tập con kích thước k + 1, phải có ít nhất 1 biến mang giá trị False (-v).
        """
        m = len(vars_list)
        if k < 0:
            return [[]]  # Clause rỗng biểu diễn UNSAT (luôn sai)
        if k >= m:
            return []    # Rỗng biểu diễn Tautology (luôn đúng)

        clauses = []
        for comb in itertools.combinations(vars_list, k + 1):
            clauses.append([-v for v in comb])
        return clauses

    def encode_at_least(self, k: int, vars_list: List[int]) -> List[List[int]]:
        """
        Mã hóa trực tiếp sum(vars_list) >= k (AT_LEAST k).
        Tương đương tối đa (m - k) người Innocent: mọi tập con kích thước m - k + 1
        phải chứa ít nhất 1 biến mang giá trị True (+v).
        """
        m = len(vars_list)
        if k <= 0:
            return []    # Luôn đúng
        if k > m:
            return [[]]  # Vô nghiệm (UNSAT)

        clauses = []
        subset_size = m - k + 1
        for comb in itertools.combinations(vars_list, subset_size):
            clauses.append([v for v in comb])
        return clauses

    def encode_exactly(self, k: int, vars_list: List[int]) -> List[List[int]]:
        """
        Mã hóa sum(vars_list) == k (EXACTLY k):
        Kết hợp đồng thời AT_LEAST(k) và AT_MOST(k), xử lý gọn hai biên k=0 và k=m.
        """
        m = len(vars_list)
        if k < 0 or k > m:
            return [[]]  # Vô nghiệm
        if k == 0:
            return [[-v] for v in vars_list]  # Tất cả là Innocent
        if k == m:
            return [[v] for v in vars_list]   # Tất cả là Criminal

        return self.encode_at_least(k, vars_list) + self.encode_at_most(k, vars_list)

    def encode_parity(self, parity: str, vars_list: List[int]) -> List[List[int]]:
        """
        Mã hóa tính chẵn/lẻ của số Criminal trong vùng (PARITY EVEN/ODD).
        Dùng kỹ thuật Blocking Clauses: duyệt 2^m tổ hợp, mỗi tổ hợp vi phạm
        tính chẵn/lẻ sẽ sinh ra 1 clause phủ định để loại bỏ đúng tổ hợp đó.
        """
        parity_upper = parity.strip().upper()
        if parity_upper not in ('EVEN', 'ODD'):
            raise ValueError(f"Unknown parity: {parity}")

        clauses = []
        target_mod = 0 if parity_upper == 'EVEN' else 1
        m = len(vars_list)
        for bits in itertools.product([0, 1], repeat=m):
            if sum(bits) % 2 != target_mod:
                clause = [
                    -v if b == 1 else v
                    for b, v in zip(bits, vars_list)
                ]
                clauses.append(clause)
        return clauses

    def encode_compare(self, r1_vars: List[int], r2_vars: List[int], op: str) -> List[List[int]]:
        """
        Mã hóa so sánh số Criminal giữa 2 vùng: count(r1) <op> count(r2).
        Lấy hợp các biến của 2 vùng (xử lý được trường hợp 2 vùng giao nhau),
        duyệt mọi tổ hợp bit và sinh blocking clause cho các tổ hợp sai điều kiện.
        """
        if op not in ('>', '<', '=', '==', '>=', '<='):
            raise ValueError(f"Unknown comparison operator: {op}")

        union_vars = sorted(list(set(r1_vars + r2_vars)))
        m = len(union_vars)
        idx_r1 = [union_vars.index(v) for v in r1_vars]
        idx_r2 = [union_vars.index(v) for v in r2_vars]

        def condition_satisfied(c1: int, c2: int) -> bool:
            if op in ('=', '=='):
                return c1 == c2
            elif op == '>':
                return c1 > c2
            elif op == '<':
                return c1 < c2
            elif op == '>=':
                return c1 >= c2
            elif op == '<=':
                return c1 <= c2
            return False

        clauses = []
        for bits in itertools.product([0, 1], repeat=m):
            c1 = sum(bits[i] for i in idx_r1)
            c2 = sum(bits[i] for i in idx_r2)
            if not condition_satisfied(c1, c2):
                clause = [
                    -v if b == 1 else v
                    for b, v in zip(bits, union_vars)
                ]
                clauses.append(clause)
        return clauses

    def encode_clue(self, clue: Clue) -> List[List[int]]:
        """Kiểm tra hợp lệ và chuyển đổi một đối tượng Clue sang danh sách clause CNF."""
        name_map = self.var_map.get_name_to_coord_map()
        validate_clue(clue, self.n, name_map)
        ctype = clue.clue_type.upper()

        if ctype == 'FACT':
            t = clue.params.get("target") or clue.params.get("cell")
            st = clue.params.get("status")
            return self.encode_fact(t, st)

        elif ctype == 'SAME':
            t1 = clue.params.get("target1") or clue.params.get("cell1")
            t2 = clue.params.get("target2") or clue.params.get("cell2")
            return self.encode_same(t1, t2)

        elif ctype == 'DIFFERENT':
            t1 = clue.params.get("target1") or clue.params.get("cell1")
            t2 = clue.params.get("target2") or clue.params.get("cell2")
            return self.encode_different(t1, t2)

        elif ctype in ('EXACTLY', 'AT_LEAST', 'AT_MOST'):
            k = int(clue.params.get("k", 0))
            reg: Region = clue.params["region"]
            cells = reg.resolve(self.n, name_map)
            vars_list = [self.var_map.coord_to_var(c) for c in cells]

            if ctype == 'EXACTLY':
                return self.encode_exactly(k, vars_list)
            elif ctype == 'AT_LEAST':
                return self.encode_at_least(k, vars_list)
            elif ctype == 'AT_MOST':
                return self.encode_at_most(k, vars_list)

        elif ctype == 'PARITY':
            parity = clue.params.get("parity", "EVEN")
            reg: Region = clue.params["region"]
            cells = reg.resolve(self.n, name_map)
            vars_list = [self.var_map.coord_to_var(c) for c in cells]
            return self.encode_parity(parity, vars_list)

        elif ctype == 'COMPARE':
            op = clue.params.get("op", "=")
            r1: Region = clue.params["region1"]
            r2: Region = clue.params["region2"]
            cells1 = r1.resolve(self.n, name_map)
            cells2 = r2.resolve(self.n, name_map)
            v1 = [self.var_map.coord_to_var(c) for c in cells1]
            v2 = [self.var_map.coord_to_var(c) for c in cells2]
            return self.encode_compare(v1, v2, op)

        raise ValueError(f"Cannot encode unknown clue type: {ctype}")

