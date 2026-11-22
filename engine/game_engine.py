"""
Game Engine for Griductive.
Owns the complete puzzle state: hidden solutions and unrevealed clues.
Guarantees strict information separation:
- Logic Agent and UI only receive the Public Knowledge State.
- Handles verdict submissions, enforcing provability:
    * ACCEPTED: verdict is forced by current KB_t. Flips card and reveals clue.
    * NOT_PROVABLE: neither verdict is forced by current KB_t.
    * CONTRADICTED: the opposite verdict is forced by current KB_t.
- Exposes the public knowledge as a typed PublicState (get_public_state(as_object=True)).
- Validates puzzle files on load and can brute-force check that a puzzle has a unique solution
  (check_unique_solution / verify_puzzle). Run `python -m engine.game_engine` from the repo root
  to verify every file in puzzles/.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any, Set
import json
import os
import sys
from engine.clue import Clue, VALID_STATUSES
from engine.evaluator import find_all_solutions
from engine.region import get_all_cells
from logic.var_map import VariableMap
from logic.kb import KnowledgeBase, build_kb
from sat.dpll import DPLLSolver


@dataclass(frozen=True)
class PublicCard:
    """What the UI / agent may know about one card. status and clue are None until proved."""
    coord: str
    name: str
    profession: str
    is_revealed: bool
    status: Optional[str] = None
    clue: Optional[Clue] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "coord": self.coord,
            "name": self.name,
            "profession": self.profession,
            "is_revealed": self.is_revealed,
            "status": self.status,
            "clue": self.clue,
        }


@dataclass(frozen=True)
class PublicState:
    """
    Public knowledge state: everything a player / Logic Agent is allowed to see.
    Hidden statuses and unrevealed clues never appear here.
    """
    size: int
    cells: Tuple[str, ...]
    revealed_clues: Tuple[Clue, ...]
    proved_verdicts: Dict[str, str]      # coord -> 'CRIMINAL' | 'INNOCENT'
    cards: Dict[str, PublicCard]

    @property
    def revealed_count(self) -> int:
        return len(self.proved_verdicts)

    @property
    def is_complete(self) -> bool:
        return len(self.proved_verdicts) == len(self.cells)

    def to_dict(self) -> Dict[str, Any]:
        """Plain-dict form (same shape GameEngine.get_public_state() has always returned)."""
        return {
            "size": self.size,
            "cells": list(self.cells),
            "revealed_clues": list(self.revealed_clues),
            "proved_verdicts": dict(self.proved_verdicts),
            "cards": {coord: card.to_dict() for coord, card in self.cards.items()},
        }


def validate_puzzle_data(data: Dict[str, Any]) -> List[str]:
    """
    Structural check of a puzzle dict. Returns a list of human-readable problems (empty = valid):
    size, one card per cell (no duplicates / out-of-grid coords), valid statuses,
    well-formed clues (Clue.validate), at least one initially revealed card.
    """
    problems: List[str] = []
    try:
        n = int(data.get("size", 3))
    except (TypeError, ValueError):
        return [f"size must be an integer, got {data.get('size')!r}"]
    if not (1 <= n <= 26):
        return [f"size must be between 1 and 26, got {n}"]

    grid = set(get_all_cells(n))
    seen: Set[str] = set()
    any_revealed = False

    for idx, c in enumerate(data.get("characters", [])):
        if not isinstance(c, dict) or "coord" not in c:
            problems.append(f"characters[{idx}]: missing 'coord'")
            continue
        coord = str(c["coord"]).upper()
        if coord not in grid:
            problems.append(f"{coord}: outside the {n}x{n} grid")
        if coord in seen:
            problems.append(f"{coord}: duplicated card")
        seen.add(coord)

        status = str(c.get("status", "")).upper()
        if status not in VALID_STATUSES:
            problems.append(f"{coord}: status must be CRIMINAL or INNOCENT, got '{status}'")

        if c.get("initially_revealed", False):
            any_revealed = True

        clue_dict = c.get("clue")
        if not isinstance(clue_dict, dict) or "clue_type" not in clue_dict:
            problems.append(f"{coord}: missing clue / clue_type")
            continue
        try:
            Clue.from_dict(clue_dict).validate(n)
        except (ValueError, KeyError, TypeError) as e:
            problems.append(f"{coord}: {e}")

    missing = sorted(grid - seen)
    if missing:
        problems.append(f"missing cards for cells: {', '.join(missing)}")
    if not any_revealed:
        problems.append("no card is initially_revealed, the player would have nothing to start from")
    return problems


class CharacterCard:
    """Represents a character card on the board."""

    def __init__(
        self,
        coord: str,
        name: str,
        profession: str,
        status: str,
        clue: Clue,
        initially_revealed: bool = False
    ):
        self.coord = coord.upper()
        self.name = name
        self.profession = profession
        self.status = status.upper()  # 'CRIMINAL' or 'INNOCENT'
        self.clue = clue
        self.initially_revealed = initially_revealed


class GameEngine:
    """
    Core engine managing the secret puzzle truth and public reveal state.
    """

    def __init__(self):
        self.n: int = 0
        self.cards: Dict[str, CharacterCard] = {}
        self.cells: List[str] = []
        self.var_map: Optional[VariableMap] = None
        self.solver = DPLLSolver()

        # Public state
        self.revealed_statuses: Dict[str, str] = {}  # coord -> 'CRIMINAL' | 'INNOCENT'
        self.revealed_clues: Dict[str, Clue] = {}    # coord -> Clue
        self.initial_revealed_coords: Set[str] = set()

    def load_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Loads and initializes puzzle from a dictionary.
        Raises ValueError listing every problem if the puzzle is malformed
        (the engine is left untouched in that case).
        """
        problems = validate_puzzle_data(data)
        if problems:
            raise ValueError("Invalid puzzle:\n  - " + "\n  - ".join(problems))

        self.n = int(data.get("size", 3))
        self.cells = get_all_cells(self.n)
        self.cards.clear()
        self.revealed_statuses.clear()
        self.revealed_clues.clear()
        self.initial_revealed_coords.clear()

        char_names = {}
        cards_raw = data.get("characters", [])

        for c_data in cards_raw:
            coord = c_data["coord"].upper()
            name = c_data.get("name", coord)
            profession = c_data.get("profession", "Citizen")
            status = c_data["status"].upper()
            clue_dict = c_data["clue"]
            clue_obj = Clue.from_dict(clue_dict)
            clue_obj.owner = coord
            initially_revealed = bool(c_data.get("initially_revealed", False))

            card = CharacterCard(
                coord=coord,
                name=name,
                profession=profession,
                status=status,
                clue=clue_obj,
                initially_revealed=initially_revealed
            )
            self.cards[coord] = card
            char_names[coord] = name

        self.var_map = VariableMap(self.cells, char_names)

        # Initialize public state from initially revealed cards
        for coord, card in self.cards.items():
            if card.initially_revealed:
                self.revealed_statuses[coord] = card.status
                self.revealed_clues[coord] = card.clue
                self.initial_revealed_coords.add(coord)

    def load_from_json(self, filepath: str) -> None:
        """Loads puzzle configuration from a JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.load_from_dict(data)

    def restart(self) -> None:
        """Resets the game state to initially revealed cards."""
        self.revealed_statuses.clear()
        self.revealed_clues.clear()
        for coord in self.initial_revealed_coords:
            card = self.cards[coord]
            self.revealed_statuses[coord] = card.status
            self.revealed_clues[coord] = card.clue

    def get_public_state(self, as_object: bool = False):
        """
        Returns ONLY the public knowledge state.
        Never reveals hidden statuses or unrevealed clues!

        as_object=False (default): plain dict, exactly as before (existing callers keep working).
        as_object=True: typed, immutable PublicState.
        """
        public_cards = {}
        for coord, card in self.cards.items():
            is_revealed = (coord in self.revealed_statuses)
            public_cards[coord] = PublicCard(
                coord=coord,
                name=card.name,
                profession=card.profession,
                is_revealed=is_revealed,
                status=self.revealed_statuses.get(coord) if is_revealed else None,
                clue=self.revealed_clues.get(coord) if is_revealed else None,
            )

        state = PublicState(
            size=self.n,
            cells=tuple(self.cells),
            revealed_clues=tuple(self.revealed_clues.values()),
            proved_verdicts=dict(self.revealed_statuses),
            cards=public_cards,
        )
        return state if as_object else state.to_dict()

    def check_verdict_provability(self, coord: str, submitted_status: str) -> Tuple[str, str]:
        """
        Uses propositional entailment on current KB_t to verify if submitted_status is forced.
        Returns:
            - 'ACCEPTED': forced by KB_t and correct
            - 'NOT_PROVABLE': neither status is forced by KB_t
            - 'CONTRADICTED': opposite status is forced by KB_t
              (also returned if KB_t is itself inconsistent, which only happens with a broken puzzle)
            - 'ALREADY_PROVED': the cell is already revealed
            - 'ERROR': unknown coordinate or status other than CRIMINAL / INNOCENT
        """
        coord_upper = str(coord).strip().upper()
        status_upper = str(submitted_status).strip().upper()

        if coord_upper not in self.cards:
            return "ERROR", f"Invalid coordinate {coord}"

        if status_upper not in VALID_STATUSES:
            return "ERROR", f"Invalid status '{submitted_status}': must be CRIMINAL or INNOCENT"

        if coord_upper in self.revealed_statuses:
            return "ALREADY_PROVED", f"{coord_upper} is already revealed"

        # Build current KB_t from public state only
        kb = build_kb(
            list(self.revealed_clues.values()),
            self.revealed_statuses,
            self.var_map,
            self.n
        )

        v = self.var_map.coord_to_var(coord_upper)
        base_clauses = kb.get_clauses()

        # Check if submitted_status is entailed:
        # If testing CRIMINAL (v=True): KB_t |= v  <==> KB_t /\ -v is UNSAT
        # If testing INNOCENT (v=False): KB_t |= -v <==> KB_t /\ v is UNSAT
        neg_literal = -v if status_upper == 'CRIMINAL' else v
        opp_literal = v if status_upper == 'CRIMINAL' else -v

        # 1. Check if submitted verdict is forced: KB_t /\ neg_literal is UNSAT
        is_sat_neg, _, _ = self.solver.solve(base_clauses, num_vars=self.var_map.total_vars, assumptions=[neg_literal])
        is_submitted_forced = not is_sat_neg

        # 2. Check if opposite verdict is forced: KB_t /\ opp_literal is UNSAT
        is_sat_opp, _, _ = self.solver.solve(base_clauses, num_vars=self.var_map.total_vars, assumptions=[opp_literal])
        is_opposite_forced = not is_sat_opp

        if is_opposite_forced:
            return "CONTRADICTED", "CONTRADICTED: The opposite verdict is logically forced from available clues!"
        elif is_submitted_forced:
            return "ACCEPTED", "ACCEPTED: Verdict is logically entailed by current knowledge base."
        else:
            return "NOT_PROVABLE", "NOT_PROVABLE: Neither verdict is logically forced yet. No guessing allowed!"

    def submit_verdict(self, coord: str, submitted_status: str) -> Tuple[str, str, Optional[Clue]]:
        """
        Processes a player or agent verdict call.
        Returns:
            (verdict_result, message, newly_revealed_clue_or_None)
        """
        coord_upper = str(coord).strip().upper()
        verdict_code, message = self.check_verdict_provability(coord_upper, submitted_status)

        if verdict_code == "ACCEPTED":
            # Reveal card
            card = self.cards[coord_upper]
            self.revealed_statuses[coord_upper] = card.status
            self.revealed_clues[coord_upper] = card.clue
            return "ACCEPTED", message, card.clue
        else:
            return verdict_code, message, None

    def is_game_won(self) -> bool:
        """Returns True if every cell on the board has been proved."""
        return len(self.revealed_statuses) == len(self.cells)

    def get_all_clues(self) -> List[Clue]:
        """Returns all clues on the board (used for uniqueness checking)."""
        return [c.clue for c in self.cards.values()]



    # ------------------------------------------------------------------
    # Puzzle verification (development / testing tools: they read the hidden solution)
    # ------------------------------------------------------------------
    def _hidden_assignment(self) -> Dict[str, bool]:
        """Hidden solution as {coord: is_criminal}. Engine-internal, never expose to UI / agent."""
        return {coord: card.status == 'CRIMINAL' for coord, card in self.cards.items()}

    def check_unique_solution(self) -> Dict[str, Any]:
        """
        Brute force over all 2^(n*n) assignments using the direct semantic evaluator
        (no CNF, no DPLL), keeping those that satisfy every clue on the board.
        Returns:
            num_solutions: how many assignments satisfy all clues
            is_unique: num_solutions == 1
            matches_hidden_solution: the status stored in the puzzle is one of them
        """
        solutions = find_all_solutions(self.get_all_clues(), self.n)
        hidden = self._hidden_assignment()
        return {
            "num_solutions": len(solutions),
            "is_unique": len(solutions) == 1,
            "matches_hidden_solution": hidden in solutions,
        }

    def solve_by_deduction(self) -> Tuple[bool, List[List[str]]]:
        """
        Plays the whole game with a perfect agent that only submits the correct verdict for cells
        and relies on the real pipeline (KB + SAT) to accept it. Tells whether the puzzle can be
        finished by pure deduction from its initially revealed cards, without any guessing.
        Returns (solved, passes): passes[i] lists the cells accepted during pass i
        (cells are tried in board order, so one pass can chain several deductions).
        The public state is restored afterwards.
        """
        saved_statuses = dict(self.revealed_statuses)
        saved_clues = dict(self.revealed_clues)
        passes: List[List[str]] = []
        try:
            while not self.is_game_won():
                accepted = []
                for coord in self.cells:
                    if coord in self.revealed_statuses:
                        continue
                    code, _, _ = self.submit_verdict(coord, self.cards[coord].status)
                    if code == "ACCEPTED":
                        accepted.append(coord)
                if not accepted:
                    break
                passes.append(accepted)
            return self.is_game_won(), passes
        finally:
            self.revealed_statuses.clear()
            self.revealed_statuses.update(saved_statuses)
            self.revealed_clues.clear()
            self.revealed_clues.update(saved_clues)

    def verify_puzzle(self, check_deduction: bool = True) -> Dict[str, Any]:
        """check_unique_solution() plus (optionally) solve_by_deduction(); report['ok'] is the verdict."""
        report = self.check_unique_solution()
        ok = report["is_unique"] and report["matches_hidden_solution"]
        if check_deduction:
            solved, passes = self.solve_by_deduction()
            report["solvable_by_deduction"] = solved
            report["deduction_passes"] = len(passes)
            ok = ok and solved
        report["ok"] = ok
        return report


def _main(argv: List[str]) -> int:
    """python -m engine.game_engine [puzzle.json ...]  (default: every file in puzzles/)"""
    import glob
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = argv or sorted(glob.glob(os.path.join(root, "puzzles", "*.json")))
    all_ok = True
    for path in paths:
        name = os.path.basename(path)
        engine = GameEngine()
        try:
            engine.load_from_json(path)
        except ValueError as e:
            print(f"FAIL  {name}: {e}")
            all_ok = False
            continue
        r = engine.verify_puzzle()
        status = "PASS" if r["ok"] else "FAIL"
        all_ok &= r["ok"]
        print(f"{status}  {name:20s} solutions={r['num_solutions']}  "
              f"matches_hidden={r['matches_hidden_solution']}  "
              f"solvable_by_deduction={r['solvable_by_deduction']} ({r['deduction_passes']} passes)")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))