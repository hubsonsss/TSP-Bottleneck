"""Testy poprawności algorytmu Bottleneck TSP."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from bottleneck_tsp import (
    build_adjacency,
    find_path_recursive,
    get_mst_edges,
    get_subtree_vertices,
    load_from_file,
    prim_mst,
    solve_bottleneck_tsp,
)
from tests.helpers import (
    brute_force_optimal_bottleneck,
    cycle_bottleneck,
    doc_example_matrix,
    is_hamiltonian_cycle,
    mst_max_edge_weight,
    random_metric_matrix,
    satisfies_triangle_inequality,
    solve,
    validate_weight_matrix,
)


class TestInputOutput:
    def test_load_doc_example_format(self, tmp_path: Path):
        content = "4\n0 3 5 2\n3 0 4 6\n5 4 0 1\n2 6 1 0\n"
        p = tmp_path / "in.txt"
        p.write_text(content, encoding="utf-8")
        n, W = load_from_file(str(p))
        assert n == 4
        assert W == doc_example_matrix()

    def test_project_input_file(self):
        root = Path(__file__).resolve().parents[1]
        inp = root / "input.txt"
        if not inp.exists():
            pytest.skip("brak input.txt w repozytorium")
        n, W = load_from_file(str(inp))
        assert n == 10
        validate_weight_matrix(W)
        assert satisfies_triangle_inequality(W)


class TestPrimMST:
    @pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 8, 12])
    def test_mst_has_n_minus_one_edges(self, n: int):
        W = random_metric_matrix(n, seed=n)
        parent = prim_mst(n, W)
        edges = get_mst_edges(parent, n)
        if n == 1:
            assert edges == []
        else:
            assert len(edges) == n - 1

    @pytest.mark.parametrize("n", [3, 4, 6, 10])
    def test_mst_is_connected_tree(self, n: int):
        W = random_metric_matrix(n, seed=100 + n)
        parent = prim_mst(n, W)
        adj = build_adjacency(parent, n)
        for v in range(1, n):
            assert parent[v] != -1
        # BFS z 0 odwiedza wszystkie wierzchołki
        seen = get_subtree_vertices(adj, 0)
        assert len(seen) == n


class TestHamiltonianCycle:
    @pytest.mark.parametrize("n", [3, 4, 5, 6, 8, 10, 15])
    def test_solution_is_valid_hamiltonian_cycle(self, n: int):
        W = random_metric_matrix(n, seed=200 + n)
        cycle, bottleneck, *_ = solve_bottleneck_tsp(n, W)
        assert is_hamiltonian_cycle(cycle, n)
        assert bottleneck == pytest.approx(cycle_bottleneck(cycle, W))

    def test_reported_bottleneck_matches_cycle(self):
        W = doc_example_matrix()
        cycle, reported, _ = solve_bottleneck_tsp(4, W)
        assert reported == pytest.approx(cycle_bottleneck(cycle, W))

    def test_single_vertex(self):
        cycle, b = solve_bottleneck_tsp(1, [[0]])
        assert cycle == [0, 0]
        assert b == 0

    def test_two_vertices(self):
        W = [[0, 7], [7, 0]]
        cycle, b = solve_bottleneck_tsp(2, W)
        assert is_hamiltonian_cycle(cycle, 2)
        assert b == 7


class TestThreeApproximation:
    """Weryfikacja gwarancji 3-aproksymacji (dowód w dokumentacji)."""

    @pytest.mark.parametrize("n", range(3, 9))
    def test_bottleneck_at_most_three_times_optimal(self, n: int):
        W = random_metric_matrix(n, seed=300 + n)
        opt, _ = brute_force_optimal_bottleneck(n, W)
        cycle, approx, *_ = solve_bottleneck_tsp(n, W)
        assert cycle_bottleneck(cycle, W) == approx
        assert approx <= 3.0 * opt + 1e-9

    def test_doc_example_within_factor_three(self):
        W = doc_example_matrix()
        opt, _ = brute_force_optimal_bottleneck(4, W)
        assert opt == pytest.approx(4)
        _, approx, _ = solve_bottleneck_tsp(4, W)
        assert approx <= 3 * opt

    @pytest.mark.parametrize("n", range(3, 9))
    def test_mst_heaviest_edge_not_greater_than_optimal(self, n: int):
        W = random_metric_matrix(n, seed=400 + n)
        opt, _ = brute_force_optimal_bottleneck(n, W)
        parent = prim_mst(n, W)
        mst_max = mst_max_edge_weight(parent, W)
        assert mst_max <= opt + 1e-9

    @pytest.mark.parametrize("n", range(3, 9))
    def test_solution_bottleneck_at_most_three_times_mst_max(self, n: int):
        W = random_metric_matrix(n, seed=500 + n)
        result = solve(n, W)
        assert result["bottleneck"] <= 3.0 * result["mst_max"] + 1e-9


class TestRecursivePath:
    def test_three_vertex_base_case(self):
        W = [[0, 1, 2], [1, 0, 3], [2, 3, 0]]
        parent = prim_mst(3, W)
        adj = build_adjacency(parent, 3)
        path = find_path_recursive(adj, {0, 1, 2}, 0, 2)
        assert set(path) == {0, 1, 2}
        assert path[0] == 0 and path[-1] == 2


class TestRegressionProjectInput:
    def test_input_txt_runs_and_is_valid(self):
        root = Path(__file__).resolve().parents[1]
        inp = root / "input.txt"
        if not inp.exists():
            pytest.skip("brak input.txt")
        n, W = load_from_file(str(inp))
        cycle, bottleneck, mst_edges = solve_bottleneck_tsp(n, W)
        assert is_hamiltonian_cycle(cycle, n)
        assert len(mst_edges) == n - 1
        assert bottleneck == pytest.approx(cycle_bottleneck(cycle, W))
        # Znany wynik z output.txt w repo (może się zmienić przy innej krawędzi startowej MST)
        assert bottleneck <= 37  # górna granica z macierzy wejściowej
