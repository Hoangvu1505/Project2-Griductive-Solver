"""
Quản lý Cơ sở tri thức (Knowledge Base) cho bài toán Griductive.
Lưu trữ các mệnh đề CNF sinh ra từ manh mối đã lật và các phán quyết đã chứng minh.
"""

from typing import List, Dict, Set
from engine.clue import Clue
from logic.var_map import VariableMap
from logic.encoder import CNFEncoder


class KnowledgeBase:
    """
    Cơ sở tri thức tại bước suy diễn t: KB_t = CNF(revealed clues) ∧ unit clauses(proved verdicts).
    Tuyệt đối không chứa trạng thái ẩn hay manh mối chưa được lật.
    """

    def __init__(self, var_map: VariableMap, n: int):
        """Khởi tạo Knowledge Base rỗng cho lưới n x n với ánh xạ biến var_map."""
        self.var_map = var_map
        self.n = n
        self.encoder = CNFEncoder(var_map, n)
        self.clauses: List[List[int]] = []
        self.revealed_clue_ids: Set[str] = set()
        self.proved_verdicts: Dict[str, str] = {}  # coord -> 'CRIMINAL' | 'INNOCENT'

    def add_clue(self, clue: Clue) -> None:
        """Mã hóa 1 clue đã lật sang CNF và thêm vào KB (bỏ qua nếu đã tồn tại)."""
        if clue.id in self.revealed_clue_ids:
            return
        new_clauses = self.encoder.encode_clue(clue)
        self.clauses.extend(new_clauses)
        self.revealed_clue_ids.add(clue.id)

    def add_verdict(self, cell_coord: str, status: str) -> None:
        """Thêm unit clause cho một nhân vật đã biết/đã chứng minh trạng thái."""
        status_upper = status.strip().upper()
        if status_upper not in ('CRIMINAL', 'INNOCENT'):
            raise ValueError(f"Invalid verdict status '{status}' for '{cell_coord}'")

        v = self.var_map.coord_to_var(cell_coord)
        coord_upper = self.var_map.var_to_coord(v)

        if coord_upper in self.proved_verdicts:
            if self.proved_verdicts[coord_upper] != status_upper:
                raise ValueError(
                    f"Conflicting verdict for {coord_upper}: "
                    f"already {self.proved_verdicts[coord_upper]}, got {status_upper}"
                )
            return

        self.proved_verdicts[coord_upper] = status_upper
        literal = v if status_upper == 'CRIMINAL' else -v
        self.clauses.append([literal])

    def get_clauses(self) -> List[List[int]]:
        """Trả về bản sao danh sách clause hiện có để tránh bị sửa nhầm bên ngoài."""
        return [list(c) for c in self.clauses]

    def get_stats(self) -> Dict[str, int]:
        """Thống kê số biến chính, biến phụ, tổng biến, số clause, số clue và verdict."""
        return {
            "num_primary_vars": self.var_map.num_primary,
            "num_aux_vars": self.var_map.num_aux,
            "total_vars": self.var_map.total_vars,
            "num_clauses": len(self.clauses),
            "num_clues": len(self.revealed_clue_ids),
            "num_proved": len(self.proved_verdicts),
        }

    def clone(self) -> "KnowledgeBase":
        """Tạo một bản sao độc lập của KnowledgeBase hiện tại."""
        cloned = KnowledgeBase(self.var_map, self.n)
        cloned.clauses = [list(c) for c in self.clauses]
        cloned.revealed_clue_ids = set(self.revealed_clue_ids)
        cloned.proved_verdicts = dict(self.proved_verdicts)
        return cloned


def build_kb(
    revealed_clues: List[Clue],
    proved_verdicts: Dict[str, str],
    var_map: VariableMap,
    n: int
) -> KnowledgeBase:
    """
    Hàm factory xây dựng KB_t tại bước suy diễn t chỉ từ trạng thái công khai:
    KB_t = CNF(revealed_clues) ∧ unit clauses(proved_verdicts).
    """
    kb = KnowledgeBase(var_map, n)
    for clue in revealed_clues:
        kb.add_clue(clue)
    for coord, status in proved_verdicts.items():
        kb.add_verdict(coord, status)
    return kb

