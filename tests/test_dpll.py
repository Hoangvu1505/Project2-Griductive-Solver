"""
Unit tests for the DPLL SAT Solver.
Tests unit propagation, conflict detection, deterministic branching,
and the deduction example from Section 3.4 of the assignment.
"""

import unittest
from sat.dpll import DPLLSolver


class TestDPLLSolver(unittest.TestCase):

    def setUp(self):
        self.solver = DPLLSolver()

    def test_empty_formula(self):
        """An empty formula is trivially satisfiable."""
        is_sat, model, stats = self.solver.solve([], num_vars=2)
        self.assertTrue(is_sat)
        self.assertIsNotNone(model)
        self.assertIn(1, model)
        self.assertIn(2, model)

    def test_simple_conflict(self):
        """Formula [1] and [-1] is unsatisfiable."""
        clauses = [[1], [-1]]
        is_sat, model, stats = self.solver.solve(clauses, num_vars=1)
        self.assertFalse(is_sat)
        self.assertIsNone(model)

    def test_unit_propagation(self):
        """[1], [-1, 2], [-2, 3] should propagate 1=True, 2=True, 3=True."""
        clauses = [[1], [-1, 2], [-2, 3]]
        is_sat, model, stats = self.solver.solve(clauses, num_vars=3)
        self.assertTrue(is_sat)
        self.assertTrue(model[1])
        self.assertTrue(model[2])
        self.assertTrue(model[3])
        self.assertGreaterEqual(stats.propagations, 2)

    def test_pdf_example_page_4(self):
        """
        Verify Example in Section 3.4 of project description:
        KB = (CA \/ CB) /\ (-CA \/ CB).
        Let CA = 1, CB = 2.
        - KB is SAT (e.g. CA=False, CB=True).
        - KB /\ -CB is UNSAT -> KB |= CB (B is Criminal).
        - KB /\ CA is SAT, and KB /\ -CA is SAT -> Status of A is UNKNOWN.
        """
        kb_clauses = [[1, 2], [-1, 2]]

        # 1. KB is SAT
        is_sat, model, _ = self.solver.solve(kb_clauses, num_vars=2)
        self.assertTrue(is_sat)

        # 2. KB /\ -CB (CB = False) is UNSAT
        is_sat_neg_b, _, _ = self.solver.solve(kb_clauses, num_vars=2, assumptions=[-2])
        self.assertFalse(is_sat_neg_b, "KB /\\ -CB should be UNSAT")

        # 3. KB /\ CB (CB = True) is SAT
        is_sat_pos_b, _, _ = self.solver.solve(kb_clauses, num_vars=2, assumptions=[2])
        self.assertTrue(is_sat_pos_b, "KB /\\ CB should be SAT")

        # Therefore B is forced to be True (Criminal)

        # 4. For CA (var 1):
        is_sat_pos_a, _, _ = self.solver.solve(kb_clauses, num_vars=2, assumptions=[1])
        is_sat_neg_a, _, _ = self.solver.solve(kb_clauses, num_vars=2, assumptions=[-1])
        self.assertTrue(is_sat_pos_a, "KB /\\ CA should be SAT")
        self.assertTrue(is_sat_neg_a, "KB /\\ -CA should be SAT")
        # Therefore A is UNKNOWN

    def test_branching_and_backtracking(self):
        """Formula requiring branching and backtracking."""
        # (1 \/ 2) /\ (-1 \/ 2) /\ (1 \/ -2)
        # Truth table:
        # (1, 1): True, True, True -> SAT
        clauses = [[1, 2], [-1, 2], [1, -2]]
        is_sat, model, stats = self.solver.solve(clauses, num_vars=2)
        self.assertTrue(is_sat)
        self.assertTrue(model[1])
        self.assertTrue(model[2])

    def test_unsat_3vars(self):
        """Formula that is UNSAT across 3 variables."""
        # All 8 combinations forbidden:
        clauses = [
            [1, 2, 3],
            [1, 2, -3],
            [1, -2, 3],
            [1, -2, -3],
            [-1, 2, 3],
            [-1, 2, -3],
            [-1, -2, 3],
            [-1, -2, -3]
        ]
        is_sat, model, stats = self.solver.solve(clauses, num_vars=3)
        self.assertFalse(is_sat)
        self.assertIsNone(model)
        self.assertGreater(stats.backtracks, 0)


if __name__ == "__main__":
    unittest.main()

