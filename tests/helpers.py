"""Pomocnicze funkcje do testów Bottleneck TSP."""

from __future__ import annotations

import itertools
import math
import random
from typing import List, Sequence, Set, Tuple

from bottleneck_tsp import (
    build_adjacency,
    get_mst_edges,
    prim_mst,
    solve_bottleneck_tsp,
)


def cycle_bottleneck(cycle: Sequence[int], W: List[List[float]]) -> float:
    return max(W[cycle[i]][cycle[i + 1]] for i in range(len(cycle) - 1))


def is_hamiltonian_cycle(cycle: Sequence[int], n: int) -> bool:
    if len(cycle) != n + 1:
        return False
    if cycle[0] != cycle[-1]:
        return False
    inner = list(cycle[:-1])
    return sorted(inner) == list(range(n)) and len(set(inner)) == n


def validate_weight_matrix(W: List[List[float]]) -> None:
    n = len(W)
    for i in range(n):
        if len(W[i]) != n:
            raise ValueError(f"Macierz nie jest kwadratowa w wierszu {i}")
        if W[i][i] != 0:
            raise ValueError(f"Diagonalna waga [{i}][{i}] != 0")
        for j in range(n):
            if W[i][j] != W[j][i]:
                raise ValueError(f"Macierz niesymetryczna: W[{i}][{j}] != W[{j}][{i}]")
            if W[i][j] < 0:
                raise ValueError("Ujemne wagi niedozwolone")


def satisfies_triangle_inequality(W: List[List[float]], eps: float = 1e-9) -> bool:
    n = len(W)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if W[i][k] > W[i][j] + W[j][k] + eps:
                    return False
    return True


def mst_max_edge_weight(parent: List[int], W: List[List[float]]) -> float:
    n = len(parent)
    best = 0.0
    for v in range(1, n):
        u = parent[v]
        best = max(best, W[u][v])
    return best


def brute_force_optimal_bottleneck(n: int, W: List[List[float]]) -> Tuple[float, List[int]]:
    """Pełne przeszukiwanie cykli Hamiltona (start w 0) — tylko małe n."""
    if n == 1:
        return 0.0, [0, 0]
    if n == 2:
        return W[0][1], [0, 1, 0]

    best = math.inf
    best_cycle: List[int] = []
    for perm in itertools.permutations(range(1, n)):
        cycle = [0, *perm, 0]
        b = cycle_bottleneck(cycle, W)
        if b < best:
            best = b
            best_cycle = cycle
    return best, best_cycle


def metric_matrix_from_points(points: List[Tuple[float, float]]) -> List[List[float]]:
    n = len(points)
    W = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            d = math.hypot(dx, dy)
            W[i][j] = W[j][i] = d
    return W


def random_metric_matrix(n: int, seed: int | None = None) -> List[List[float]]:
    rng = random.Random(seed)
    points = [(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(n)]
    return metric_matrix_from_points(points)


def doc_example_matrix() -> List[List[float]]:
    return [
        [0, 3, 5, 2],
        [3, 0, 4, 6],
        [5, 4, 0, 1],
        [2, 6, 1, 0],
    ]


def solve(n: int, W: List[List[float]]):
    cycle, bottleneck, mst_edges = solve_bottleneck_tsp(n, W)
    parent = prim_mst(n, W)
    return {
        "cycle": cycle,
        "bottleneck": bottleneck,
        "mst_edges": mst_edges,
        "parent": parent,
        "mst_max": mst_max_edge_weight(parent, W),
    }
