"""
Main GUI Application for Griductive.
Connects the GameEngine, LogicAgent, BoardRenderer, and Widgets into an interactive, playable desktop GUI.
Supports manual play, proof-checking with rejection feedback, clue highlighting, hints, and automated solving.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import glob
from typing import Optional, List, Dict, Any

from engine.game_engine import GameEngine
from engine.region import get_all_cells
from agent.agent import LogicAgent
from agent.uniqueness import check_uniqueness_dpll
from gui.widgets import StatusBannerWidget, TraceLogWidget, COLOR_BG
from gui.renderer import BoardRenderer


class GriductiveApp(tk.Tk):
    """Main Application Window."""

    def __init__(self, default_puzzle_path: Optional[str] = None):
        super().__init__()
        self.title("Griductive - Propositional SAT Logic Deductive Solver")
        self.geometry("1150 Central" if False else "1180x820")
        self.minsize(980, 700)
        self.configure(bg=COLOR_BG)

        self.engine = GameEngine()
        self.agent: Optional[LogicAgent] = None
        self.puzzles_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "puzzles"))
        self.auto_solve_running: bool = False

        self._init_ui()

        # Load default puzzle if available
        if default_puzzle_path and os.path.exists(default_puzzle_path):
            self.load_puzzle(default_puzzle_path)
        else:
            puzzles = self._get_bundled_puzzles()
            if puzzles:
                self.load_puzzle(puzzles[0])

    def _get_bundled_puzzles(self) -> List[str]:
        return sorted(glob.glob(os.path.join(self.puzzles_dir, "*.json")))

    def _init_ui(self):
        # 1. Top Control Bar
        self.top_bar = tk.Frame(self, bg="#2B2D42", padx=10, pady=8)
        self.top_bar.pack(fill=tk.X, side=tk.TOP)

        tk.Label(
            self.top_bar,
            text="Griductive Solver",
            font=("Segoe UI", 12, "bold"),
            fg="#EDF2F4",
            bg="#2B2D42"
        ).pack(side=tk.LEFT, padx=(0, 15))

        # Puzzle Selection Dropdown
        tk.Label(self.top_bar, text="Puzzle:", font=("Segoe UI", 9), fg="#8D99AE", bg="#2B2D42").pack(side=tk.LEFT, padx=(0, 4))
        self.puzzle_var = tk.StringVar()
        self.puzzle_combo = ttk.Combobox(self.top_bar, textvariable=self.puzzle_var, state="readonly", width=22)
        puzzles = [os.path.basename(p) for p in self._get_bundled_puzzles()]
        self.puzzle_combo["values"] = puzzles
        if puzzles:
            self.puzzle_combo.current(0)
        self.puzzle_combo.bind("<<ComboboxSelected>>", self._on_combo_puzzle_selected)
        self.puzzle_combo.pack(side=tk.LEFT, padx=(0, 6))

        # Buttons
        self.btn_load_file = tk.Button(self.top_bar, text="Open File...", command=self._browse_and_load_file, bg="#4A4E69", fg="white", relief=tk.FLAT, cursor="hand2")
        self.btn_load_file.pack(side=tk.LEFT, padx=3)

        self.btn_restart = tk.Button(self.top_bar, text="Restart", command=self.restart_puzzle, bg="#4A4E69", fg="white", relief=tk.FLAT, cursor="hand2")
        self.btn_restart.pack(side=tk.LEFT, padx=3)

        tk.Frame(self.top_bar, width=15, bg="#2B2D42").pack(side=tk.LEFT)

        self.btn_hint = tk.Button(self.top_bar, text="Hint", command=self.give_hint, bg="#0077B6", fg="white", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, cursor="hand2")
        self.btn_hint.pack(side=tk.LEFT, padx=3)

        self.btn_step = tk.Button(self.top_bar, text="Auto Solve (Step)", command=self.auto_solve_step, bg="#2A9D8F", fg="white", relief=tk.FLAT, cursor="hand2")
        self.btn_step.pack(side=tk.LEFT, padx=3)

        self.btn_auto_all = tk.Button(self.top_bar, text="Auto Solve (All)", command=self.toggle_auto_solve_all, bg="#E76F51", fg="white", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, cursor="hand2")
        self.btn_auto_all.pack(side=tk.LEFT, padx=3)

        self.btn_uniqueness = tk.Button(self.top_bar, text="Check Uniqueness", command=self.check_uniqueness, bg="#6D597A", fg="white", relief=tk.FLAT, cursor="hand2")
        self.btn_uniqueness.pack(side=tk.LEFT, padx=3)

        # 2. Bottom Status Banner
        self.banner = StatusBannerWidget(self)
        self.banner.pack(fill=tk.X, side=tk.BOTTOM)

        # 3. Main Center Area (Board on Left, Info & Trace on Right)
        self.main_content = tk.Frame(self, bg=COLOR_BG)
        self.main_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # Left: Board Area
        self.board_outer = tk.Frame(self.main_content, bg=COLOR_BG)
        self.board_outer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self.board_frame = tk.Frame(self.board_outer, bg=COLOR_BG)
        self.board_frame.pack(anchor=tk.CENTER, expand=True)

        self.renderer = BoardRenderer(
            container=self.board_frame,
            on_verdict_call=self.handle_verdict_call,
            on_clue_selected=self.handle_clue_selected
        )

        # Right: Sidebar with Stats & Deduction Log
        self.sidebar = tk.Frame(self.main_content, bg="#2B2D42", width=340, padx=10, pady=8)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.BOTH)

        # Knowledge Base Info Card
        self.kb_info_frame = tk.LabelFrame(
            self.sidebar,
            text="Knowledge Base State",
            font=("Segoe UI", 10, "bold"),
            fg="#EDF2F4",
            bg="#2B2D42",
            padx=8,
            pady=6
        )
        self.kb_info_frame.pack(fill=tk.X, pady=(0, 8))

        self.lbl_puzzle_name = tk.Label(self.kb_info_frame, text="Puzzle: None", font=("Segoe UI", 9, "bold"), fg="#EDF2F4", bg="#2B2D42", anchor=tk.W)
        self.lbl_puzzle_name.pack(fill=tk.X)

        self.lbl_progress = tk.Label(self.kb_info_frame, text="Solved Cards: 0 / 0", font=("Segoe UI", 9), fg="#8D99AE", bg="#2B2D42", anchor=tk.W)
        self.lbl_progress.pack(fill=tk.X)

        self.lbl_vars = tk.Label(self.kb_info_frame, text="SAT Variables: Primary 0 | Aux 0", font=("Segoe UI", 9), fg="#8D99AE", bg="#2B2D42", anchor=tk.W)
        self.lbl_vars.pack(fill=tk.X)

        self.lbl_clauses = tk.Label(self.kb_info_frame, text="Active Clauses: 0", font=("Segoe UI", 9), fg="#8D99AE", bg="#2B2D42", anchor=tk.W)
        self.lbl_clauses.pack(fill=tk.X)

        # Deduction Trace Widget
        self.trace_widget = TraceLogWidget(self.sidebar)
        self.trace_widget.pack(fill=tk.BOTH, expand=True)

    def load_puzzle(self, filepath: str):
        """Loads a puzzle from JSON and initializes the board and agent."""
        try:
            self.engine.load_from_json(filepath)
            self.agent = LogicAgent(self.engine.var_map, self.engine.n)
            self.trace_widget.clear()
            self.banner.show_info(f"Loaded puzzle: {os.path.basename(filepath)} ({self.engine.n}x{self.engine.n} grid)")

            public_state = self.engine.get_public_state()
            self.renderer.render_board(public_state)
            self._update_stats()

            # Update combobox selection if matching
            fname = os.path.basename(filepath)
            if fname in self.puzzle_combo["values"]:
                self.puzzle_var.set(fname)
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load puzzle: {e}")

    def _on_combo_puzzle_selected(self, event=None):
        selected_file = self.puzzle_var.get()
        if selected_file:
            path = os.path.join(self.puzzles_dir, selected_file)
            self.load_puzzle(path)

    def _browse_and_load_file(self):
        path = filedialog.askopenfilename(
            title="Open Griductive Puzzle JSON",
            initialdir=self.puzzles_dir,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            self.load_puzzle(path)

    def restart_puzzle(self):
        """Resets puzzle back to initial revealed state."""
        self.auto_solve_running = False
        self.btn_auto_all.configure(text="Auto Solve (All)", bg="#E76F51")
        self.engine.restart()
        self.agent = LogicAgent(self.engine.var_map, self.engine.n)
        self.trace_widget.clear()
        self.renderer.render_board(self.engine.get_public_state())
        self.banner.show_info("Puzzle restarted to initial state.")
        self._update_stats()

    def handle_verdict_call(self, coord: str, submitted_status: str):
        """
        Processes a player's verdict submission for a cell.
        Enforces provability: ACCEPTED, NOT_PROVABLE, or CONTRADICTED.
        """
        verdict_code, message, revealed_clue = self.engine.submit_verdict(coord, submitted_status)

        if verdict_code == "ACCEPTED":
            clue_text = revealed_clue.get_display_text(self.engine.n) if revealed_clue else ""
            clue_id = revealed_clue.id if revealed_clue else ""
            self.renderer.update_card(coord, True, submitted_status, clue_text, clue_id)
            self.banner.show_accepted(coord, submitted_status, clue_text)
            self.trace_widget.append_step(f"[PLAYER CALL] {coord} proved as {submitted_status} -> Revealed Clue [{clue_id}]: {clue_text}")
            self._update_stats()

            if self.engine.is_game_won():
                self.banner.show_info("CONGRATULATIONS! You have successfully solved the entire puzzle without guessing!")
                messagebox.showinfo("Victory!", "Congratulations! Every single character has been logically deduced!")

        elif verdict_code == "NOT_PROVABLE":
            self.banner.show_not_provable(coord, submitted_status)
        elif verdict_code == "CONTRADICTED":
            self.banner.show_contradicted(coord, submitted_status)

    def handle_clue_selected(self, coord: str):
        """
        When a revealed clue is clicked, visually highlights all cells referenced by that clue.
        Clicking again clears the highlight.
        """
        if self.renderer.selected_clue_owner == coord:
            self.renderer.clear_highlights()
            self.banner.show_info("Highlights cleared.")
            return

        public_state = self.engine.get_public_state()
        card_info = public_state["cards"].get(coord)
        if not card_info or not card_info["clue"]:
            return

        clue = card_info["clue"]
        ref_cells = clue.get_referenced_cells(self.engine.n, self.engine.var_map.get_name_to_coord_map())
        self.renderer.highlight_clue_cells(coord, ref_cells)

        ref_str = ", ".join(ref_cells) if ref_cells else "None"
        self.banner.show_info(f"Clue [{clue.id}] selected: References cell(s) [{ref_str}]")

    def give_hint(self):
        """
        Queries LogicAgent to find one currently forced verdict without looking at hidden data.
        Highlights the forced cell and any relevant active clues.
        """
        if self.engine.is_game_won():
            messagebox.showinfo("Hint", "The puzzle is already completely solved!")
            return

        public_state = self.engine.get_public_state()
        unresolved = [c for c in self.engine.cells if c not in public_state["proved_verdicts"]]

        hint_info = self.agent.get_hint(
            unresolved,
            public_state["revealed_clues"],
            public_state["proved_verdicts"]
        )

        if not hint_info:
            self.banner.show_info("HINT: No character is currently forced from public knowledge (Ambiguous state).")
            messagebox.showwarning("Hint", "No verdict can be logically forced right now with available clues.")
            return

        cell = hint_info["cell"]
        name = hint_info["name"]
        st = hint_info["forced_status"]
        rel_clue_ids = hint_info["relevant_clue_ids"]

        # Find owner coords of relevant clues
        rel_owners = []
        for clue in public_state["revealed_clues"]:
            if clue.id in rel_clue_ids and clue.owner:
                rel_owners.append(clue.owner)

        self.renderer.highlight_hint_cell(cell, rel_owners)
        self.banner.show_hint(cell, name, st, rel_clue_ids)
        self.trace_widget.append_step(f"[HINT] Character {name} [{cell}] can be proved as {st} (Relevant Clues: {', '.join(rel_clue_ids)})")

    def auto_solve_step(self):
        """Executes a single automated deduction step."""
        if self.engine.is_game_won():
            self.banner.show_info("Puzzle already completely solved.")
            return

        step_record = self.agent.step_deduce(self.engine)
        if step_record and step_record.proved_cell:
            coord = step_record.proved_cell
            st = step_record.proved_status
            clue_id = step_record.newly_revealed_clue_id
            clue_text = step_record.newly_revealed_clue_text

            self.renderer.update_card(coord, True, st, clue_text, clue_id)
            self.banner.show_accepted(coord, st, clue_text)
            self.trace_widget.append_step(step_record.to_text())
            self._update_stats()

            if self.engine.is_game_won():
                self.banner.show_info("Puzzle fully solved by Logic Agent!")
                messagebox.showinfo("Solved!", "The Logic Agent has successfully deduced every card!")
        else:
            self.banner.show_info("Auto Solve: No further verdicts are forced (Terminal state).")

    def toggle_auto_solve_all(self):
        """Starts or pauses animated automatic deduction loop."""
        if self.auto_solve_running:
            self.auto_solve_running = False
            self.btn_auto_all.configure(text="Auto Solve (All)", bg="#E76F51")
        else:
            self.auto_solve_running = True
            self.btn_auto_all.configure(text="Pause Solving", bg="#8B263E")
            self._run_auto_solve_loop()

    def _run_auto_solve_loop(self):
        if not self.auto_solve_running:
            return

        if self.engine.is_game_won():
            self.auto_solve_running = False
            self.btn_auto_all.configure(text="Auto Solve (All)", bg="#E76F51")
            return

        step_record = self.agent.step_deduce(self.engine)
        if step_record and step_record.proved_cell:
            coord = step_record.proved_cell
            st = step_record.proved_status
            clue_id = step_record.newly_revealed_clue_id
            clue_text = step_record.newly_revealed_clue_text

            self.renderer.update_card(coord, True, st, clue_text, clue_id)
            self.banner.show_accepted(coord, st, clue_text)
            self.trace_widget.append_step(step_record.to_text())
            self._update_stats()

            # Schedule next step
            self.after(250, self._run_auto_solve_loop)
        else:
            self.auto_solve_running = False
            self.btn_auto_all.configure(text="Auto Solve (All)", bg="#E76F51")
            self.banner.show_info("Auto Solve: Terminal state reached.")

    def check_uniqueness(self):
        """Performs DPLL uniqueness verification on the complete clue set."""
        all_clues = self.engine.get_all_clues()
        is_u, msg, models = check_uniqueness_dpll(all_clues, self.engine.var_map, self.engine.n)

        if is_u:
            messagebox.showinfo("Uniqueness Check", f"SUCCESS: {msg}\nThe complete clue set defines exactly 1 unique model!")
        else:
            messagebox.showwarning("Uniqueness Check", f"RESULT: {msg}\nFound {len(models)} satisfying model(s).")

    def _update_stats(self):
        """Updates knowledge base counters in the sidebar."""
        public_state = self.engine.get_public_state()
        n = self.engine.n
        total_cells = n * n
        proved_count = len(public_state["proved_verdicts"])

        pname = os.path.basename(self.puzzle_var.get() or "Custom")
        self.lbl_puzzle_name.configure(text=f"Puzzle: {pname} ({n}x{n})")
        self.lbl_progress.configure(text=f"Solved Cards: {proved_count} / {total_cells}")

        if self.engine.var_map:
            self.lbl_vars.configure(
                text=f"SAT Variables: Primary {self.engine.var_map.num_primary} | Aux {self.engine.var_map.num_aux}"
            )

        # Build current KB
        from logic.kb import build_kb
        kb = build_kb(
            public_state["revealed_clues"],
            public_state["proved_verdicts"],
            self.engine.var_map,
            self.engine.n
        )
        self.lbl_clauses.configure(text=f"Active Clauses in KB_t: {len(kb.clauses)}")


def main():
    app = GriductiveApp()
    app.mainloop()


if __name__ == "__main__":
    main()

