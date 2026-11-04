"""
Clue definitions and representations for Griductive.
Supports all 6 core clue types plus extensions (PARITY, COMPARE, and advanced regions).
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from engine.region import Region


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
            reg_name = f"{reg.region_type} {reg.param}" if reg.param else reg.region_type
            op_map = {
                'EXACTLY': f"Exactly {k} criminals",
                'AT_LEAST': f"At least {k} criminals",
                'AT_MOST': f"At most {k} criminals"
            }
            return f"{op_map[ctype]} in {reg_name}"

        elif ctype == 'PARITY':
            parity = self.params.get("parity", "EVEN").upper()
            reg = self.params.get("region")
            reg_name = f"{reg.region_type} {reg.param}" if reg.param else reg.region_type
            return f"Criminal count in {reg_name} is {parity}"

        elif ctype == 'COMPARE':
            op = self.params.get("op", "=")
            r1 = self.params.get("region1")
            r2 = self.params.get("region2")
            return f"Criminals in {r1.region_type}({r1.param}) {op} {r2.region_type}({r2.param})"

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

