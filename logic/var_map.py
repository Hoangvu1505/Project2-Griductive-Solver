"""
Deterministic propositional variable mapping for Griductive.
Maps each character / cell to a primary propositional variable (1 to N^2).
Keeps auxiliary variables distinct and tracked.
"""

from typing import Dict, List, Optional


class VariableMap:
    """
    Manages deterministic bijection between cells/characters and SAT variable IDs (1-based integers).
    Primary variables represent: C_i = True iff character/cell i is Criminal.
    Auxiliary variables are allocated strictly above the primary variable range.
    """

    def __init__(self, cells: List[str], character_names: Optional[Dict[str, str]] = None):
        """
        cells: list of coordinates (e.g. ['A1', 'B1', ...]) in deterministic order.
        character_names: optional dict mapping coord -> character name.
        """
        # Sort cells deterministically if not sorted
        # Griductive order: row-major A1, B1, C1, A2, B2, ...
        self.cells: List[str] = list(cells)
        self._coord_to_var: Dict[str, int] = {}
        self._var_to_coord: Dict[int, str] = {}
        self._name_to_coord: Dict[str, str] = {}
        self._coord_to_name: Dict[str, str] = {}

        for idx, cell in enumerate(self.cells):
            var_id = idx + 1
            cell_upper = cell.upper()
            self._coord_to_var[cell_upper] = var_id
            self._var_to_coord[var_id] = cell_upper

        if character_names:
            for coord, name in character_names.items():
                cu = coord.upper()
                self._coord_to_name[cu] = name
                self._name_to_coord[name] = cu

        self._num_primary: int = len(self.cells)
        self._aux_counter: int = self._num_primary
        self._aux_descriptions: Dict[int, str] = {}

    @property
    def num_primary(self) -> int:
        return self._num_primary

    @property
    def num_aux(self) -> int:
        return self._aux_counter - self._num_primary

    @property
    def total_vars(self) -> int:
        return self._aux_counter

    def is_primary(self, var_id: int) -> bool:
        return 1 <= abs(var_id) <= self._num_primary

    def coord_to_var(self, coord_or_name: str) -> int:
        item = coord_or_name.strip()
        if item in self._name_to_coord:
            item = self._name_to_coord[item]
        item_upper = item.upper()
        if item_upper not in self._coord_to_var:
            raise KeyError(f"Coordinate/character '{coord_or_name}' not in variable map")
        return self._coord_to_var[item_upper]

    def var_to_coord(self, var_id: int) -> str:
        v = abs(var_id)
        if v not in self._var_to_coord:
            raise KeyError(f"Variable ID {v} is not a primary variable")
        return self._var_to_coord[v]

    def name_to_coord(self, name: str) -> Optional[str]:
        return self._name_to_coord.get(name)

    def coord_to_name(self, coord: str) -> Optional[str]:
        return self._coord_to_name.get(coord.upper())

    def get_name_to_coord_map(self) -> Dict[str, str]:
        return dict(self._name_to_coord)

    def alloc_aux_var(self, desc: str = "") -> int:
        """Allocates a fresh auxiliary variable."""
        self._aux_counter += 1
        if desc:
            self._aux_descriptions[self._aux_counter] = desc
        return self._aux_counter

    def reset_aux(self) -> None:
        """Resets the auxiliary variable counter back to primary."""
        self._aux_counter = self._num_primary
        self._aux_descriptions.clear()

