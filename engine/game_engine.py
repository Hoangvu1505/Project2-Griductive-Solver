"""
Game Engine for Griductive.
Owns the complete puzzle state: hidden solutions and unrevealed clues.
Guarantees strict information separation:
- Logic Agent and UI only receive the Public Knowledge State.
- Handles verdict submissions, enforcing provability:
    * ACCEPTED: verdict is forced by current KB_t. Flips card and reveals clue.
    * NOT_PROVABLE: neither verdict is forced by current KB_t.
    * CONTRADICTED: the opposite verdict is forced by current KB_t.
"""

from typing import Dict, List, Optional, Tuple, Any, Set
import json
import os
from engine.clue import Clue
from engine.region import get_all_cells
from logic.var_map import VariableMap
from logic.kb import KnowledgeBase, build_kb
from sat.dpll import DPLLSolver


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
        """Loads and initializes puzzle from a dictionary."""
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

    def get_public_state(self) -> Dict[str, Any]:
        """
        Returns ONLY the public knowledge state.
        Never reveals hidden statuses or unrevealed clues!
        """
        public_cards = {}
        for coord, card in self.cards.items():
            is_revealed = (coord in self.revealed_statuses)
            public_cards[coord] = {
                "coord": coord,
                "name": card.name,
                "profession": card.profession,
                "is_revealed": is_revealed,
                "status": self.revealed_statuses.get(coord) if is_revealed else None,
                "clue": self.revealed_clues.get(coord) if is_revealed else None
            }

        return {
            "size": self.n,
            "cells": list(self.cells),
            "revealed_clues": list(self.revealed_clues.values()),
            "proved_verdicts": dict(self.revealed_statuses),
            "cards": public_cards
        }

    def check_verdict_provability(self, coord: str, submitted_status: str) -> Tuple[str, str]:
        """
        Uses propositional entailment on current KB_t to verify if submitted_status is forced.
        Returns:
            - 'ACCEPTED': forced by KB_t and correct
            - 'NOT_PROVABLE': neither status is forced by KB_t
            - 'CONTRADICTED': opposite status is forced by KB_t
        """
        coord_upper = coord.upper()
        status_upper = submitted_status.upper()

        if coord_upper not in self.cards:
            return "ERROR", f"Invalid coordinate {coord}"

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
        coord_upper = coord.upper()
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

