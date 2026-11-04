"""
Deductive Logic Agent for Griductive.
Classifies unresolved characters using logical consequence via DPLL:
- KB_t |= C_i  <==> KB_t /\ ¬C_i is UNSAT  --> CRIMINAL
- KB_t |= ¬C_i <==> KB_t /\ C_i is UNSAT   --> INNOCENT
- Both SAT                                 --> UNKNOWN
- KB_t UNSAT                               --> INCONSISTENT

Operates exclusively on the Public State (revealed clues and proved verdicts).
Never guesses. Implements deterministic deduction loop, hint system, and trace logging.
"""

from typing import Dict, List, Optional, Tuple, Any
import time
from engine.clue import Clue
from engine.region import get_all_cells
from logic.var_map import VariableMap
from logic.kb import KnowledgeBase, build_kb
from sat.dpll import DPLLSolver, DPLLStats
from agent.trace import DeductionTrace, DeductionStepRecord, SATQueryRecord


class LogicAgent:
    """
    Autonomous deduction agent using propositional SAT solving.
    Strictly isolated from hidden game engine data.
    """

    def __init__(self, var_map: VariableMap, n: int, solver: Optional[DPLLSolver] = None):
        self.var_map = var_map
        self.n = n
        self.solver = solver or DPLLSolver()
        self.trace = DeductionTrace()

    def check_kb_consistency(self, kb: KnowledgeBase) -> bool:
        """Verifies if the current knowledge base KB_t is satisfiable."""
        is_sat, _, _ = self.solver.solve(kb.get_clauses(), num_vars=self.var_map.total_vars)
        return is_sat

    def classify_cell(
        self,
        cell: str,
        kb: KnowledgeBase
    ) -> Tuple[str, List[SATQueryRecord]]:
        """
        Classifies an unresolved cell into:
        - 'CRIMINAL' if KB_t |= C_i (i.e. KB_t /\ ¬C_i is UNSAT)
        - 'INNOCENT' if KB_t |= ¬C_i (i.e. KB_t /\ C_i is UNSAT)
        - 'UNKNOWN' if both are SAT
        - 'INCONSISTENT' if KB_t itself is UNSAT
        """
        cell_upper = cell.upper()
        v = self.var_map.coord_to_var(cell_upper)
        name = self.var_map.coord_to_name(cell_upper) or cell_upper
        base_clauses = kb.get_clauses()
        queries: List[SATQueryRecord] = []

        # 1. Test KB_t /\ ¬C_i (assumes Innocence to prove Criminal)
        t0 = time.perf_counter()
        sat_neg, _, _ = self.solver.solve(base_clauses, num_vars=self.var_map.total_vars, assumptions=[-v])
        t_neg = time.perf_counter() - t0
        queries.append(SATQueryRecord(
            target_cell=cell_upper,
            target_name=name,
            tested_status="CRIMINAL",
            assumed_literal=-v,
            is_sat=sat_neg,
            runtime=t_neg
        ))

        # 2. Test KB_t /\ C_i (assumes Criminality to prove Innocent)
        t0 = time.perf_counter()
        sat_pos, _, _ = self.solver.solve(base_clauses, num_vars=self.var_map.total_vars, assumptions=[v])
        t_pos = time.perf_counter() - t0
        queries.append(SATQueryRecord(
            target_cell=cell_upper,
            target_name=name,
            tested_status="INNOCENT",
            assumed_literal=v,
            is_sat=sat_pos,
            runtime=t_pos
        ))

        if not sat_neg and not sat_pos:
            return "INCONSISTENT", queries
        elif not sat_neg and sat_pos:
            return "CRIMINAL", queries
        elif sat_neg and not sat_pos:
            return "INNOCENT", queries
        else:
            return "UNKNOWN", queries

    def classify_all_unresolved(
        self,
        unresolved_cells: List[str],
        kb: KnowledgeBase
    ) -> Tuple[Dict[str, str], List[SATQueryRecord]]:
        """Classifies all currently unresolved cells."""
        classifications: Dict[str, str] = {}
        all_queries: List[SATQueryRecord] = []

        for cell in unresolved_cells:
            status, queries = self.classify_cell(cell, kb)
            classifications[cell] = status
            all_queries.extend(queries)

        return classifications, all_queries

    def find_forced_verdict(
        self,
        unresolved_cells: List[str],
        kb: KnowledgeBase
    ) -> Optional[Tuple[str, str, List[SATQueryRecord]]]:
        """
        Scans unresolved cells in deterministic row-major order.
        Returns the first forced verdict (cell, status, queries), or None if none is forced.
        """
        all_queries: List[SATQueryRecord] = []
        for cell in unresolved_cells:
            status, queries = self.classify_cell(cell, kb)
            all_queries.extend(queries)
            if status in ('CRIMINAL', 'INNOCENT'):
                return cell, status, all_queries
            elif status == 'INCONSISTENT':
                raise RuntimeError(f"Inconsistent knowledge base detected while querying {cell}")
        return None

    def get_hint(
        self,
        unresolved_cells: List[str],
        revealed_clues: List[Clue],
        proved_verdicts: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """
        Generates a hint without inspecting hidden labels.
        Identifies a character whose status is currently forced and highlights relevant clues.
        """
        kb = build_kb(revealed_clues, proved_verdicts, self.var_map, self.n)
        forced = self.find_forced_verdict(unresolved_cells, kb)
        if not forced:
            return None

        cell, status, _ = forced
        name = self.var_map.coord_to_name(cell) or cell

        # Find which active clues reference this cell
        relevant_clues = []
        for clue in revealed_clues:
            if cell in clue.get_referenced_cells(self.n, self.var_map.get_name_to_coord_map()):
                relevant_clues.append(clue.id)

        return {
            "cell": cell,
            "name": name,
            "forced_status": status,
            "relevant_clue_ids": relevant_clues,
            "message": f"Character {name} at cell {cell} can be logically proved as {status}!"
        }

    def step_deduce(self, game_engine: Any) -> Optional[DeductionStepRecord]:
        """
        Executes a single deduction step against the GameEngine.
        1. Reads public state from engine.
        2. Builds KB_t.
        3. Identifies next forced verdict.
        4. Submits verdict to engine.
        5. Records trace and returns step record.
        """
        public_state = game_engine.get_public_state()
        unresolved = [c for c in self.var_map.cells if c not in public_state["proved_verdicts"]]
        if not unresolved:
            return None  # Puzzle already completely solved

        kb = build_kb(
            public_state["revealed_clues"],
            public_state["proved_verdicts"],
            self.var_map,
            self.n
        )

        step_num = self.trace.total_steps() + 1
        active_ids = [c.id for c in public_state["revealed_clues"]]

        forced = self.find_forced_verdict(unresolved, kb)
        if not forced:
            # No verdict forced: ambiguous / stuck
            rec = DeductionStepRecord(
                step_number=step_num,
                active_clue_ids=active_ids,
                sat_queries=[],
                proved_cell="",
                proved_name="",
                proved_status="UNKNOWN (No forced verdict available)"
            )
            self.trace.add_step(rec)
            return rec

        cell, status, queries = forced
        name = self.var_map.coord_to_name(cell) or cell

        # Submit verdict to GameEngine
        verdict_status, message, revealed_clue = game_engine.submit_verdict(cell, status)

        new_clue_id = revealed_clue.id if revealed_clue else ""
        new_clue_text = revealed_clue.get_display_text(self.n) if revealed_clue else ""

        rec = DeductionStepRecord(
            step_number=step_num,
            active_clue_ids=active_ids,
            sat_queries=queries,
            proved_cell=cell,
            proved_name=name,
            proved_status=status,
            newly_revealed_clue_id=new_clue_id,
            newly_revealed_clue_text=new_clue_text
        )
        self.trace.add_step(rec)
        return rec

    def solve_all(self, game_engine: Any) -> DeductionTrace:
        """Runs the deduction loop until solved or no further verdicts are provable."""
        while not game_engine.is_game_won():
            step_record = self.step_deduce(game_engine)
            if step_record is None or not step_record.proved_cell:
                break
        return self.trace

