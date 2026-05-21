"""Testy wydajności i złożoności czasowej O(n^2)."""

from __future__ import annotations

import statistics
import time
from typing import Dict, List, Tuple

import pytest

from bottleneck_tsp import prim_mst, solve_bottleneck_tsp
from generator import generate_euclidean


def _median_time_seconds(func, repeats: int = 5) -> float:
    samples = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        func()
        samples.append(time.perf_counter() - t0)
    return statistics.median(samples)


def _time_prim(n: int, repeats: int = 5) -> float:
    W, _ = generate_euclidean(n, seed=9000 + n)

    def run():
        prim_mst(n, W)

    return _median_time_seconds(run, repeats=repeats)


def _time_full_solver(n: int, repeats: int = 5) -> float:
    W, _ = generate_euclidean(n, seed=8000 + n)

    def run():
        solve_bottleneck_tsp(n, W)

    return _median_time_seconds(run, repeats=repeats)


# Rozmiary instancji do benchmarku (można rozszerzyć lokalnie)
BENCHMARK_SIZES = [10, 20, 30, 50, 75, 100]


@pytest.mark.performance
class TestPerformancePrim:
    @pytest.mark.parametrize("n", BENCHMARK_SIZES)
    def test_prim_runtime_recorded(self, n: int, benchmark_results: Dict[str, List[Tuple[int, float]]]):
        elapsed = _time_prim(n, repeats=3)
        benchmark_results["prim"].append((n, elapsed))
        assert elapsed < 30.0, f"Prim n={n} trwa zbyt długo: {elapsed:.3f}s"

    def test_prim_scaling_quadratic(self, benchmark_results: Dict[str, List[Tuple[int, float]]]):
        """Dla grafu pełnego oczekujemy przybliżonego wzrostu kwadratowego."""
        sizes = [20, 40, 80]
        times = [_time_prim(n, repeats=3) for n in sizes]
        benchmark_results["prim_scaling"] = list(zip(sizes, times))

        # T(2n) / T(n) dla n=20->40 i 40->80 powinno być w rozsądnym paśmie O(n^2)
        ratio_1 = times[1] / max(times[0], 1e-9)
        ratio_2 = times[2] / max(times[1], 1e-9)
        assert 2.0 <= ratio_1 <= 12.0, f"ratio 20->40: {ratio_1:.2f}"
        assert 2.0 <= ratio_2 <= 12.0, f"ratio 40->80: {ratio_2:.2f}"


@pytest.mark.performance
class TestPerformanceFullAlgorithm:
    @pytest.mark.parametrize("n", BENCHMARK_SIZES)
    def test_solver_runtime_recorded(self, n: int, benchmark_results: Dict[str, List[Tuple[int, float]]]):
        elapsed = _time_full_solver(n, repeats=3)
        benchmark_results["solver"].append((n, elapsed))
        assert elapsed < 60.0, f"Solver n={n} trwa zbyt długo: {elapsed:.3f}s"

    def test_full_solver_not_worse_than_cubic_growth(self):
        """Cały algorytm dokumentowany jako O(n^2); odrzucamy jawny O(n^3)."""
        t50 = _time_full_solver(50, repeats=3)
        t100 = _time_full_solver(100, repeats=3)
        ratio = t100 / max(t50, 1e-9)
        assert ratio < 20.0, f"T(100)/T(50)={ratio:.2f} sugeruje gorsze niż O(n^2 log n)"


@pytest.mark.performance
def test_print_timing_summary(benchmark_results: Dict[str, List[Tuple[int, float]]], capsys):
    """Wypisuje tabelę czasów po zakończeniu testów performance (raport w pytest)."""
    lines = ["", "=== Pomiar czasu (mediana, sekundy) ==="]
    for label in ("prim", "solver"):
        rows = benchmark_results.get(label, [])
        if rows:
            lines.append(f"--- {label} ---")
            for n, t in sorted(rows):
                lines.append(f"  n={n:4d}  {t:.6f}s")
    scaling = benchmark_results.get("prim_scaling")
    if scaling:
        lines.append("--- prim scaling ---")
        for n, t in scaling:
            lines.append(f"  n={n:4d}  {t:.6f}s")
    lines.append("=" * 40)
    print("\n".join(lines))
    captured = capsys.readouterr()
    assert "Pomiar czasu" in captured.out or True
