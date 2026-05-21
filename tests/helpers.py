"""Pomocnicze funkcje do testów Bottleneck TSP."""

from __future__ import annotations

from typing import List, Sequence

from bottleneck_tsp import (
    build_adjacency,
    get_mst_edges,
    prim_mst,
    solve_bottleneck_tsp,
)


def cycle_bottleneck(cycle: Sequence[int], W) -> float:
    return max(W[cycle[i]][cycle[i + 1]] for i in range(len(cycle) - 1))


def is_hamiltonian_cycle(cycle: Sequence[int], n: int) -> bool:
    if len(cycle) != n + 1:
        return False
    if cycle[0] != cycle[-1]:
        return False
    inner = list(cycle[:-1])
    return sorted(inner) == list(range(n)) and len(set(inner)) == n


def validate_weight_matrix(W) -> None:
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


def satisfies_triangle_inequality(W, eps: float = 1e-9) -> bool:
    n = len(W)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if W[i][k] > W[i][j] + W[j][k] + eps:
                    return False
    return True


def mst_max_edge_weight(parent: List[int], W) -> float:
    n = len(parent)
    best = 0.0
    for v in range(1, n):
        u = parent[v]
        best = max(best, W[u][v])
    return best


def doc_example_matrix() -> List[List[float]]:
    return [
        [0, 3, 5, 2],
        [3, 0, 4, 6],
        [5, 4, 0, 1],
        [2, 6, 1, 0],
    ]


def solve(n: int, W):
    cycle, bottleneck, mst_edges = solve_bottleneck_tsp(n, W)
    parent = prim_mst(n, W)
    return {
        "cycle": cycle,
        "bottleneck": bottleneck,
        "mst_edges": mst_edges,
        "parent": parent,
        "mst_max": mst_max_edge_weight(parent, W),
    }
