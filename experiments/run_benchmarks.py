"""
Benchmark and experiment evaluation suite for Griductive.
Evaluates 3x3, 4x4, and 5x5 puzzles against DPLL SAT solver and Logic Agent.
Records the 6 required metrics:
1. Primary and auxiliary variable counts
2. CNF clause counts
3. Total SAT calls
4. Decisions, propagations, and backtracks
5. Number of deduction steps / reveal waves
6. Total and per-query runtime
Exports results to CSV and generates comparison charts.
"""

import sys
import os
import glob
import time
import csv

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import List, Dict, Any, Optional
from engine.game_engine import GameEngine
from agent.agent import LogicAgent
from logic.kb import build_kb
from sat.dpll import DPLLSolver


class InstrumentedDPLLSolver(DPLLSolver):
    """Subclass of DPLLSolver that accumulates cumulative statistics across multiple solve calls."""

    def __init__(self):
        super().__init__()
        self.total_calls: int = 0
        self.cum_decisions: int = 0
        self.cum_propagations: int = 0
        self.cum_backtracks: int = 0
        self.cum_sat_runtime: float = 0.0

    def solve(self, clauses, num_vars=None, assumptions=None):
        self.total_calls += 1
        is_sat, model, stats = super().solve(clauses, num_vars, assumptions)
        self.cum_decisions += stats.decisions
        self.cum_propagations += stats.propagations
        self.cum_backtracks += stats.backtracks
        self.cum_sat_runtime += stats.runtime
        return is_sat, model, stats


def run_single_benchmark(puzzle_path: str, timeout_sec: float = 30.0) -> Dict[str, Any]:
    """Runs a complete benchmark test on a single puzzle file."""
    engine = GameEngine()
    engine.load_from_json(puzzle_path)

    puzzle_name = os.path.basename(puzzle_path)
    n = engine.n
    num_primary = engine.var_map.num_primary
    num_aux = engine.var_map.num_aux
    total_vars = engine.var_map.total_vars

    # Measure initial KB clause count
    initial_kb = build_kb(
        list(engine.revealed_clues.values()),
        engine.revealed_statuses,
        engine.var_map,
        engine.n
    )
    initial_clauses = len(initial_kb.clauses)

    solver = InstrumentedDPLLSolver()
    agent = LogicAgent(engine.var_map, engine.n, solver=solver)

    t_start = time.perf_counter()
    status = "SUCCESS"

    try:
        trace = agent.solve_all(engine)
        runtime = time.perf_counter() - t_start
        won = engine.is_game_won()
        if not won:
            status = "STUCK / UNPROVABLE"
    except Exception as e:
        runtime = time.perf_counter() - t_start
        status = f"FAILED: {e}"

    # Peak clauses at the final state
    final_kb = build_kb(
        list(engine.revealed_clues.values()),
        engine.revealed_statuses,
        engine.var_map,
        engine.n
    )
    final_clauses = len(final_kb.clauses)

    return {
        "puzzle_file": puzzle_name,
        "grid_size": f"{n}x{n}",
        "n": n,
        "status": status,
        "primary_vars": num_primary,
        "aux_vars": num_aux,
        "total_vars": total_vars,
        "initial_clauses": initial_clauses,
        "final_clauses": final_clauses,
        "sat_calls": solver.total_calls,
        "decisions": solver.cum_decisions,
        "propagations": solver.cum_propagations,
        "backtracks": solver.cum_backtracks,
        "deduction_steps": trace.total_steps() if 'trace' in locals() else 0,
        "total_runtime_ms": round(runtime * 1000, 2),
        "sat_runtime_ms": round(solver.cum_sat_runtime * 1000, 2)
    }


def generate_plots(results: List[Dict[str, Any]], output_path: str):
    """Generates benchmark visualization charts using matplotlib."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed, skipping plot generation.")
        return

    labels = [r["puzzle_file"].replace(".json", "") for r in results]
    runtimes = [r["total_runtime_ms"] for r in results]
    sat_calls = [r["sat_calls"] for r in results]
    propagations = [r["propagations"] for r in results]
    clauses = [r["final_clauses"] for r in results]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Griductive Solver - Empirical Benchmark Evaluation", fontsize=16, fontweight='bold')

    # 1. Total Runtime
    ax1 = axes[0, 0]
    bars1 = ax1.bar(labels, runtimes, color='steelblue', edgecolor='black')
    ax1.set_title("Total Deduction Runtime (ms)", fontweight='bold')
    ax1.set_ylabel("Milliseconds")
    ax1.tick_params(axis='x', rotation=25)
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.1, f"{yval:.1f}ms", ha='center', va='bottom', fontsize=8)

    # 2. Number of SAT Calls
    ax2 = axes[0, 1]
    bars2 = ax2.bar(labels, sat_calls, color='coral', edgecolor='black')
    ax2.set_title("Total DPLL SAT Queries", fontweight='bold')
    ax2.set_ylabel("Query Count")
    ax2.tick_params(axis='x', rotation=25)
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.5, f"{int(yval)}", ha='center', va='bottom', fontsize=8)

    # 3. Unit Propagations
    ax3 = axes[1, 0]
    bars3 = ax3.bar(labels, propagations, color='mediumseagreen', edgecolor='black')
    ax3.set_title("DPLL Unit Propagations Performed", fontweight='bold')
    ax3.set_ylabel("Propagations")
    ax3.tick_params(axis='x', rotation=25)
    for bar in bars3:
        yval = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2.0, yval + 0.5, f"{int(yval)}", ha='center', va='bottom', fontsize=8)

    # 4. Final Knowledge Base Clauses
    ax4 = axes[1, 1]
    bars4 = ax4.bar(labels, clauses, color='mediumpurple', edgecolor='black')
    ax4.set_title("Total CNF Clauses in Final KB", fontweight='bold')
    ax4.set_ylabel("Clause Count")
    ax4.tick_params(axis='x', rotation=25)
    for bar in bars4:
        yval = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2.0, yval + 0.5, f"{int(yval)}", ha='center', va='bottom', fontsize=8)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Benchmark chart saved to {output_path}")


def main():
    puzzles_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "puzzles"))
    puzzle_files = sorted(glob.glob(os.path.join(puzzles_dir, "*.json")))

    if not puzzle_files:
        print(f"No puzzles found in {puzzles_dir}")
        return

    print("=" * 90)
    print("GRIDUCTIVE SOLVER: RUNNING BENCHMARK EVALUATIONS")
    print("=" * 90)

    results = []
    for ppath in puzzle_files:
        print(f"Evaluating {os.path.basename(ppath)}...")
        res = run_single_benchmark(ppath)
        results.append(res)

    # Print summary table
    print("\n" + "=" * 90)
    print(f"{'Puzzle':<20} | {'Grid':<6} | {'Status':<10} | {'Vars':<6} | {'Clauses':<8} | {'SAT Calls':<10} | {'Dec/Prop/Bk':<12} | {'Time (ms)':<10}")
    print("-" * 90)
    for r in results:
        dec_prop = f"{r['decisions']}/{r['propagations']}/{r['backtracks']}"
        print(f"{r['puzzle_file']:<20} | {r['grid_size']:<6} | {r['status']:<10} | {r['total_vars']:<6} | {r['final_clauses']:<8} | {r['sat_calls']:<10} | {dec_prop:<12} | {r['total_runtime_ms']:<10}")
    print("=" * 90)

    # Export to CSV
    csv_path = os.path.join(os.path.dirname(__file__), "benchmark_results.csv")
    fieldnames = [
        "puzzle_file", "grid_size", "n", "status",
        "primary_vars", "aux_vars", "total_vars",
        "initial_clauses", "final_clauses",
        "sat_calls", "decisions", "propagations", "backtracks",
        "deduction_steps", "total_runtime_ms", "sat_runtime_ms"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\nCSV results saved to {csv_path}")

    # Generate charts
    plot_path = os.path.join(os.path.dirname(__file__), "benchmark_plots.png")
    generate_plots(results, plot_path)


if __name__ == "__main__":
    main()

