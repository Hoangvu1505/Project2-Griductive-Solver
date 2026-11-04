"""
DPLL SAT Solver for Griductive.
Implements the Davis-Putnam-Logemann-Loveland procedure with:
1. Unit propagation
2. Conflict detection
3. Deterministic variable selection
4. Recursive branching and backtracking
5. Complete model generation on SAT
6. Full statistics recording (decisions, propagations, backtracks, runtime)
7. Support for assumptions / temporary unit literals
"""

import time
from typing import List, Dict, Optional, Tuple, Set, Any
from dataclasses import dataclass, field


@dataclass
class DPLLStats:
    decisions: int = 0
    propagations: int = 0
    backtracks: int = 0
    runtime: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decisions": self.decisions,
            "propagations": self.propagations,
            "backtracks": self.backtracks,
            "runtime": self.runtime
        }


class DPLLSolver:
    """
    DPLL-based propositional SAT solver.
    Operates on integer clauses, e.g. [[1, -2], [-1, 3]].
    """

    def __init__(self):
        self.stats = DPLLStats()
        self._all_vars: List[int] = []

    def solve(
        self,
        clauses: List[List[int]],
        num_vars: Optional[int] = None,
        assumptions: Optional[List[int]] = None
    ) -> Tuple[bool, Optional[Dict[int, bool]], DPLLStats]:
        """
        Solves the CNF formula with optional assumptions.
        Returns:
            (is_sat, assignment_dict_or_None, stats)
        """
        start_time = time.perf_counter()
        self.stats = DPLLStats()

        # Collect all variables from clauses and assumptions
        var_set: Set[int] = set()
        for clause in clauses:
            for lit in clause:
                var_set.add(abs(lit))
        if assumptions:
            for lit in assumptions:
                var_set.add(abs(lit))
        if num_vars:
            for v in range(1, num_vars + 1):
                var_set.add(v)

        self._all_vars = sorted(list(var_set))

        # Initial formula copy
        working_clauses = [list(c) for c in clauses]
        if assumptions:
            for lit in assumptions:
                working_clauses.append([lit])

        assignment: Dict[int, bool] = {}

        # Run DPLL recursive solver
        is_sat, final_assignment = self._dpll(working_clauses, assignment)

        self.stats.runtime = time.perf_counter() - start_time

        if is_sat:
            # Complete the assignment for any unassigned variables deterministically (default False)
            assert final_assignment is not None
            for v in self._all_vars:
                if v not in final_assignment:
                    final_assignment[v] = False
            return True, final_assignment, self.stats
        else:
            return False, None, self.stats

    def _evaluate_clause(self, clause: List[int], assignment: Dict[int, bool]) -> Tuple[Optional[bool], List[int]]:
        """
        Evaluates a clause under the partial assignment.
        Returns (clause_status, unassigned_literals):
        - clause_status is True if at least one literal is satisfied.
        - clause_status is False if all literals are falsified (conflict).
        - clause_status is None if unresolved.
        """
        unassigned = []
        for lit in clause:
            var = abs(lit)
            if var in assignment:
                val = assignment[var]
                # Literal is True if (lit > 0 and val == True) or (lit < 0 and val == False)
                if (lit > 0 and val) or (lit < 0 and not val):
                    return True, []
            else:
                unassigned.append(lit)

        if not unassigned:
            # All literals were evaluated to False
            return False, []
        return None, unassigned

    def _unit_propagate(
        self,
        clauses: List[List[int]],
        assignment: Dict[int, bool]
    ) -> Tuple[bool, Dict[int, bool]]:
        """
        Performs unit propagation iteratively.
        Returns: (success, updated_assignment)
        success is False if a conflict (empty clause) was detected.
        """
        current_assign = dict(assignment)

        while True:
            unit_found = False
            for clause in clauses:
                status, unassigned = self._evaluate_clause(clause, current_assign)
                if status is False:
                    # Conflict: all literals in this clause are False
                    return False, current_assign
                elif status is None and len(unassigned) == 1:
                    # Unit clause!
                    unit_lit = unassigned[0]
                    var = abs(unit_lit)
                    val = (unit_lit > 0)
                    if var in current_assign:
                        if current_assign[var] != val:
                            return False, current_assign
                    else:
                        current_assign[var] = val
                        self.stats.propagations += 1
                        unit_found = True
                        break  # restart scan with new assignment

            if not unit_found:
                break

        return True, current_assign

    def _dpll(
        self,
        clauses: List[List[int]],
        assignment: Dict[int, bool]
    ) -> Tuple[bool, Optional[Dict[int, bool]]]:
        """Recursive DPLL procedure."""
        # 1. Unit propagation
        success, propagated_assignment = self._unit_propagate(clauses, assignment)
        if not success:
            return False, None

        # 2. Check if all clauses are satisfied
        all_satisfied = True
        for clause in clauses:
            status, _ = self._evaluate_clause(clause, propagated_assignment)
            if status is False:
                return False, None
            if status is not True:
                all_satisfied = False

        if all_satisfied:
            return True, propagated_assignment

        # 3. Deterministic variable selection:
        # Choose the first unassigned variable in sorted order
        chosen_var = None
        for v in self._all_vars:
            if v not in propagated_assignment:
                chosen_var = v
                break

        if chosen_var is None:
            # All variables assigned; check satisfied
            return all_satisfied, propagated_assignment if all_satisfied else None

        # 4. Recursive branching and backtracking
        # Try chosen_var = True
        self.stats.decisions += 1
        branch_assign_true = dict(propagated_assignment)
        branch_assign_true[chosen_var] = True
        sat_res, model = self._dpll(clauses, branch_assign_true)
        if sat_res:
            return True, model

        # Backtrack and try chosen_var = False
        self.stats.backtracks += 1
        self.stats.decisions += 1
        branch_assign_false = dict(propagated_assignment)
        branch_assign_false[chosen_var] = False
        sat_res, model = self._dpll(clauses, branch_assign_false)
        if sat_res:
            return True, model

        self.stats.backtracks += 1
        return False, None

