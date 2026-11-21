"""
Bộ công cụ chạy thực nghiệm và đánh giá hiệu năng (Benchmark Suite) cho hệ thống Griductive.
Đánh giá bộ giải DPLL SAT Solver và Deductive Logic Agent trên các bộ puzzle 3x3, 4x4 và 5x5.

Ghi nhận đầy đủ 6 nhóm chỉ số bắt buộc theo Mục 4.5 của đề bài:
1. Số lượng biến chính (primary_vars) và biến phụ (aux_vars)
2. Số lượng mệnh đề CNF (initial_clauses, final_clauses)
3. Tổng số lần gọi bộ giải SAT (sat_calls)
4. Số lần quyết định (decisions), lan truyền đơn vị (propagations) và quay lui (backtracks)
5. Số bước suy diễn (deduction_steps)
6. Thời gian chạy tổng thể và thời gian riêng của SAT (total_runtime_ms, sat_runtime_ms)

Hỗ trợ cơ chế giới hạn thời gian (timeout), giữ lại đầy đủ các trường hợp thất bại/quá giờ
trong báo cáo, xuất bảng kết quả CSV và vẽ biểu đồ trực quan.
"""

import argparse
import csv
import glob
import os
import sys
import time
from typing import Any, Dict, List, Optional

# Đảm bảo thư mục gốc của project nằm trong sys.path để import các module nội bộ
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.agent import LogicAgent
from engine.game_engine import GameEngine
from logic.kb import build_kb
from sat.dpll import DPLLSolver


class InstrumentedDPLLSolver(DPLLSolver):
    """
    Lớp kế thừa từ DPLLSolver nhằm:
    1. Cộng dồn thống kê (số lần gọi, decisions, propagations, backtracks, runtime)
       xuyên suốt nhiều truy vấn SAT của một màn chơi.
    2. Áp đặt mốc thời gian tối đa (deadline/timeout) để ngắt tìm kiếm khi chạy quá lâu.
    """

    def __init__(self, deadline: Optional[float] = None):
        """Khởi tạo bộ giải có gắn bộ đếm cộng dồn và mốc thời gian kết thúc (deadline)."""
        super().__init__()
        self.deadline: Optional[float] = deadline
        self.total_calls: int = 0
        self.cum_decisions: int = 0
        self.cum_propagations: int = 0
        self.cum_backtracks: int = 0
        self.cum_sat_runtime: float = 0.0

    def _check_timeout(self) -> None:
        """Kiểm tra đồng hồ hệ thống; ném TimeoutError ngay nếu đã vượt quá deadline."""
        if self.deadline is not None and time.perf_counter() > self.deadline:
            raise TimeoutError("Benchmark time limit exceeded during DPLL search.")

    def _dpll(self, clauses, assignment):
        """Ghi đè hàm đệ quy _dpll để kiểm tra timeout tại mỗi nút trong cây tìm kiếm."""
        self._check_timeout()
        return super()._dpll(clauses, assignment)

    def solve(self, clauses, num_vars=None, assumptions=None):
        """
        Ghi đè hàm solve() để đếm số truy vấn SAT, cộng dồn chỉ số hiệu năng
        và đảm bảo vẫn lưu lại thống kê một phần ngay cả khi bị ngắt do TimeoutError.
        """
        self._check_timeout()
        self.total_calls += 1
        call_start = time.perf_counter()
        try:
            is_sat, model, stats = super().solve(clauses, num_vars, assumptions)
            self.cum_decisions += stats.decisions
            self.cum_propagations += stats.propagations
            self.cum_backtracks += stats.backtracks
            self.cum_sat_runtime += stats.runtime
            return is_sat, model, stats
        except TimeoutError:
            # Vẫn cộng dồn thống kê đã thực hiện được trước thời điểm quá giờ
            self.cum_decisions += self.stats.decisions
            self.cum_propagations += self.stats.propagations
            self.cum_backtracks += self.stats.backtracks
            self.cum_sat_runtime += time.perf_counter() - call_start
            raise


def run_single_benchmark(puzzle_path: str, timeout_sec: float = 30.0) -> Dict[str, Any]:
    """
    Chạy thực nghiệm hoàn chỉnh trên một file puzzle JSON duy nhất.

    Tham số:
        puzzle_path: Đường dẫn đến file cấu hình puzzle (.json).
        timeout_sec: Giới hạn thời gian chạy tối đa cho puzzle này (tính bằng giây).

    Trả về:
        Dictionary chứa toàn bộ 16 trường thông tin (tên file, kích thước, trạng thái,
        biến chính/phụ, số mệnh đề, thống kê DPLL, số bước suy diễn và thời gian chạy).
    """
    engine = GameEngine()
    engine.load_from_json(puzzle_path)

    puzzle_name = os.path.basename(puzzle_path)
    n = engine.n

    # Đo số lượng mệnh đề CNF của cơ sở tri thức ban đầu (trước khi suy diễn)
    initial_kb = build_kb(
        list(engine.revealed_clues.values()),
        engine.revealed_statuses,
        engine.var_map,
        engine.n,
    )
    initial_clauses = len(initial_kb.clauses)

    # Thiết lập mốc timeout và khởi tạo bộ giải + tác tử logic
    t_start = time.perf_counter()
    deadline = t_start + timeout_sec if timeout_sec and timeout_sec > 0 else None
    solver = InstrumentedDPLLSolver(deadline=deadline)
    agent = LogicAgent(engine.var_map, engine.n, solver=solver)

    status = "SUCCESS"
    deduction_steps = 0

    # Chạy vòng lặp suy diễn tự động và bắt đầy đủ các trạng thái lỗi / quá giờ / bế tắc
    try:
        trace = agent.solve_all(engine)
        runtime = time.perf_counter() - t_start
        deduction_steps = trace.total_steps()
        if not engine.is_game_won():
            status = "STUCK / UNPROVABLE"
    except TimeoutError:
        runtime = time.perf_counter() - t_start
        deduction_steps = agent.trace.total_steps()
        status = "TIMEOUT"
    except Exception as e:
        runtime = time.perf_counter() - t_start
        deduction_steps = agent.trace.total_steps()
        status = f"FAILED: {e}"

    # Xây dựng lại KB ở trạng thái cuối để đo chính xác số mệnh đề đỉnh và số biến phụ đã cấp phát
    final_kb = build_kb(
        list(engine.revealed_clues.values()),
        engine.revealed_statuses,
        engine.var_map,
        engine.n,
    )
    kb_stats = final_kb.get_stats()

    return {
        "puzzle_file": puzzle_name,
        "grid_size": f"{n}x{n}",
        "n": n,
        "status": status,
        "primary_vars": kb_stats["num_primary_vars"],
        "aux_vars": kb_stats["num_aux_vars"],
        "total_vars": kb_stats["total_vars"],
        "initial_clauses": initial_clauses,
        "final_clauses": kb_stats["num_clauses"],
        "sat_calls": solver.total_calls,
        "decisions": solver.cum_decisions,
        "propagations": solver.cum_propagations,
        "backtracks": solver.cum_backtracks,
        "deduction_steps": deduction_steps,
        "total_runtime_ms": round(runtime * 1000, 2),
        "sat_runtime_ms": round(solver.cum_sat_runtime * 1000, 2),
    }


def generate_plots(results: List[Dict[str, Any]], output_path: str) -> None:
    """
    Vẽ 4 biểu đồ cột so sánh hiệu năng giữa các puzzle bằng matplotlib và lưu ra file ảnh PNG:
    1. Tổng thời gian suy diễn (ms)
    2. Tổng số lần gọi truy vấn DPLL SAT
    3. Tổng số bước lan truyền đơn vị (Unit Propagations)
    4. Tổng số mệnh đề CNF trong cơ sở tri thức cuối cùng

    Các bài bị lỗi hoặc quá giờ (không đạt SUCCESS) vẫn được giữ lại và tô màu đỏ (crimson).
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed, skipping plot generation.")
        return

    # Gắn nhãn trạng thái bổ sung (ví dụ [TIMEOUT]) cho những bài không giải thành công
    labels = [
        r["puzzle_file"].replace(".json", "")
        + ("" if r["status"] == "SUCCESS" else f"\n[{r['status'].split(':')[0]}]")
        for r in results
    ]
    runtimes = [r["total_runtime_ms"] for r in results]
    sat_calls = [r["sat_calls"] for r in results]
    propagations = [r["propagations"] for r in results]
    clauses = [r["final_clauses"] for r in results]

    def bar_colors(default_color: str) -> List[str]:
        """Trả về màu mặc định cho bài SUCCESS và màu đỏ (crimson) cho bài lỗi/timeout."""
        return [
            default_color if r["status"] == "SUCCESS" else "crimson"
            for r in results
        ]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Griductive Solver - Empirical Benchmark Evaluation", fontsize=16, fontweight="bold")

    # Biểu đồ 1: Tổng thời gian chạy (ms)
    ax1 = axes[0, 0]
    bars1 = ax1.bar(labels, runtimes, color=bar_colors("steelblue"), edgecolor="black")
    ax1.set_title("Total Deduction Runtime (ms)", fontweight="bold")
    ax1.set_ylabel("Milliseconds")
    ax1.tick_params(axis="x", rotation=25)
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.1, f"{yval:.1f}ms", ha="center", va="bottom", fontsize=8)

    # Biểu đồ 2: Tổng số lần gọi truy vấn SAT
    ax2 = axes[0, 1]
    bars2 = ax2.bar(labels, sat_calls, color=bar_colors("coral"), edgecolor="black")
    ax2.set_title("Total DPLL SAT Queries", fontweight="bold")
    ax2.set_ylabel("Query Count")
    ax2.tick_params(axis="x", rotation=25)
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.5, f"{int(yval)}", ha="center", va="bottom", fontsize=8)

    # Biểu đồ 3: Tổng số lần lan truyền đơn vị
    ax3 = axes[1, 0]
    bars3 = ax3.bar(labels, propagations, color=bar_colors("mediumseagreen"), edgecolor="black")
    ax3.set_title("DPLL Unit Propagations Performed", fontweight="bold")
    ax3.set_ylabel("Propagations")
    ax3.tick_params(axis="x", rotation=25)
    for bar in bars3:
        yval = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.5, f"{int(yval)}", ha="center", va="bottom", fontsize=8)

    # Biểu đồ 4: Số lượng mệnh đề CNF trong KB cuối cùng
    ax4 = axes[1, 1]
    bars4 = ax4.bar(labels, clauses, color=bar_colors("mediumpurple"), edgecolor="black")
    ax4.set_title("Total CNF Clauses in Final KB", fontweight="bold")
    ax4.set_ylabel("Clause Count")
    ax4.tick_params(axis="x", rotation=25)
    for bar in bars4:
        yval = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.5, f"{int(yval)}", ha="center", va="bottom", fontsize=8)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Benchmark chart saved to {output_path}")


def main() -> None:
    """
    Điểm vào chính của script benchmark:
    1. Đọc tham số dòng lệnh (--timeout), dùng parse_known_args để tương thích khi gọi qua main.py --benchmark.
    2. Quét và chạy thực nghiệm tuần tự trên toàn bộ các file puzzle trong thư mục puzzles/.
    3. In bảng tổng hợp ra terminal, xuất file experiments/benchmark_results.csv và vẽ biểu đồ PNG.
    """
    parser = argparse.ArgumentParser(description="Run Griductive SAT/DPLL benchmarks.")
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Timeout per puzzle in seconds (default: 30.0).",
    )
    # Dùng parse_known_args() để bỏ qua cờ --benchmark khi được gọi gián tiếp từ main.py
    args, _ = parser.parse_known_args()

    puzzles_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "puzzles"))
    puzzle_files = sorted(glob.glob(os.path.join(puzzles_dir, "*.json")))

    if not puzzle_files:
        print(f"No puzzles found in {puzzles_dir}")
        return

    print("=" * 98)
    print(f"GRIDUCTIVE SOLVER: RUNNING BENCHMARK EVALUATIONS (timeout={args.timeout}s)")
    print("=" * 98)

    # Chạy lần lượt trên cùng một tập puzzle cố định để đảm bảo công bằng khi so sánh
    results = []
    for ppath in puzzle_files:
        print(f"Evaluating {os.path.basename(ppath)}...")
        res = run_single_benchmark(ppath, timeout_sec=args.timeout)
        results.append(res)

    # In bảng tóm tắt kết quả ra màn hình console
    print("\n" + "=" * 98)
    print(
        f"{'Puzzle':<20} | {'Grid':<5} | {'Status':<12} | {'Vars(P+A)':<9} | "
        f"{'Clauses':<7} | {'SAT Calls':<9} | {'Dec/Prop/Bk':<12} | {'Time (ms)':<9}"
    )
    print("-" * 98)
    for r in results:
        dec_prop = f"{r['decisions']}/{r['propagations']}/{r['backtracks']}"
        vars_str = f"{r['primary_vars']}+{r['aux_vars']}"
        print(
            f"{r['puzzle_file']:<20} | {r['grid_size']:<5} | {r['status'][:12]:<12} | "
            f"{vars_str:<9} | {r['final_clauses']:<7} | {r['sat_calls']:<9} | "
            f"{dec_prop:<12} | {r['total_runtime_ms']:<9}"
        )
    print("=" * 98)

    # Xuất toàn bộ dữ liệu thực nghiệm ra file CSV
    csv_path = os.path.join(os.path.dirname(__file__), "benchmark_results.csv")
    fieldnames = [
        "puzzle_file", "grid_size", "n", "status",
        "primary_vars", "aux_vars", "total_vars",
        "initial_clauses", "final_clauses",
        "sat_calls", "decisions", "propagations", "backtracks",
        "deduction_steps", "total_runtime_ms", "sat_runtime_ms",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\nCSV results saved to {csv_path}")

    # Vẽ và lưu biểu đồ trực quan
    plot_path = os.path.join(os.path.dirname(__file__), "benchmark_plots.png")
    generate_plots(results, plot_path)


if __name__ == "__main__":
    main()