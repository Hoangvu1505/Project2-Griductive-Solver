"""
Main Entry Point for Griductive Project.
Supports:
- Web GUI Mode (default): python main.py [--port 8000]
- CLI Solve Mode: python main.py --cli [--puzzle path/to/puzzle.json]
- Benchmark Mode: python main.py --benchmark
- Test Mode: python main.py --test
"""

import sys
import os
import argparse
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def run_web_gui(port: int = 8000):
    """Launches the React Web GUI server and opens browser."""
    from gui.app import launch_gui
    launch_gui(port=port, open_browser=True)


def run_cli_solve(puzzle_path: str):
    """Runs the Logic Agent from command line and outputs deduction trace."""
    from engine.game_engine import GameEngine
    from agent.agent import LogicAgent
    from agent.uniqueness import check_uniqueness_dpll

    if not os.path.exists(puzzle_path):
        print(f"Error: Puzzle file not found at '{puzzle_path}'")
        sys.exit(1)

    print("=" * 80)
    print(f"GRIDUCTIVE CLI SOLVER: {os.path.basename(puzzle_path)}")
    print("=" * 80)

    engine = GameEngine()
    engine.load_from_json(puzzle_path)

    # 1. Check Uniqueness
    is_unique, msg, _ = check_uniqueness_dpll(engine.get_all_clues(), engine.var_map, engine.n)
    print(f"[*] Complete Clue Set Uniqueness Check: {is_unique} ({msg})")

    # 2. Run Deductive Logic Agent
    agent = LogicAgent(engine.var_map, engine.n)
    trace = agent.solve_all(engine)

    print("\n" + "=" * 80)
    print("DEDUCTION TRACE:")
    print("=" * 80)
    print(trace.to_text())

    print("\n" + "=" * 80)
    print("FINAL RESULT:")
    print(f"[*] Puzzle Solved: {engine.is_game_won()}")
    print(f"[*] Total Deduction Steps: {trace.total_steps()}")
    print(f"[*] Total SAT Queries Executed: {trace.total_sat_queries()}")
    print("=" * 80)


def run_benchmarks():
    """Executes the benchmark evaluation experiments."""
    from experiments.run_benchmarks import main as benchmark_main
    benchmark_main()


def run_tests():
    """Discovers and runs all unit tests."""
    print("=" * 80)
    print("RUNNING UNIT TESTS (DPLL, CNF ENCODER, EVALUATOR)")
    print("=" * 80)
    loader = unittest.TestLoader()
    suite = loader.discover("tests")
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    sys.exit(0 if res.wasSuccessful() else 1)


def main():
    parser = argparse.ArgumentParser(description="Griductive Propositional SAT Solver & GUI")
    parser.add_argument("--port", type=int, default=8000, help="Port for web server (default: 8000)")
    parser.add_argument("--cli", action="store_true", help="Run solver in command-line mode without GUI")
    parser.add_argument("--puzzle", type=str, default=None, help="Path to puzzle JSON file")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark experiments on all puzzles")
    parser.add_argument("--test", action="store_true", help="Run unit test suite")

    args = parser.parse_args()

    if args.test:
        run_tests()
    elif args.benchmark:
        run_benchmarks()
    elif args.cli:
        puzzle = args.puzzle or os.path.join("puzzles", "puzzle_3x3_1.json")
        run_cli_solve(puzzle)
    else:
        run_web_gui(args.port)


if __name__ == "__main__":
    main()
