"""
Region definitions and resolution for Griductive.
Defines coordinate conversions, region types, and methods to resolve regions to cell lists.
"""

from typing import List, Tuple, Set, Optional, Dict, Any
from dataclasses import dataclass, field


def col_letter_to_index(letter: str) -> int:
    """Converts a column letter ('A', 'B', ...) to 0-based column index."""
    return ord(letter.upper()) - ord('A')


def index_to_col_letter(idx: int) -> str:
    """Converts a 0-based column index to letter ('A', 'B', ...)."""
    return chr(ord('A') + idx)


def coord_to_rc(coord: str) -> Tuple[int, int]:
    """
    Converts coordinate string like 'C2' or 'A1' to (row_idx, col_idx).
    Rows in Griductive are 1-based (top to bottom).
    Columns are letters A..Z (left to right).
    'C2' means Column C (index 2), Row 2 (index 1).
    """
    coord = coord.strip().upper()
    col_str = coord[0]
    row_str = coord[1:]
    col_idx = col_letter_to_index(col_str)
    row_idx = int(row_str) - 1
    return row_idx, col_idx


def rc_to_coord(row_idx: int, col_idx: int) -> str:
    """Converts (row_idx, col_idx) to coordinate string like 'C2'."""
    col_letter = index_to_col_letter(col_idx)
    return f"{col_letter}{row_idx + 1}"


def get_all_cells(n: int) -> List[str]:
    """Returns all cell coordinates in row-major order for an n x n grid."""
    cells = []
    for r in range(n):
        for c in range(n):
            cells.append(rc_to_coord(r, c))
    return cells


def get_neighbors(coord: str, n: int) -> List[str]:
    """
    Returns 8-neighbors of a cell (horizontal, vertical, diagonal).
    Excludes the cell itself. Boundaries are respected.
    """
    r, c = coord_to_rc(coord)
    neighbors = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n:
                neighbors.append(rc_to_coord(nr, nc))
    neighbors.sort()
    return neighbors


@dataclass
class Region:
    """
    Represents a region on the Griductive board.
    Supported types:
    - 'ROW': param is int (1-based row number)
    - 'COL': param is str (column letter 'A', 'B', ...)
    - 'NEIGHBORS': param is str (cell coord, e.g. 'B2')
    - 'EXPLICIT': param is list of cell coords, e.g. ['A1', 'B2']
    - 'CORNERS': param is None or dict (the 4 corner cells)
    - 'BOUNDARY': all outer cells
    - 'BETWEEN': param is tuple of two coords (cells strictly between them)
    - 'COMMON_NEIGHBORS': param is tuple of two coords
    """
    region_type: str
    param: Any = None

    def resolve(self, n: int, name_to_coord: Optional[Dict[str, str]] = None) -> List[str]:
        """
        Resolves the region into a sorted list of unique cell coordinates.
        Optional name_to_coord mapping allows referencing cells by character name.
        """
        rtype = self.region_type.upper()

        if rtype == 'ROW':
            row_num = int(self.param)
            r_idx = row_num - 1
            if not (0 <= r_idx < n):
                raise ValueError(f"Row {row_num} out of bounds for {n}x{n} grid")
            return [rc_to_coord(r_idx, c) for c in range(n)]

        elif rtype == 'COL' or rtype == 'COLUMN':
            col_letter = str(self.param).upper()
            c_idx = col_letter_to_index(col_letter)
            if not (0 <= c_idx < n):
                raise ValueError(f"Column {col_letter} out of bounds for {n}x{n} grid")
            return [rc_to_coord(r, c_idx) for r in range(n)]

        elif rtype == 'NEIGHBORS':
            coord = str(self.param)
            if name_to_coord and coord in name_to_coord:
                coord = name_to_coord[coord]
            return get_neighbors(coord, n)

        elif rtype == 'EXPLICIT':
            cells = []
            for item in self.param:
                c = str(item)
                if name_to_coord and c in name_to_coord:
                    c = name_to_coord[c]
                cells.append(c.upper())
            return sorted(list(set(cells)))

        elif rtype == 'CORNERS':
            corners = [
                rc_to_coord(0, 0),
                rc_to_coord(0, n - 1),
                rc_to_coord(n - 1, 0),
                rc_to_coord(n - 1, n - 1),
            ]
            return sorted(list(set(corners)))

        elif rtype == 'BOUNDARY':
            boundary_set = set()
            for r in range(n):
                for c in range(n):
                    if r == 0 or r == n - 1 or c == 0 or c == n - 1:
                        boundary_set.add(rc_to_coord(r, c))
            return sorted(list(boundary_set))

        elif rtype == 'COMMON_NEIGHBORS':
            c1, c2 = self.param
            if name_to_coord:
                c1 = name_to_coord.get(c1, c1)
                c2 = name_to_coord.get(c2, c2)
            n1 = set(get_neighbors(c1, n))
            n2 = set(get_neighbors(c2, n))
            return sorted(list(n1.intersection(n2)))

        elif rtype == 'BETWEEN':
            c1, c2 = self.param
            if name_to_coord:
                c1 = name_to_coord.get(c1, c1)
                c2 = name_to_coord.get(c2, c2)
            r1, col1 = coord_to_rc(c1)
            r2, col2 = coord_to_rc(c2)
            dr = r2 - r1
            dc = col2 - col1
            step_r = 0 if dr == 0 else (1 if dr > 0 else -1)
            step_c = 0 if dc == 0 else (1 if dc > 0 else -1)

            # Check if collinear (horizontal, vertical, or 45-degree diagonal)
            if dr == 0 or dc == 0 or abs(dr) == abs(dc):
                curr_r, curr_c = r1 + step_r, col1 + step_c
                between_cells = []
                while (curr_r, curr_c) != (r2, col2):
                    between_cells.append(rc_to_coord(curr_r, curr_c))
                    curr_r += step_r
                    curr_c += step_c
                return sorted(between_cells)
            else:
                return []

        else:
            raise ValueError(f"Unknown region type: {self.region_type}")

    def to_dict(self) -> Dict[str, Any]:
        return {"region_type": self.region_type, "param": self.param}

    @classmethod
    def from_dict(cls, data: Any) -> "Region":
        if isinstance(data, dict):
            return cls(region_type=data["region_type"], param=data.get("param"))
        elif isinstance(data, str):
            # Shortcut parser: "row:2", "col:B", "neighbors:A1", "corners"
            parts = data.split(":", 1)
            rtype = parts[0].upper()
            param = parts[1] if len(parts) > 1 else None
            return cls(region_type=rtype, param=param)
        elif isinstance(data, list):
            return cls(region_type="EXPLICIT", param=data)
        raise ValueError(f"Cannot construct Region from {data}")

