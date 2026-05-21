"""
Generowanie wykresów z wyników benchmarków Bottleneck TSP
Algorytmy zaawansowane, projekt 2025/2026

Hubert Sobociński, Sandra Adamiec, Piotr Tyrakowski
"""

import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt

from bottleneck_tsp import load_from_file, solve_bottleneck_tsp, get_mst_edges, prim_mst
from generator import generate_euclidean


def load_timing_results(filepath):
    """Wczytuje wyniki pomiarów czasowych z CSV."""
    data = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split(',')
            if len(parts) < 3:
                continue
            n = int(parts[0])
            t = float(parts[2])
            if n not in data:
                data[n] = []
            data[n].append(t)
    return data



def plot_time_complexity(timing_data, out_dir):
    """Wykres: zmierzone czasy vs teoretyczna złożoność O(n^3)."""
    sizes = sorted(timing_data.keys())
    means = [np.mean(timing_data[n]) for n in sizes]
    stds = [np.std(timing_data[n]) for n in sizes]

    sizes_arr = np.array(sizes, dtype=float)
    means_arr = np.array(means)

    c = np.sum(means_arr * sizes_arr ** 3) / np.sum(sizes_arr ** 6)
    fitted = c * sizes_arr ** 3

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.errorbar(sizes, means, yerr=stds, fmt='o-', color='blue', capsize=4,
                label='Zmierzony średni czas', linewidth=2, markersize=6)
    ax.plot(sizes, fitted, '--', color='red', linewidth=2,
            label=f'Dopasowana krzywa $c \\cdot n^3$ (c={c:.2e})')
    ax.set_xlabel('Rozmiar instancji (n)', fontsize=12)
    ax.set_ylabel('Czas wykonania [s]', fontsize=12)
    ax.set_title('Czas wykonania algorytmu 3-aproksymacji Bottleneck TSP', fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    filepath = os.path.join(out_dir, 'time_complexity.png')
    fig.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Zapisano: {filepath}")


def plot_time_loglog(timing_data, out_dir):
    """Wykres log-log: potwierdzenie złożoności wielomianowej."""
    sizes = sorted(timing_data.keys())
    means = [np.mean(timing_data[n]) for n in sizes]

    sizes_arr = np.array(sizes, dtype=float)
    means_arr = np.array(means)

    log_sizes = np.log10(sizes_arr)
    log_means = np.log10(means_arr)

    a, b = np.polyfit(log_sizes, log_means, 1)

    ref_line = 10 ** (3 * log_sizes + (b + (a - 3) * np.mean(log_sizes)))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.loglog(sizes, means, 'o-', color='blue', linewidth=2, markersize=6,
              label=f'Zmierzone czasy (nachylenie={a:.2f})')
    ax.loglog(sizes, ref_line, '--', color='red', linewidth=2,
              label='Referencyjna prosta $n^3$')
    ax.set_xlabel('Rozmiar instancji (n)', fontsize=12)
    ax.set_ylabel('Czas wykonania [s]', fontsize=12)
    ax.set_title('Złożoność czasowa (skala log-log)', fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, which='both')

    filepath = os.path.join(out_dir, 'time_loglog.png')
    fig.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Zapisano: {filepath}")



def load_comparison_results(filepath):
    """Wczytuje wyniki porównania aproksymacji z brute force."""
    data = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        f.readline()
        for line in f:
            parts = line.strip().split(',')
            if len(parts) < 7:
                continue
            n = int(parts[0])
            if n not in data:
                data[n] = {'time_approx': [], 'time_bf': [], 'approx': [], 'optimal': [], 'ratio': []}
            data[n]['time_approx'].append(float(parts[2]))
            data[n]['time_bf'].append(float(parts[3]))
            data[n]['approx'].append(float(parts[4]))
            data[n]['optimal'].append(float(parts[5]))
            data[n]['ratio'].append(float(parts[6]))
    return data


def plot_comparison_time(comp_data, out_dir):
    """Wykres porównawczy czasów: aproksymacja vs brute force."""
    sizes = sorted(comp_data.keys())
    mean_approx = [np.mean(comp_data[n]['time_approx']) for n in sizes]
    mean_bf = [np.mean(comp_data[n]['time_bf']) for n in sizes]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(sizes, mean_approx, 'o-', color='blue', linewidth=2, markersize=7,
            label='3-aproksymacja (O(n³))')
    ax.plot(sizes, mean_bf, 's-', color='red', linewidth=2, markersize=7,
            label='Brute force (O(n!))')
    ax.set_xlabel('Liczba wierzchołków (n)', fontsize=12)
    ax.set_ylabel('Średni czas wykonania [s]', fontsize=12)
    ax.set_title('Porównanie czasu: 3-aproksymacja vs brute force', fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(sizes)

    filepath = os.path.join(out_dir, 'comparison_time.png')
    fig.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Zapisano: {filepath}")


def plot_comparison_time_log(comp_data, out_dir):
    """Wykres porównawczy czasów w skali logarytmicznej."""
    sizes = sorted(comp_data.keys())
    mean_approx = [np.mean(comp_data[n]['time_approx']) for n in sizes]
    mean_bf = [np.mean(comp_data[n]['time_bf']) for n in sizes]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.semilogy(sizes, mean_approx, 'o-', color='blue', linewidth=2, markersize=7,
                label='3-aproksymacja (O(n³))')
    ax.semilogy(sizes, mean_bf, 's-', color='red', linewidth=2, markersize=7,
                label='Brute force (O(n!))')
    ax.set_xlabel('Liczba wierzchołków (n)', fontsize=12)
    ax.set_ylabel('Średni czas wykonania [s] (skala log)', fontsize=12)
    ax.set_title('Porównanie czasu: 3-aproksymacja vs brute force (skala logarytmiczna)', fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, which='both')
    ax.set_xticks(sizes)

    filepath = os.path.join(out_dir, 'comparison_time_log.png')
    fig.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Zapisano: {filepath}")



def plot_comparison_ratio(comp_data, out_dir):
    """Wykres współczynnika aproksymacji z porównania."""
    sizes = sorted(comp_data.keys())
    mean_ratio = [np.mean(comp_data[n]['ratio']) for n in sizes]

    fig, ax = plt.subplots(figsize=(10, 6))
    for n in sizes:
        ratios = comp_data[n]['ratio']
        ax.scatter([n] * len(ratios), ratios, color='blue', s=40, alpha=0.6)
    ax.plot(sizes, mean_ratio, 'o-', color='darkblue', linewidth=2, markersize=7, label='Średnie ratio')
    ax.axhline(y=1.0, color='green', linestyle='--', linewidth=1.5, label='Optimum (ratio=1.0)')
    ax.axhline(y=3.0, color='red', linestyle='--', linewidth=1.5, label='Gwarancja teoretyczna (ratio=3.0)')
    ax.set_xlabel('Liczba wierzchołków (n)', fontsize=12)
    ax.set_ylabel('Współczynnik aproksymacji (approx / optimal)', fontsize=12)
    ax.set_title('Jakość 3-aproksymacji Bottleneck TSP', fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(sizes)
    ax.set_ylim(0.5, 3.5)

    filepath = os.path.join(out_dir, 'comparison_ratio.png')
    fig.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Zapisano: {filepath}")


def _draw_edges_on_ax(ax, x, y, W, edges, title, node_color, highlight_heaviest=True):
    n = len(x)

    heaviest = 0
    heaviest_edge = (0, 0)
    if highlight_heaviest:
        for u, v in edges:
            w = W[u][v]
            if w > heaviest:
                heaviest = w
                heaviest_edge = (u, v)

    for u, v in edges:
        is_h = highlight_heaviest and (u == heaviest_edge[0] and v == heaviest_edge[1])
        color = 'red' if is_h else 'steelblue'
        lw = 3.5 if is_h else 1.5
        ax.plot([x[u], x[v]], [y[u], y[v]], color=color, linewidth=lw, zorder=2)
        mid_x, mid_y = (x[u] + x[v]) / 2, (y[u] + y[v]) / 2
        ax.text(mid_x, mid_y, f"{W[u][v]:.0f}", fontsize=7, ha='center',
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white', alpha=0.85), zorder=4)

    ax.scatter(x, y, s=220, c=node_color, edgecolors='black', linewidths=1.2, zorder=5)
    for i in range(n):
        ax.text(x[i], y[i], str(i), fontsize=9, ha='center', va='center',
                fontweight='bold', zorder=6)

    subtitle = f"\nbottleneck = {heaviest:.0f}" if highlight_heaviest and heaviest > 0 else ""
    ax.set_title(f"{title}{subtitle}", fontsize=11)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2)


def _cycle_to_edges(cycle):
    return [(cycle[i], cycle[i + 1]) for i in range(len(cycle) - 1)]


def visualize(n, W, cycle, mst_edges):
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x = np.cos(angles)
    y = np.sin(angles)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    _draw_edges_on_ax(ax1, x, y, W, mst_edges,
                      "Minimalne Drzewo Rozpinające (MST)", 'lightblue',
                      highlight_heaviest=False)
    _draw_edges_on_ax(ax2, x, y, W, _cycle_to_edges(cycle),
                      "Cykl Hamiltona (Bottleneck TSP)", 'lightgreen')

    bottleneck = max(W[cycle[i]][cycle[i + 1]] for i in range(len(cycle) - 1))
    plt.suptitle(f"Bottleneck TSP — najcięższa krawędź: {bottleneck}", fontsize=13)
    plt.tight_layout()
    plt.show()


def plot_routes(out_dir, instances=None):
    """Generuje wykresy porównawcze tras dla aproksymacji i brute force."""
    from generator import generate_euclidean
    from bottleneck_tsp import solve_bottleneck_tsp
    from benchmark import brute_force_bottleneck_tsp

    if instances is None:
        instances = [6, 8, 10]

    sys.setrecursionlimit(5000)

    for idx, n in enumerate(instances):
        W_np, points = generate_euclidean(n, seed=42 + idx)
        W = [list(row) for row in W_np]
        px = points[:, 0]
        py = points[:, 1]

        approx_cycle, approx_bn, _ = solve_bottleneck_tsp(n, W)

        bf_cycle, bf_bn = brute_force_bottleneck_tsp(n, W)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        _draw_edges_on_ax(ax1, px, py, W, _cycle_to_edges(bf_cycle),
                          "Brute force (optimum)", '#90EE90')
        _draw_edges_on_ax(ax2, px, py, W, _cycle_to_edges(approx_cycle),
                          "3-aproksymacja", '#ADD8E6')

        ratio = approx_bn / bf_bn if bf_bn > 0 else 1.0
        fig.suptitle(f"Bottleneck TSP — n={n}, ratio = {ratio:.2f}", fontsize=14)
        plt.tight_layout()

        filepath = os.path.join(out_dir, f'routes_n{n}.png')
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close(fig)
        print(f"Zapisano: {filepath}")


def plot_instance_from_file(filepath, out_dir, seed=None):
    n, W = load_from_file(filepath)
    sys.setrecursionlimit(max(2000, 3 * n))

    cycle, bottleneck, mst_edges = solve_bottleneck_tsp(n, W)

    if seed is not None:
        _, points = generate_euclidean(n, seed=seed)
        px, py = points[:, 0], points[:, 1]
    else:
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
        px, py = np.cos(angles), np.sin(angles)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    _draw_edges_on_ax(ax1, px, py, W, mst_edges,
                      "MST (Prim)", 'lightblue', highlight_heaviest=False)
    _draw_edges_on_ax(ax2, px, py, W, _cycle_to_edges(cycle),
                      "3-aproksymacja", 'lightgreen')

    basename = os.path.splitext(os.path.basename(filepath))[0]
    fig.suptitle(f"Bottleneck TSP — n={n}, bottleneck = {bottleneck:.0f}", fontsize=14)
    plt.tight_layout()

    out_path = os.path.join(out_dir, f'{basename}.png')
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Zapisano: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Generowanie wykresów Bottleneck TSP")
    parser.add_argument('--results-dir', type=str, default='results', help="Katalog z wynikami benchmarków")
    parser.add_argument('--out-dir', type=str, default='charts', help="Katalog na wykresy")
    parser.add_argument('--routes', action='store_true',
                        help="Generuj wykresy tras (aproksymacja vs brute force)")
    parser.add_argument('--route-sizes', type=str, default='6,8,10',
                        help="Rozmiary instancji do wykresów tras (rozdzielone przecinkami)")
    parser.add_argument('--files', nargs='+',
                        help="Pliki wejsciowe do wizualizacji (MST + cykl aproksymacji)")
    parser.add_argument('--seed', type=int, default=None,
                        help="Seed generatora (do odtworzenia wspolrzednych 2D)")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    timing_path = os.path.join(args.results_dir, 'timing_results.csv')
    comparison_path = os.path.join(args.results_dir, 'comparison_results.csv')

    if os.path.exists(timing_path):
        timing_data = load_timing_results(timing_path)
        plot_time_complexity(timing_data, args.out_dir)
        plot_time_loglog(timing_data, args.out_dir)
    else:
        print(f"Brak pliku: {timing_path}")

    if os.path.exists(comparison_path):
        comp_data = load_comparison_results(comparison_path)
        plot_comparison_time(comp_data, args.out_dir)
        plot_comparison_time_log(comp_data, args.out_dir)
        plot_comparison_ratio(comp_data, args.out_dir)
    else:
        print(f"Brak pliku: {comparison_path}")

    if args.routes:
        route_sizes = [int(s) for s in args.route_sizes.split(',')]
        plot_routes(args.out_dir, instances=route_sizes)

    if args.files:
        for fp in args.files:
            if not os.path.exists(fp):
                print(f"Brak pliku: {fp}")
                continue
            file_seed = None
            if args.seed is not None:
                base = os.path.splitext(os.path.basename(fp))[0]
                parts = base.replace('test_n', '').split('_')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    size, idx = int(parts[0]), int(parts[1])
                    file_seed = args.seed * 10000 + size * 100 + idx
            plot_instance_from_file(fp, args.out_dir, seed=file_seed)


if __name__ == '__main__':
    main()
