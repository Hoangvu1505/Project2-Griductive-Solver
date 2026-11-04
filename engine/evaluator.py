"""
Direct semantic evaluator for Griductive clues.
Evaluates whether a clue is satisfied under a complete truth assignment
WITHOUT converting to CNF.
"""

from typing import Dict, List, Optional
from engine.clue import Clue
from engine.region import Region


def evaluate_clue(
    clue: Clue,
    assignment: Dict[str, bool],
    n: int,
    name_to_coord: Optional[Dict[str, str]] = None
) -> bool:
    """
    Evaluates whether a clue evaluates to True given a complete boolean assignment.
    assignment: maps cell coordinate (e.g. 'A1') to bool (True = Criminal, False = Innocent).
    """
    ctype = clue.clue_type.upper()

    def get_val(item: str) -> bool:
        c = item
        if name_to_coord and c in name_to_coord:
            c = name_to_coord[c]
        c = c.upper()
        if c not in assignment:
            raise KeyError(f"Cell '{c}' not found in assignment")
        return assignment[c]

    if ctype == 'FACT':
        target = clue.params.get("target") or clue.params.get("cell")
        expected_status = clue.params.get("status", "").upper()
        expected_val = (expected_status == 'CRIMINAL')
        return get_val(target) == expected_val

    elif ctype == 'SAME':
        t1 = clue.params.get("target1") or clue.params.get("cell1")
        t2 = clue.params.get("target2") or clue.params.get("cell2")
        return get_val(t1) == get_val(t2)

    elif ctype == 'DIFFERENT':
        t1 = clue.params.get("target1") or clue.params.get("cell1")
        t2 = clue.params.get("target2") or clue.params.get("cell2")
        return get_val(t1) != get_val(t2)

    elif ctype in ('EXACTLY', 'AT_LEAST', 'AT_MOST'):
        k = int(clue.params.get("k", 0))
        region: Region = clue.params.get("region")
        if not region:
            raise ValueError(f"Region missing in clue {clue.id}")
        cells = region.resolve(n, name_to_coord)
        criminal_count = sum(1 for c in cells if get_val(c))

        if ctype == 'EXACTLY':
            return criminal_count == k
        elif ctype == 'AT_LEAST':
            return criminal_count >= k
        elif ctype == 'AT_MOST':
            return criminal_count <= k

    elif ctype == 'PARITY':
        parity = clue.params.get("parity", "EVEN").upper()
        region: Region = clue.params.get("region")
        cells = region.resolve(n, name_to_coord)
        criminal_count = sum(1 for c in cells if get_val(c))
        if parity == 'EVEN':
            return (criminal_count % 2) == 0
        elif parity == 'ODD':
            return (criminal_count % 2) == 1
        else:
            raise ValueError(f"Unknown parity: {parity}")

    elif ctype == 'COMPARE':
        r1: Region = clue.params.get("region1")
        r2: Region = clue.params.get("region2")
        op = clue.params.get("op", "=")
        c1 = sum(1 for c in r1.resolve(n, name_to_coord) if get_val(c))
        c2 = sum(1 for c in r2.resolve(n, name_to_coord) if get_val(c))

        if op == '=' or op == '==':
            return c1 == c2
        elif op == '>':
            return c1 > c2
        elif op == '<':
            return c1 < c2
        elif op == '>=':
            return c1 >= c2
        elif op == '<=':
            return c1 <= c2
        else:
            raise ValueError(f"Unknown comparison operator: {op}")

    else:
        raise ValueError(f"Unsupported clue type for direct semantic evaluation: {ctype}")


def evaluate_all(
    clues: List[Clue],
    assignment: Dict[str, bool],
    n: int,
    name_to_coord: Optional[Dict[str, str]] = None
) -> bool:
    """Evaluates whether all given clues are satisfied by the assignment."""
    for clue in clues:
        if not evaluate_clue(clue, assignment, n, name_to_coord):
            return False
    return True

