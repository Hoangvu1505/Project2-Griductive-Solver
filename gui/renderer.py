"""
Board Renderer for Griductive.
Manages grid coordinate layout, card placement, and visual highlighting of referenced clue cells.
"""

import tkinter as tk
from typing import Dict, List, Optional, Callable, Any
from engine.region import col_letter_to_index, index_to_col_letter, rc_to_coord
from gui.widgets import CardWidget


class BoardRenderer:
    """
    Renders the NxN grid board inside a Tkinter container.
    Manages card widgets, coordinates headers, and clue-based highlighting.
    """

    def __init__(
        self,
        container: tk.Widget,
        on_verdict_call: Callable[[str, str], None],
        on_clue_selected: Callable[[str], None]
    ):
        self.container = container
        self.on_verdict_call = on_verdict_call
        self.on_clue_selected = on_clue_selected
        self.card_widgets: Dict[str, CardWidget] = {}
        self.current_n: int = 0
        self.selected_clue_owner: Optional[str] = None

    def render_board(self, public_state: Dict[str, Any]):
        """Builds or rebuilds the grid of character cards with row and column headers."""
        # Clear existing widgets
        for widget in self.container.winfo_children():
            widget.destroy()
        self.card_widgets.clear()

        n = public_state["size"]
        self.current_n = n
        cards_info = public_state["cards"]

        # 1. Render column letter headers (A, B, C, ...)
        # Blank corner at (0, 0)
        corner = tk.Label(self.container, text="", width=3, bg=self.container["bg"])
        corner.grid(row=0, column=0, padx=2, pady=2)

        for col_idx in range(n):
            col_letter = index_to_col_letter(col_idx)
            header_lbl = tk.Label(
                self.container,
                text=col_letter,
                font=("Segoe UI", 12, "bold"),
                fg="#EDF2F4",
                bg="#2B2D42",
                padx=10,
                pady=2,
                relief=tk.RAISED
            )
            header_lbl.grid(row=0, column=col_idx + 1, padx=4, pady=4, sticky="nsew")

        # 2. Render row number headers (1, 2, 3, ...) and card widgets
        for row_idx in range(n):
            row_num = row_idx + 1
            # Row header
            row_lbl = tk.Label(
                self.container,
                text=str(row_num),
                font=("Segoe UI", 12, "bold"),
                fg="#EDF2F4",
                bg="#2B2D42",
                padx=6,
                pady=10,
                relief=tk.RAISED
            )
            row_lbl.grid(row=row_idx + 1, column=0, padx=4, pady=4, sticky="nsew")

            for col_idx in range(n):
                coord = rc_to_coord(row_idx, col_idx)
                c_data = cards_info[coord]

                card = CardWidget(
                    parent=self.container,
                    coord=coord,
                    name=c_data["name"],
                    profession=c_data["profession"],
                    on_verdict_call=self.on_verdict_call,
                    on_clue_selected=self.on_clue_selected
                )
                card.grid(row=row_idx + 1, column=col_idx + 1, padx=4, pady=4, sticky="nsew")
                self.card_widgets[coord] = card

                # Update initial card state
                is_revealed = c_data["is_revealed"]
                st = c_data["status"]
                clue_obj = c_data["clue"]
                clue_text = clue_obj.get_display_text(n) if clue_obj else ""
                clue_id = clue_obj.id if clue_obj else ""

                card.update_state(is_revealed, st, clue_text, clue_id)

    def update_card(self, coord: str, is_revealed: bool, status: str, clue_text: str, clue_id: str):
        """Updates a single card widget's state."""
        coord_u = coord.upper()
        if coord_u in self.card_widgets:
            self.card_widgets[coord_u].update_state(is_revealed, status, clue_text, clue_id)

    def highlight_clue_cells(self, owner_coord: str, referenced_cells: List[str]):
        """
        Highlights the owner card and all referenced/counted cells.
        Resets highlights on all other cards.
        """
        self.selected_clue_owner = owner_coord
        ref_set = set(c.upper() for c in referenced_cells)

        for coord, card in self.card_widgets.items():
            if coord == owner_coord:
                card.set_highlight("SELECTED")
            elif coord in ref_set:
                card.set_highlight("REFERENCED")
            else:
                card.set_highlight("NORMAL")

    def highlight_hint_cell(self, forced_cell: str, relevant_clues_owners: List[str]):
        """Visually marks the forced card suggested by the Hint feature."""
        fc = forced_cell.upper()
        ref_set = set(c.upper() for c in relevant_clues_owners)

        for coord, card in self.card_widgets.items():
            if coord == fc:
                card.set_highlight("HINT")
            elif coord in ref_set:
                card.set_highlight("REFERENCED")
            else:
                card.set_highlight("NORMAL")

    def clear_highlights(self):
        """Clears all highlights back to normal."""
        self.selected_clue_owner = None
        for card in self.card_widgets.values():
            card.set_highlight("NORMAL")

