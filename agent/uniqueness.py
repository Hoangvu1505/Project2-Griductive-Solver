"""
Uniqueness checker for Griductive puzzle complete clue set.
Verifies whether the complete clue set has exactly ONE satisfying assignment.
Uses DPLL with blocking clauses, and includes an independent brute-force check.
"""

from typing import List, Dict, Tuple, Optional
import itertools
from engine.clue import Clue
from engine.region import get_all_cells
from engine.evaluator import evaluate_all
from logic.var_map import VariableMap
from logic.encoder import CNFEncoder
from sat.dpll import DPLLSolver


def check_uniqueness_dpll(
    all_clues: List[Clue],
    var_map: VariableMap,
    n: int
) -> Tuple[bool, str, List[Dict[str, str]]]:
    """
    Checks if all clues combined produce exactly one unique truth assignment using DPLL.
    Returns:
        (is_unique: bool, message: str, models: List[Dict[cell_coord, 'CRIMINAL'|'INNOCENT']])
    """
    encoder = CNFEncoder(var_map, n)
    clauses: List[List[int]] = []
    for clue in all_clues:
        clauses.extend(encoder.encode_clue(clue))

    solver = DPLLSolver()
    # Find Model 1
    is_sat1, model1, _ = solver.solve(clauses, num_vars=var_map.total_vars)
    if not is_sat1 or model1 is None:
        return False, "Puzzle has 0 solutions (UNSAT / Inconsistent)", []

    # Map model 1 to cell statuses
    sol1 = {}
    for cell in var_map.cells:
        v = var_map.coord_to_var(cell)
        sol1[cell] = "CRIMINAL" if model1[v] else "INNOCENT"

    # Create blocking clause for primary variables to exclude Model 1
    blocking_clause = []
    for cell in var_map.cells:
        v = var_map.coord_to_var(cell)
        if model1[v]:
            blocking_clause.append(-v)
        else:
            blocking_clause.append(v)

    clauses_with_block = [list(c) for c in clauses]
    clauses_with_block.append(blocking_clause)

    # Search for Model 2
    is_sat2, model2, _ = solver.solve(clauses_with_block, num_vars=var_map.total_vars)
    if not is_sat2:
        return True, "Puzzle has exactly ONE unique solution", [sol1]

    sol2 = {}
    for cell in var_map.cells:
        v = var_map.coord_to_var(cell)
        sol2[cell] = "CRIMINAL" if model2[v] else "INNOCENT"

    return False, "Puzzle has MULTIPLE solutions (Ambiguous)", [sol1, sol2]


def check_uniqueness_brute_force(
    all_clues: List[Clue],
    n: int,
    name_to_coord: Optional[Dict[str, str]] = None,
    max_search_limit: int = 65536
) -> Tuple[bool, int, List[Dict[str, str]]]:
    """
    Independent brute-force check over all 2^(n^2) assignments using the direct semantic evaluator.
    Suitable for 3x3 (512 states) and 4x4 (65536 states).
    """
    cells = get_all_cells(n)
    total_assignments = 1 << len(cells)
    if total_assignments > max_search_limit:
        return False, -1, []  # Search space too large for direct brute-force

    valid_solutions: List[Dict[str, str]] = []

    for bits in itertools.product([False, True], repeat=len(cells)):
        assignment = {cell: bits[i] for i, cell in enumerate(cells)}
        if evaluate_all(all_clues, assignment, n, name_to_coord):
            sol = {c: "CRIMINAL" if assignment[c] else "INNOCENT" for c in cells}
            valid_solutions.append(sol)
            if len(valid_solutions) > 1:
                # Early stop if more than 1 solution found
                return False, len(valid_solutions), valid_solutions

    is_unique = (len(valid_solutions) == 1)
    return is_unique, len(valid_solutions), valid_solutions

