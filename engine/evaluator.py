"""
Direct semantic evaluator for Griductive clues.
Evaluates whether a clue is satisfied under a complete truth assignment
WITHOUT converting to CNF.

It also provides a brute-force solver (find_all_solutions) built on the same
semantics. Because it never touches the CNF encoder or the DPLL solver, it is an
independent oracle for checking that a puzzle has a unique solution and that the
SAT-based pipeline agrees with the plain meaning of the clues.
"""

import random
from typing import Callable, Dict, List, Optional
from engine.clue import Clue, VALID_STATUSES
from engine.region import Region, get_all_cells


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
        expected_status = str(clue.params.get("status", "")).upper()
        if expected_status not in VALID_STATUSES:
            raise ValueError(f"FACT status must be CRIMINAL or INNOCENT in clue {clue.id}, got '{expected_status}'")
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
        if not region:
            raise ValueError(f"Region missing in clue {clue.id}")
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
        if not r1 or not r2:
            raise ValueError(f"region1/region2 missing in clue {clue.id}")
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


# ----------------------------------------------------------------------------
# Brute-force solver
# ----------------------------------------------------------------------------
# An assignment is packed into an int: bit i is 1 <=> get_all_cells(n)[i] is CRIMINAL.
# Each clue is compiled once into a predicate on that int, so enumerating all
# 2^(n*n) assignments stays affordable (5x5 = 33.5M assignments, pure Python).

def _popcount(x: int) -> int:
    return x.bit_count() if hasattr(x, "bit_count") else bin(x).count("1")


def compile_clue(
    clue: Clue,
    n: int,
    name_to_coord: Optional[Dict[str, str]] = None
) -> Callable[[int], bool]:
    """
    Compiles a clue into a predicate over packed assignments (see above).
    Semantics are identical to evaluate_clue (checked by verify_compiled_matches_evaluator).
    """
    ctype = clue.clue_type.upper()
    bit_of = {c: 1 << i for i, c in enumerate(get_all_cells(n))}

    def bit(item: str) -> int:
        c = name_to_coord.get(item, item) if name_to_coord else item
        c = c.upper()
        if c not in bit_of:
            raise KeyError(f"Cell '{c}' not found on the {n}x{n} board (clue {clue.id})")
        return bit_of[c]

    def mask(region: Region) -> int:
        m = 0
        for c in region.resolve(n, name_to_coord):
            m |= bit(c)
        return m

    if ctype == 'FACT':
        b = bit(clue.params.get("target") or clue.params.get("cell"))
        status = str(clue.params.get("status", "")).upper()
        if status not in VALID_STATUSES:
            raise ValueError(f"FACT status must be CRIMINAL or INNOCENT in clue {clue.id}, got '{status}'")
        want = (status == 'CRIMINAL')
        return lambda x: bool(x & b) == want

    if ctype in ('SAME', 'DIFFERENT'):
        b1 = bit(clue.params.get("target1") or clue.params.get("cell1"))
        b2 = bit(clue.params.get("target2") or clue.params.get("cell2"))
        if ctype == 'SAME':
            return lambda x: bool(x & b1) == bool(x & b2)
        return lambda x: bool(x & b1) != bool(x & b2)

    if ctype in ('EXACTLY', 'AT_LEAST', 'AT_MOST'):
        k = int(clue.params.get("k", 0))
        region = clue.params.get("region")
        if not region:
            raise ValueError(f"Region missing in clue {clue.id}")
        m = mask(region)
        if ctype == 'EXACTLY':
            return lambda x: _popcount(x & m) == k
        if ctype == 'AT_LEAST':
            return lambda x: _popcount(x & m) >= k
        return lambda x: _popcount(x & m) <= k

    if ctype == 'PARITY':
        region = clue.params.get("region")
        if not region:
            raise ValueError(f"Region missing in clue {clue.id}")
        parity = str(clue.params.get("parity", "EVEN")).upper()
        if parity not in ('EVEN', 'ODD'):
            raise ValueError(f"Unknown parity: {parity}")
        m = mask(region)
        want = 0 if parity == 'EVEN' else 1
        return lambda x: (_popcount(x & m) & 1) == want

    if ctype == 'COMPARE':
        r1, r2 = clue.params.get("region1"), clue.params.get("region2")
        if not r1 or not r2:
            raise ValueError(f"region1/region2 missing in clue {clue.id}")
        op = clue.params.get("op", "=")
        m1, m2 = mask(r1), mask(r2)
        cmp_ops = {
            '=': lambda a, b: a == b, '==': lambda a, b: a == b,
            '>': lambda a, b: a > b, '<': lambda a, b: a < b,
            '>=': lambda a, b: a >= b, '<=': lambda a, b: a <= b,
        }
        if op not in cmp_ops:
            raise ValueError(f"Unknown comparison operator: {op}")
        f = cmp_ops[op]
        return lambda x: f(_popcount(x & m1), _popcount(x & m2))

    raise ValueError(f"Unsupported clue type for direct semantic evaluation: {ctype}")


def _unpack(x: int, cells: List[str]) -> Dict[str, bool]:
    return {c: bool((x >> i) & 1) for i, c in enumerate(cells)}


def verify_compiled_matches_evaluator(
    clues: List[Clue],
    n: int,
    name_to_coord: Optional[Dict[str, str]] = None,
    samples: int = 1000,
    seed: int = 0
) -> bool:
    """
    Cross-checks every compiled predicate against evaluate_clue on random assignments.
    Returns True if they agree everywhere; raises AssertionError describing the first mismatch.
    """
    rng = random.Random(seed)
    cells = get_all_cells(n)
    compiled = [(c, compile_clue(c, n, name_to_coord)) for c in clues]
    for _ in range(samples):
        x = rng.getrandbits(len(cells))
        assignment = _unpack(x, cells)
        for clue, pred in compiled:
            if pred(x) != evaluate_clue(clue, assignment, n, name_to_coord):
                raise AssertionError(f"compile_clue disagrees with evaluate_clue on {clue.id} (assignment {x:#x})")
    return True


def find_all_solutions(
    clues: List[Clue],
    n: int,
    name_to_coord: Optional[Dict[str, str]] = None,
    limit: Optional[int] = None,
    selfcheck: bool = True
) -> List[Dict[str, bool]]:
    """
    Brute force: tries all 2^(n*n) assignments and returns every one that satisfies ALL clues,
    as {coord: is_criminal} dicts. A puzzle is uniquely solvable iff exactly one is returned.

    limit: stop as soon as this many solutions are found (limit=2 is enough to refute uniqueness).
    selfcheck: first cross-check the compiled predicates against evaluate_clue.
    Cost (CPython 3.12): well under 1s for 3x3 / 4x4, about 7s for 5x5.
    """
    cells = get_all_cells(n)
    if selfcheck:
        verify_compiled_matches_evaluator(clues, n, name_to_coord)

    preds = [compile_clue(c, n, name_to_coord) for c in clues]

    # Most selective clue first (estimated on a random sample) so most assignments fail on the first test.
    rng = random.Random(1)
    sample = [rng.getrandbits(len(cells)) for _ in range(512)]
    preds.sort(key=lambda p: sum(1 for x in sample if p(x)))

    solutions: List[Dict[str, bool]] = []
    for x in range(1 << len(cells)):
        for p in preds:
            if not p(x):
                break
        else:
            solutions.append(_unpack(x, cells))
            if limit is not None and len(solutions) >= limit:
                break
    return solutions