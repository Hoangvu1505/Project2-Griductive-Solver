"""
Deduction trace logging for Griductive Logic Agent.
Records:
- Step number
- Active clue identifiers in KB_t
- SAT queries and their outcomes
- Proved verdict
- Newly revealed clue
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import json


@dataclass
class SATQueryRecord:
    target_cell: str
    target_name: str
    tested_status: str  # 'CRIMINAL' or 'INNOCENT'
    assumed_literal: int
    is_sat: bool
    runtime: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_cell": self.target_cell,
            "target_name": self.target_name,
            "tested_status": self.tested_status,
            "assumed_literal": self.assumed_literal,
            "is_sat": self.is_sat,
            "conclusion": "UNSAT (Entailed!)" if not self.is_sat else "SAT (Consistent)",
            "runtime": self.runtime
        }


@dataclass
class DeductionStepRecord:
    step_number: int
    active_clue_ids: List[str]
    sat_queries: List[SATQueryRecord] = field(default_factory=list)
    proved_cell: str = ""
    proved_name: str = ""
    proved_status: str = ""
    newly_revealed_clue_id: str = ""
    newly_revealed_clue_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "active_clue_ids": self.active_clue_ids,
            "sat_queries": [q.to_dict() for q in self.sat_queries],
            "proved_cell": self.proved_cell,
            "proved_name": self.proved_name,
            "proved_status": self.proved_status,
            "newly_revealed_clue_id": self.newly_revealed_clue_id,
            "newly_revealed_clue_text": self.newly_revealed_clue_text
        }

    def to_text(self) -> str:
        lines = [
            f"=== Step {self.step_number} ===",
            f"Active Clues ({len(self.active_clue_ids)}): {', '.join(self.active_clue_ids)}",
            f"SAT Queries ({len(self.sat_queries)}):"
        ]
        for q in self.sat_queries:
            status_desc = "UNSAT -> FORCED!" if not q.is_sat else "SAT"
            neg_prefix = "~" if q.tested_status == 'CRIMINAL' else ""
            lines.append(f"  * Query KB /\\ {neg_prefix}C_{q.target_cell} ({q.tested_status}) -> {status_desc} [{q.runtime*1000:.2f}ms]")

        if self.proved_cell:
            lines.append(f"Verdict: {self.proved_cell} ({self.proved_name}) is {self.proved_status}")
            if self.newly_revealed_clue_id:
                lines.append(f"Revealed Clue [{self.newly_revealed_clue_id}]: {self.newly_revealed_clue_text}")
        else:
            lines.append("Verdict: NONE (Terminal / Stuck)")
        return "\n".join(lines)


class DeductionTrace:
    """Manages the full execution trace of the deduction loop."""

    def __init__(self):
        self.steps: List[DeductionStepRecord] = []

    def add_step(self, step: DeductionStepRecord) -> None:
        self.steps.append(step)

    def total_steps(self) -> int:
        return len(self.steps)

    def total_sat_queries(self) -> int:
        return sum(len(step.sat_queries) for step in self.steps)

    def to_text(self) -> str:
        return "\n\n".join(step.to_text() for step in self.steps)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_steps": self.total_steps(),
            "total_sat_queries": self.total_sat_queries(),
            "steps": [step.to_dict() for step in self.steps]
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
