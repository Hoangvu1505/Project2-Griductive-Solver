"""
Knowledge Base representation for Griductive.
Maintains CNF clauses derived from revealed clues and proved verdicts.
"""

from typing import List, Dict, Optional, Tuple, Set
from engine.clue import Clue
from logic.var_map import VariableMap
from logic.encoder import CNFEncoder


class KnowledgeBase:
    """
    Knowledge base at deduction step t: KB_t = CNF(revealed clues) /\ unit clauses for proved verdicts.
    Strictly excludes hidden statuses and unrevealed clues.
    """

    def __init__(self, var_map: VariableMap, n: int):
        self.var_map = var_map
        self.n = n
        self.encoder = CNFEncoder(var_map, n)
        self.clauses: List[List[int]] = []
        self.revealed_clue_ids: Set[str] = set()
        self.proved_verdicts: Dict[str, str] = {}  # cell_coord -> 'CRIMINAL' | 'INNOCENT'

    def add_clue(self, clue: Clue) -> None:
        """Encodes and appends the clauses for a revealed clue."""
        if clue.id in self.revealed_clue_ids:
            return
        new_clauses = self.encoder.encode_clue(clue)
        self.clauses.extend(new_clauses)
        self.revealed_clue_ids.add(clue.id)

    def add_verdict(self, cell_coord: str, status: str) -> None:
        """Adds a unit clause corresponding to a proved verdict."""
        coord_upper = cell_coord.upper()
        if coord_upper in self.proved_verdicts:
            return
        status_upper = status.upper()
        self.proved_verdicts[coord_upper] = status_upper
        v = self.var_map.coord_to_var(coord_upper)
        literal = v if status_upper == 'CRIMINAL' else -v
        self.clauses.append([literal])

    def get_clauses(self) -> List[List[int]]:
        """Returns a copy of all current clauses."""
        return [list(c) for c in self.clauses]

    def get_stats(self) -> Dict[str, int]:
        """Returns variable and clause statistics."""
        return {
            "num_primary_vars": self.var_map.num_primary,
            "num_aux_vars": self.var_map.num_aux,
            "total_vars": self.var_map.total_vars,
            "num_clauses": len(self.clauses),
            "num_clues": len(self.revealed_clue_ids),
            "num_proved": len(self.proved_verdicts)
        }

    def clone(self) -> "KnowledgeBase":
        """Creates a deep copy of the knowledge base."""
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
    """Factory function to build KB_t from public state."""
    kb = KnowledgeBase(var_map, n)
    for clue in revealed_clues:
        kb.add_clue(clue)
    for coord, status in proved_verdicts.items():
        kb.add_verdict(coord, status)
    return kb

