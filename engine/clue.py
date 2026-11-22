"""
Clue definitions and representations for Griductive.
Supports all 6 core clue types plus extensions (PARITY, COMPARE, and advanced regions).
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from engine.region import Region, get_all_cells

SUPPORTED_CLUE_TYPES = ('FACT', 'SAME', 'DIFFERENT', 'EXACTLY', 'AT_LEAST', 'AT_MOST', 'PARITY', 'COMPARE')
VALID_STATUSES = ('CRIMINAL', 'INNOCENT')
VALID_PARITIES = ('EVEN', 'ODD')
VALID_COMPARE_OPS = ('=', '==', '>', '<', '>=', '<=')


def describe_region(region: Region) -> str:
    """Short human-readable label of a region, used by Clue.get_display_text."""
    rtype = region.region_type.upper()
    p = region.param
    if rtype == 'ROW':
        return f"row {p}"
    if rtype in ('COL', 'COLUMN'):
        return f"column {str(p).upper()}"
    if rtype == 'NEIGHBORS':
        return f"the neighbors of {p}"
    if rtype == 'CORNERS':
        return "the 4 corners"
    if rtype == 'BOUNDARY':
        return "the boundary"
    if rtype == 'EXPLICIT':
        return "{" + ", ".join(str(c) for c in p) + "}"
    if rtype == 'BETWEEN':
        return f"the cells between {p[0]} and {p[1]}"
    if rtype == 'COMMON_NEIGHBORS':
        return f"the common neighbors of {p[0]} and {p[1]}"
    return f"{rtype} {p}" if p is not None else rtype


@dataclass
class Clue:
    """
    Represents a structured clue in Griductive.
    Fields:
    - id: Unique clue identifier (e.g., 'clue_A1')
    - clue_type: FACT, SAME, DIFFERENT, EXACTLY, AT_LEAST, AT_MOST, PARITY, COMPARE
    - params: Parameters specific to the clue type
    - owner: The cell coordinate (or character name) that holds this clue
    - text: Optional natural-language text representation for GUI display
    """
    id: str
    clue_type: str
    params: Dict[str, Any]
    owner: str = ""
    text: str = ""

    def __post_init__(self):
        self.clue_type = self.clue_type.upper()
        # Convert raw region dicts/strings to Region objects inside params if applicable
        if "region" in self.params and not isinstance(self.params["region"], Region):
            self.params["region"] = Region.from_dict(self.params["region"])
        if "region1" in self.params and not isinstance(self.params["region1"], Region):
            self.params["region1"] = Region.from_dict(self.params["region1"])
        if "region2" in self.params and not isinstance(self.params["region2"], Region):
            self.params["region2"] = Region.from_dict(self.params["region2"])

    def validate(self, n: int, name_to_coord: Optional[Dict[str, str]] = None) -> None:
        """
        Checks that the clue is well-formed for an n x n board.
        Raises ValueError (message starts with the clue id) on the first problem:
        unknown clue type, missing/invalid params, cells outside the grid,
        k out of range, unknown status / parity / comparison operator.
        """
        cid = self.id or "<no id>"
        ctype = self.clue_type
        if ctype not in SUPPORTED_CLUE_TYPES:
            raise ValueError(f"{cid}: unsupported clue_type '{ctype}'")

        grid = set(get_all_cells(n))

        def cell_param(*keys: str) -> str:
            for k in keys:
                v = self.params.get(k)
                if v:
                    v = name_to_coord.get(v, v) if name_to_coord else v
                    v = str(v).upper()
                    if v not in grid:
                        raise ValueError(f"{cid}: cell '{v}' is outside the {n}x{n} grid")
                    return v
            raise ValueError(f"{cid}: missing parameter {' / '.join(keys)} for {ctype}")

        def region_param(key: str) -> List[str]:
            reg = self.params.get(key)
            if not isinstance(reg, Region):
                raise ValueError(f"{cid}: missing parameter '{key}' for {ctype}")
            try:
                cells = reg.resolve(n, name_to_coord)
            except (ValueError, KeyError, IndexError, TypeError) as e:
                raise ValueError(f"{cid}: invalid {key} ({reg.region_type}, {reg.param}): {e}") from e
            if not set(cells) <= grid:
                raise ValueError(f"{cid}: {key} contains cells outside the {n}x{n} grid")
            return cells

        if ctype == 'FACT':
            cell_param("target", "cell")
            status = str(self.params.get("status", "")).upper()
            if status not in VALID_STATUSES:
                raise ValueError(f"{cid}: FACT status must be CRIMINAL or INNOCENT, got '{status}'")

        elif ctype in ('SAME', 'DIFFERENT'):
            a = cell_param("target1", "cell1")
            b = cell_param("target2", "cell2")
            if a == b:
                raise ValueError(f"{cid}: {ctype} compares {a} with itself")

        elif ctype in ('EXACTLY', 'AT_LEAST', 'AT_MOST'):
            cells = region_param("region")
            try:
                k = int(self.params.get("k"))
            except (TypeError, ValueError):
                raise ValueError(f"{cid}: k must be an integer, got {self.params.get('k')!r}")
            if k < 0:
                raise ValueError(f"{cid}: k must be >= 0, got {k}")
            if ctype in ('EXACTLY', 'AT_LEAST') and k > len(cells):
                raise ValueError(f"{cid}: {ctype} {k} is impossible, region has only {len(cells)} cells")

        elif ctype == 'PARITY':
            region_param("region")
            parity = str(self.params.get("parity", "")).upper()
            if parity not in VALID_PARITIES:
                raise ValueError(f"{cid}: parity must be EVEN or ODD, got '{parity}'")

        elif ctype == 'COMPARE':
            region_param("region1")
            region_param("region2")
            op = self.params.get("op", "=")
            if op not in VALID_COMPARE_OPS:
                raise ValueError(f"{cid}: unknown comparison operator '{op}'")

    def get_referenced_cells(self, n: int, name_to_coord: Optional[Dict[str, str]] = None) -> List[str]:
        """
        Returns all grid cell coordinates referenced or counted by this clue.
        Used by the GUI to visually highlight cells when a clue is selected.
        """
        ctype = self.clue_type
        cells: List[str] = []

        if ctype == 'FACT':
            t = self.params.get("target") or self.params.get("cell")
            if t:
                if name_to_coord and t in name_to_coord:
                    t = name_to_coord[t]
                cells.append(t.upper())

        elif ctype in ('SAME', 'DIFFERENT'):
            t1 = self.params.get("target1") or self.params.get("cell1")
            t2 = self.params.get("target2") or self.params.get("cell2")
            for t in (t1, t2):
                if t:
                    if name_to_coord and t in name_to_coord:
                        t = name_to_coord[t]
                    cells.append(t.upper())

        elif ctype in ('EXACTLY', 'AT_LEAST', 'AT_MOST', 'PARITY'):
            region: Region = self.params.get("region")
            if region:
                cells.extend(region.resolve(n, name_to_coord))

        elif ctype == 'COMPARE':
            r1: Region = self.params.get("region1")
            r2: Region = self.params.get("region2")
            if r1:
                cells.extend(r1.resolve(n, name_to_coord))
            if r2:
                cells.extend(r2.resolve(n, name_to_coord))

        # Return unique sorted coordinates
        return sorted(list(set(cells)))

    def get_display_text(self, n: int = 3, name_to_coord: Optional[Dict[str, str]] = None) -> str:
        """Returns a human-readable text description of the clue."""
        if self.text:
            return self.text

        ctype = self.clue_type
        if ctype == 'FACT':
            t = self.params.get("target") or self.params.get("cell")
            st = self.params.get("status", "").upper()
            return f"{t} is {st}"

        elif ctype == 'SAME':
            t1 = self.params.get("target1") or self.params.get("cell1")
            t2 = self.params.get("target2") or self.params.get("cell2")
            return f"{t1} and {t2} have the SAME status"

        elif ctype == 'DIFFERENT':
            t1 = self.params.get("target1") or self.params.get("cell1")
            t2 = self.params.get("target2") or self.params.get("cell2")
            return f"{t1} and {t2} have DIFFERENT statuses"

        elif ctype in ('EXACTLY', 'AT_LEAST', 'AT_MOST'):
            k = self.params.get("k", 0)
            reg = self.params.get("region")
            reg_name = describe_region(reg)
            op_map = {
                'EXACTLY': f"Exactly {k} criminals",
                'AT_LEAST': f"At least {k} criminals",
                'AT_MOST': f"At most {k} criminals"
            }
            return f"{op_map[ctype]} in {reg_name}"

        elif ctype == 'PARITY':
            parity = self.params.get("parity", "EVEN").upper()
            reg = self.params.get("region")
            reg_name = describe_region(reg)
            return f"Criminal count in {reg_name} is {parity}"

        elif ctype == 'COMPARE':
            op = self.params.get("op", "=")
            r1 = self.params.get("region1")
            r2 = self.params.get("region2")
            return f"Criminals in {describe_region(r1)} {op} criminals in {describe_region(r2)}"

        return f"{ctype}: {self.params}"

    def to_dict(self) -> Dict[str, Any]:
        params_dict = {}
        for k, v in self.params.items():
            if isinstance(v, Region):
                params_dict[k] = v.to_dict()
            else:
                params_dict[k] = v
        return {
            "id": self.id,
            "clue_type": self.clue_type,
            "params": params_dict,
            "owner": self.owner,
            "text": self.text
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Clue":
        return cls(
            id=data.get("id", ""),
            clue_type=data["clue_type"],
            params=dict(data.get("params", {})),
            owner=data.get("owner", ""),
            text=data.get("text", "")
        )