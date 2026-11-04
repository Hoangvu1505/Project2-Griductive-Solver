"""
Unit tests comparing CNF Encoder with Direct Semantic Evaluator.
Performs brute-force equivalence verification across all 2^k truth assignments
for every clue template (FACT, SAME, DIFFERENT, EXACTLY, AT_LEAST, AT_MOST, PARITY, COMPARE).
"""

import unittest
import itertools
from typing import List, Dict
from engine.region import Region, get_all_cells
from engine.clue import Clue
from engine.evaluator import evaluate_clue
from logic.var_map import VariableMap
from logic.encoder import CNFEncoder


def check_cnf_satisfaction(clauses: List[List[int]], assignment: Dict[int, bool]) -> bool:
    """Evaluates whether all clauses are satisfied by a truth assignment."""
    for clause in clauses:
        clause_satisfied = False
        for lit in clause:
            var = abs(lit)
            val = assignment.get(var, False)
            if (lit > 0 and val) or (lit < 0 and not val):
                clause_satisfied = True
                break
        if not clause_satisfied:
            return False
    return True


class TestEncoderVsEvaluator(unittest.TestCase):

    def setUp(self):
        self.n = 3
        self.cells = get_all_cells(self.n)
        self.var_map = VariableMap(self.cells)
        self.encoder = CNFEncoder(self.var_map, self.n)

    def _verify_clue_equivalence(self, clue: Clue, relevant_cells: List[str]):
        """
        Brute-force check:
        For every 2^k boolean assignment to relevant_cells,
        semantic evaluator result == CNF satisfaction result.
        """
        clauses = self.encoder.encode_clue(clue)
        num_cells = len(relevant_cells)

        for bits in itertools.product([False, True], repeat=num_cells):
            # Construct cell assignment
            cell_assignment = {cell: bits[i] for i, cell in enumerate(relevant_cells)}
            # Also fill remaining grid cells as False
            full_assignment = {c: False for c in self.cells}
            full_assignment.update(cell_assignment)

            # Map to var assignment
            var_assignment = {self.var_map.coord_to_var(c): full_assignment[c] for c in self.cells}

            eval_res = evaluate_clue(clue, full_assignment, self.n)
            cnf_res = check_cnf_satisfaction(clauses, var_assignment)

            self.assertEqual(
                eval_res, cnf_res,
                f"Mismatch for clue {clue.clue_type} with assignment {cell_assignment}: eval={eval_res}, cnf={cnf_res}"
            )

    def test_fact_criminal(self):
        clue = Clue(id="c1", clue_type="FACT", params={"target": "A1", "status": "CRIMINAL"})
        self._verify_clue_equivalence(clue, ["A1"])

    def test_fact_innocent(self):
        clue = Clue(id="c2", clue_type="FACT", params={"target": "B2", "status": "INNOCENT"})
        self._verify_clue_equivalence(clue, ["B2"])

    def test_same(self):
        clue = Clue(id="c3", clue_type="SAME", params={"target1": "A1", "target2": "B2"})
        self._verify_clue_equivalence(clue, ["A1", "B2"])

    def test_different(self):
        clue = Clue(id="c4", clue_type="DIFFERENT", params={"target1": "A1", "target2": "B2"})
        self._verify_clue_equivalence(clue, ["A1", "B2"])

    def test_exactly_row(self):
        region = Region(region_type="ROW", param=1)  # A1, B1, C1
        for k in range(0, 4):
            clue = Clue(id=f"c_ex_{k}", clue_type="EXACTLY", params={"k": k, "region": region})
            self._verify_clue_equivalence(clue, ["A1", "B1", "C1"])

    def test_at_least_col(self):
        region = Region(region_type="COL", param="B")  # B1, B2, B3
        for k in range(0, 4):
            clue = Clue(id=f"c_al_{k}", clue_type="AT_LEAST", params={"k": k, "region": region})
            self._verify_clue_equivalence(clue, ["B1", "B2", "B3"])

    def test_at_most_neighbors(self):
        region = Region(region_type="NEIGHBORS", param="A1")  # B1, A2, B2 (3 cells)
        for k in range(0, 4):
            clue = Clue(id=f"c_am_{k}", clue_type="AT_MOST", params={"k": k, "region": region})
            self._verify_clue_equivalence(clue, region.resolve(self.n))

    def test_parity_even_and_odd(self):
        region = Region(region_type="ROW", param=2)  # A2, B2, C2
        for parity in ("EVEN", "ODD"):
            clue = Clue(id=f"c_par_{parity}", clue_type="PARITY", params={"parity": parity, "region": region})
            self._verify_clue_equivalence(clue, ["A2", "B2", "C2"])

    def test_compare_regions(self):
        r1 = Region(region_type="EXPLICIT", param=["A1", "A2"])
        r2 = Region(region_type="EXPLICIT", param=["B1", "B2"])
        for op in (">", "<", "="):
            clue = Clue(id=f"c_cmp_{op}", clue_type="COMPARE", params={"region1": r1, "region2": r2, "op": op})
            self._verify_clue_equivalence(clue, ["A1", "A2", "B1", "B2"])


if __name__ == "__main__":
    unittest.main()

