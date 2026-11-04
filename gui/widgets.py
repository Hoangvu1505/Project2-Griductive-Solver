"""
Custom UI Widgets for Griductive.
Implements:
- CardWidget: Character card displaying coordinates, name, profession, status, clue, and call buttons.
- StatusBannerWidget: Color-coded feedback alerts (ACCEPTED, NOT_PROVABLE, CONTRADICTED).
- TraceLogWidget: Scrollable deduction history log.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, Any, List


# Color Palette
COLOR_BG = "#1E1E24"
COLOR_CARD_FACE_DOWN = "#2B2D42"
COLOR_CARD_REVEALED = "#F8F9FA"
COLOR_CRIMINAL = "#D90429"
COLOR_INNOCENT = "#2B9348"
COLOR_HIGHLIGHT_REF = "#FFB703"
COLOR_HIGHLIGHT_HINT = "#00B4D8"
COLOR_BORDER_NORMAL = "#4A4E69"
COLOR_BORDER_SELECTED = "#7209B7"


class CardWidget(tk.Frame):
    """
    Interactive character card widget on the grid.
    Visual states:
    - FACE DOWN: shows coord, name, profession, and [Criminal] / [Innocent] call buttons.
    - REVEALED: shows status badge (CRIMINAL / INNOCENT) and structured clue text.
    - HIGHLIGHTED: highlighted when referenced by a selected clue or suggested by a hint.
    """

    def __init__(
        self,
        parent: tk.Widget,
        coord: str,
        name: str,
        profession: str,
        on_verdict_call: Callable[[str, str], None],
        on_clue_selected: Callable[[str], None],
        width: int = 150,
        height: int = 170
    ):
        super().__init__(
            parent,
            bg=COLOR_CARD_FACE_DOWN,
            highlightbackground=COLOR_BORDER_NORMAL,
            highlightthickness=2,
            padx=4,
            pady=4
        )
        self.coord = coord
        self.name = name
        self.profession = profession
        self.on_verdict_call = on_verdict_call
        self.on_clue_selected = on_clue_selected

        self.is_revealed: bool = False
        self.status: Optional[str] = None
        self.clue_text: str = ""
        self.clue_id: str = ""

        self._build_ui()

    def _build_ui(self):
        # Header: Coord and Name
        self.header_frame = tk.Frame(self, bg=COLOR_CARD_FACE_DOWN)
        self.header_frame.pack(fill=tk.X, pady=(0, 2))

        self.coord_label = tk.Label(
            self.header_frame,
            text=f"[{self.coord}]",
            font=("Segoe UI", 9, "bold"),
            fg="#8D99AE",
            bg=COLOR_CARD_FACE_DOWN
        )
        self.coord_label.pack(side=tk.LEFT)

        self.name_label = tk.Label(
            self.header_frame,
            text=self.name,
            font=("Segoe UI", 9, "bold"),
            fg="#EDF2F4",
            bg=COLOR_CARD_FACE_DOWN
        )
        self.name_label.pack(side=tk.RIGHT)

        # Profession subtitle
        self.prof_label = tk.Label(
            self,
            text=self.profession,
            font=("Segoe UI", 8, "italic"),
            fg="#8D99AE",
            bg=COLOR_CARD_FACE_DOWN
        )
        self.prof_label.pack(anchor=tk.W, pady=(0, 4))

        # Center Status Area / Badge
        self.status_badge = tk.Label(
            self,
            text="? HIDDEN ?",
            font=("Segoe UI", 9, "bold"),
            fg="#8D99AE",
            bg="#3A3D54",
            relief=tk.RIDGE,
            pady=3
        )
        self.status_badge.pack(fill=tk.X, pady=4)

        # Actions frame for face-down cards
        self.actions_frame = tk.Frame(self, bg=COLOR_CARD_FACE_DOWN)
        self.actions_frame.pack(fill=tk.X, pady=4)

        self.btn_crim = tk.Button(
            self.actions_frame,
            text="+ Criminal",
            font=("Segoe UI", 8, "bold"),
            bg="#800F2F",
            fg="white",
            activebackground="#D90429",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.on_verdict_call(self.coord, "CRIMINAL")
        )
        self.btn_crim.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))

        self.btn_inno = tk.Button(
            self.actions_frame,
            text="- Innocent",
            font=("Segoe UI", 8, "bold"),
            bg="#1B4332",
            fg="white",
            activebackground="#2B9348",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.on_verdict_call(self.coord, "INNOCENT")
        )
        self.btn_inno.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(2, 0))

        # Clue display box (visible when revealed)
        self.clue_box = tk.Label(
            self,
            text="",
            font=("Segoe UI", 8),
            fg="#1A1A24",
            bg="#E9ECEF",
            wraplength=135,
            justify=tk.LEFT,
            relief=tk.SUNKEN,
            padx=4,
            pady=4,
            cursor="hand2"
        )
        self.clue_box.bind("<Button-1>", lambda e: self.on_clue_selected(self.coord))

    def update_state(
        self,
        is_revealed: bool,
        status: Optional[str] = None,
        clue_text: str = "",
        clue_id: str = ""
    ):
        """Updates the visual representation of this card."""
        self.is_revealed = is_revealed
        self.status = status
        self.clue_text = clue_text
        self.clue_id = clue_id

        if is_revealed:
            # Card is revealed face-up
            bg_color = COLOR_CARD_REVEALED
            self.configure(bg=bg_color)
            self.header_frame.configure(bg=bg_color)
            self.coord_label.configure(bg=bg_color, fg="#495057")
            self.name_label.configure(bg=bg_color, fg="#212529")
            self.prof_label.configure(bg=bg_color, fg="#6C757D")

            # Update status badge
            if status == "CRIMINAL":
                self.status_badge.configure(
                    text="CRIMINAL",
                    bg=COLOR_CRIMINAL,
                    fg="white",
                    font=("Segoe UI", 9, "bold")
                )
            else:
                self.status_badge.configure(
                    text="INNOCENT",
                    bg=COLOR_INNOCENT,
                    fg="white",
                    font=("Segoe UI", 9, "bold")
                )

            # Hide action buttons
            self.actions_frame.pack_forget()

            # Show clue box
            self.clue_box.configure(text=f"CLUE [{clue_id}]:\n{clue_text}")
            self.clue_box.pack(fill=tk.BOTH, expand=True, pady=(2, 0))
        else:
            # Card is face-down
            self.configure(bg=COLOR_CARD_FACE_DOWN)
            self.header_frame.configure(bg=COLOR_CARD_FACE_DOWN)
            self.coord_label.configure(bg=COLOR_CARD_FACE_DOWN, fg="#8D99AE")
            self.name_label.configure(bg=COLOR_CARD_FACE_DOWN, fg="#EDF2F4")
            self.prof_label.configure(bg=COLOR_CARD_FACE_DOWN, fg="#8D99AE")

            self.status_badge.configure(
                text="? FACE DOWN ?",
                bg="#3A3D54",
                fg="#8D99AE",
                font=("Segoe UI", 8, "italic")
            )
            self.clue_box.pack_forget()
            self.actions_frame.pack(fill=tk.X, pady=4)

        self.set_highlight("NORMAL")

    def set_highlight(self, mode: str):
        """
        Sets border and background highlight:
        - 'NORMAL': standard border
        - 'SELECTED': clue owner card
        - 'REFERENCED': cells referenced/counted by the selected clue
        - 'HINT': forced card recommended by hint
        """
        if mode == "SELECTED":
            self.configure(highlightbackground=COLOR_BORDER_SELECTED, highlightthickness=3)
        elif mode == "REFERENCED":
            self.configure(highlightbackground=COLOR_HIGHLIGHT_REF, highlightthickness=3)
        elif mode == "HINT":
            self.configure(highlightbackground=COLOR_HIGHLIGHT_HINT, highlightthickness=3)
        else:
            self.configure(highlightbackground=COLOR_BORDER_NORMAL, highlightthickness=2)


class StatusBannerWidget(tk.Frame):
    """Dynamic alert banner for game actions and verdict rejections."""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent, bg="#2B2D42", padx=10, pady=6)
        self.label = tk.Label(
            self,
            text="Welcome to Griductive! Choose a face-down card to submit a verdict, or select a clue to inspect.",
            font=("Segoe UI", 10),
            fg="#EDF2F4",
            bg="#2B2D42",
            wraplength=800,
            justify=tk.LEFT
        )
        self.label.pack(fill=tk.X)

    def show_accepted(self, coord: str, status: str, clue_text: str):
        self.configure(bg="#1B4332")
        self.label.configure(
            bg="#1B4332",
            fg="#D8F3DC",
            text=f"ACCEPTED: Card {coord} proved as {status}! Clue revealed: '{clue_text}'"
        )

    def show_not_provable(self, coord: str, status: str):
        self.configure(bg="#7F4F24")
        self.label.configure(
            bg="#7F4F24",
            fg="#FFEDD8",
            text=f"REJECTED [NOT_PROVABLE]: Calling {coord} as {status} is not justified by currently revealed clues! NO GUESSING allowed."
        )

    def show_contradicted(self, coord: str, status: str):
        self.configure(bg="#6A040F")
        self.label.configure(
            bg="#6A040F",
            fg="#FFCCD5",
            text=f"REJECTED [CONTRADICTED]: Calling {coord} as {status} is CONTRADICTED! The opposite status is logically forced!"
        )

    def show_hint(self, cell: str, name: str, status: str, relevant_clues: List[str]):
        clue_str = f" using clue(s): {', '.join(relevant_clues)}" if relevant_clues else ""
        self.configure(bg="#005F73")
        self.label.configure(
            bg="#005F73",
            fg="#E0FAFF",
            text=f"HINT: Character {name} [{cell}] is logically forced to be {status}{clue_str}!"
        )

    def show_info(self, message: str):
        self.configure(bg="#2B2D42")
        self.label.configure(bg="#2B2D42", fg="#EDF2F4", text=message)


class TraceLogWidget(tk.Frame):
    """Scrollable text log displaying deduction steps, SAT calls, and KB updates."""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent, bg="#1E1E24")
        self.header = tk.Label(
            self,
            text="Deduction Trace Log",
            font=("Segoe UI", 10, "bold"),
            fg="#EDF2F4",
            bg="#1E1E24"
        )
        self.header.pack(anchor=tk.W, pady=(0, 4))

        self.text = tk.Text(
            self,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#141419",
            fg="#E0E1DD",
            insertbackground="white",
            relief=tk.FLAT,
            padx=6,
            pady=6,
            width=45
        )
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.text.yview)
        self.text.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Style tags
        self.text.tag_config("step_header", foreground="#4CC9F0", font=("Consolas", 9, "bold"))
        self.text.tag_config("verdict_accepted", foreground="#52B788", font=("Consolas", 9, "bold"))
        self.text.tag_config("sat_query", foreground="#8D99AE")
        self.text.tag_config("hint", foreground="#FFB703")

    def append_step(self, step_text: str):
        self.text.insert(tk.END, step_text + "\n\n")
        self.text.see(tk.END)

    def clear(self):
        self.text.delete("1.0", tk.END)

