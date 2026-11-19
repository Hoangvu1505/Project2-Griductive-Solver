"""
Ánh xạ biến mệnh đề xác định cho bài toán Griductive.
Ánh xạ từng nhân vật / ô lưới sang một biến mệnh đề chính (1 đến N^2),
đồng thời quản lý tách biệt tập biến phụ (auxiliary variables).
"""

from typing import Dict, List, Optional
from engine.region import coord_to_rc


class VariableMap:
    """
    Ánh xạ 1-1 xác định giữa tọa độ/tên nhân vật và ID biến SAT (1..N^2).
    C_i = True  <=> nhân vật i là Criminal
    C_i = False <=> nhân vật i là Innocent
    Biến phụ (auxiliary) được cấp phát bắt đầu từ N^2 + 1.
    """

    def __init__(self, cells: List[str], character_names: Optional[Dict[str, str]] = None):
        # 1. Chuẩn hóa in hoa, loại trùng và sắp xếp cố định theo row-major: (row_idx, col_idx)
        unique_cells = {c.strip().upper() for c in cells}
        self.cells: List[str] = sorted(unique_cells, key=coord_to_rc)

        # 2. Tạo bảng ánh xạ hai chiều coord <-> var_id (1-based)
        self._coord_to_var: Dict[str, int] = {}
        self._var_to_coord: Dict[int, str] = {}

        for idx, cell in enumerate(self.cells):
            var_id = idx + 1  # Bắt đầu từ 1 (tránh 0 vì SAT dùng dấu +/- biểu diễn literal)
            self._coord_to_var[cell] = var_id
            self._var_to_coord[var_id] = cell

        # 3. Lưu ánh xạ tên nhân vật <-> tọa độ (ví dụ "Abel" <-> "A1")
        self._name_to_coord: Dict[str, str] = {}
        self._coord_to_name: Dict[str, str] = {}
        if character_names:
            for coord, name in character_names.items():
                cu = coord.strip().upper()
                self._coord_to_name[cu] = name
                self._name_to_coord[name] = cu

        # 4. Quản lý ranh giới biến chính và biến phụ
        self._num_primary: int = len(self.cells)
        self._aux_counter: int = self._num_primary
        self._aux_descriptions: Dict[int, str] = {}

    @property
    def num_primary(self) -> int:
        """Trả về số lượng biến chính (N^2)."""
        return self._num_primary

    @property
    def num_aux(self) -> int:
        """Trả về số lượng biến phụ đã cấp phát."""
        return self._aux_counter - self._num_primary

    @property
    def total_vars(self) -> int:
        """Trả về tổng số biến hiện có (biến chính + biến phụ)."""
        return self._aux_counter

    def is_primary(self, var_id: int) -> bool:
        """Kiểm tra var_id (hoặc literal) có thuộc tập biến chính hay không."""
        return 1 <= abs(var_id) <= self._num_primary

    def coord_to_var(self, coord_or_name: str) -> int:
        """Đổi tọa độ ô hoặc tên nhân vật sang ID biến SAT nguyên dương."""
        item = coord_or_name.strip()
        if item in self._name_to_coord:
            item = self._name_to_coord[item]
        item_upper = item.upper()
        if item_upper not in self._coord_to_var:
            raise KeyError(f"Coordinate/character '{coord_or_name}' not in variable map")
        return self._coord_to_var[item_upper]

    def var_to_coord(self, var_id: int) -> str:
        """Đổi ID biến (hoặc literal âm/dương) về tọa độ ô tương ứng."""
        v = abs(var_id)
        if v not in self._var_to_coord:
            raise KeyError(f"Variable ID {v} is not a primary variable")
        return self._var_to_coord[v]

    def name_to_coord(self, name: str) -> Optional[str]:
        """Tra cứu tọa độ từ tên nhân vật."""
        return self._name_to_coord.get(name)

    def coord_to_name(self, coord: str) -> Optional[str]:
        """Tra cứu tên nhân vật từ tọa độ ô."""
        return self._coord_to_name.get(coord.strip().upper())

    def get_name_to_coord_map(self) -> Dict[str, str]:
        """Trả về bản sao từ điển ánh xạ tên nhân vật -> tọa độ."""
        return dict(self._name_to_coord)

    def alloc_aux_var(self, desc: str = "") -> int:
        """Cấp phát 1 biến phụ mới (> num_primary)."""
        self._aux_counter += 1
        if desc:
            self._aux_descriptions[self._aux_counter] = desc
        return self._aux_counter

    def reset_aux(self) -> None:
        """Đưa bộ đếm biến phụ về lại mốc ban đầu."""
        self._aux_counter = self._num_primary
        self._aux_descriptions.clear()

