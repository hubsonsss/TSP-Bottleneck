"""
Benchmarking i analiza jakości aproksymacji Bottleneck TSP
Algorytmy zaawansowane, projekt 2025/2026

Hubert Sobociński, Sandra Adamiec, Piotr Tyrakowski
"""

import sys
import os
import time
import argparse
from itertools import permutations

from bottleneck_tsp import load_from_file, solve_bottleneck_tsp
from generator import generate_euclidean


def brute_force_bottleneck_tsp(n, W):
    """Dokładne rozwiązanie Bottleneck TSP"""
    if n == 1:
        return [0, 0], 0
    if n == 2:
        return [0, 1, 0], W[0][1]

    best = float('inf')
    best_cycle = None

    for perm in permutations(range(1, n)):
        cycle = [0] + list(perm) + [0]
        bottleneck = max(W[cycle[i]][cycle[i + 1]] for i in range(n))
        if bottleneck < best:
            best = bottleneck
            best_cycle = cycle

    return best_cycle, best


def run_timing_benchmark(sizes, repeats, input_dir, out_dir):
    """Mierzy czas wykonania algorytmu"""
    os.makedirs(out_dir, exist_ok=True)
    results_path = os.path.join(out_dir, "timing_results.csv")

    with open(results_path, 'w', encoding='utf-8') as f:
        f.write("n,repeat,time_s,bottleneck\n")

        for size in sizes:
            times = []
            print(f"Pomiar czasu dla n={size}...", end=" ", flush=True)

            for i in range(repeats):
                filepath = os.path.join(input_dir, f"test_n{size}_{i}.txt")
                if not os.path.exists(filepath):
                    print(f"\n  Brak pliku: {filepath}, pomijam")
                    continue

                n, W = load_from_file(filepath)
                sys.setrecursionlimit(max(2000, 3 * n))

                t0 = time.perf_counter()
                result = solve_bottleneck_tsp(n, W)
                t1 = time.perf_counter()

                elapsed = t1 - t0
                times.append(elapsed)

                if len(result) == 3:
                    cycle, bottleneck, mst_edges = result
                else:
                    cycle, bottleneck = result

                f.write(f"{size},{i},{elapsed:.6f},{bottleneck}\n")

            if times:
                avg = sum(times) / len(times)
                print(f"średni czas: {avg:.4f}s ({len(times)} instancji)")
            else:
                print("brak danych")

    print(f"\nWyniki zapisano do: {results_path}")


def run_quality_benchmark(sizes, repeats, input_dir, out_dir):
    """Porównuje jakość aproksymacji z rozwiązaniem optymalnym (brute force)."""
    os.makedirs(out_dir, exist_ok=True)
    results_path = os.path.join(out_dir, "quality_results.csv")

    small_sizes = [s for s in sizes if s <= 10]
    if not small_sizes:
        print("Brak rozmiarów <= 10, pomijam analizę jakości")
        return

    with open(results_path, 'w', encoding='utf-8') as f:
        f.write("n,repeat,optimal,approximation,ratio\n")

        for size in small_sizes:
            print(f"Analiza jakości dla n={size}...", end=" ", flush=True)
            ratios = []

            for i in range(repeats):
                filepath = os.path.join(input_dir, f"test_n{size}_{i}.txt")
                if not os.path.exists(filepath):
                    continue

                n, W = load_from_file(filepath)

                result = solve_bottleneck_tsp(n, W)
                if len(result) == 3:
                    _, approx_val, _ = result
                else:
                    _, approx_val = result

                _, optimal_val = brute_force_bottleneck_tsp(n, W)

                ratio = approx_val / optimal_val if optimal_val > 0 else 1.0
                ratios.append(ratio)

                f.write(f"{size},{i},{optimal_val},{approx_val},{ratio:.4f}\n")

            if ratios:
                avg_ratio = sum(ratios) / len(ratios)
                max_ratio = max(ratios)
                print(f"średnie ratio: {avg_ratio:.3f}, max: {max_ratio:.3f}")
            else:
                print("brak danych")

    print(f"\nWyniki jakości zapisano do: {results_path}")


def run_comparison_benchmark(max_n, repeats, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    results_path = os.path.join(out_dir, "comparison_results.csv")

    sys.setrecursionlimit(max(2000, 3 * max_n))

    with open(results_path, 'w', encoding='utf-8') as f:
        f.write("n,repeat,time_approx,time_bruteforce,bottleneck_approx,bottleneck_optimal,ratio\n")

        for n in range(3, max_n + 1):
            print(f"Porównanie dla n={n}...", end=" ", flush=True)

            for r in range(repeats):
                W_np, _ = generate_euclidean(n, seed=100 * n + r)
                W = [list(row) for row in W_np]

                t0 = time.perf_counter()
                _, approx_val, _ = solve_bottleneck_tsp(n, W)
                t1 = time.perf_counter()
                time_approx = t1 - t0

                t0 = time.perf_counter()
                _, optimal_val = brute_force_bottleneck_tsp(n, W)
                t1 = time.perf_counter()
                time_bf = t1 - t0

                ratio = approx_val / optimal_val if optimal_val > 0 else 1.0
                f.write(f"{n},{r},{time_approx:.6f},{time_bf:.6f},{approx_val},{optimal_val},{ratio:.4f}\n")

            print("done")

    print(f"\nWyniki porównania zapisano do: {results_path}")


# main 
def main():
    parser = argparse.ArgumentParser(description="Benchmark Bottleneck TSP")
    parser.add_argument('--sizes', type=str, default='5,10,20,50,100,200,500',
                        help="Rozmiary instancji (rozdzielone przecinkami)")
    parser.add_argument('--repeats', type=int, default=10, help="Liczba powtórzeń na rozmiar")
    parser.add_argument('--input-dir', type=str, default='test_inputs', help="Katalog z plikami wejściowymi")
    parser.add_argument('--out-dir', type=str, default='results', help="Katalog na wyniki")
    parser.add_argument('--skip-timing', action='store_true', help="Pomiń pomiary czasowe")
    parser.add_argument('--skip-quality', action='store_true', help="Pomiń analizę jakości")
    parser.add_argument('--comparison', action='store_true',
                        help="Porównanie z brute force (generuje instancje automatycznie)")
    parser.add_argument('--max-n', type=int, default=11,
                        help="Maks. n dla porównania z brute force (domyślnie: 11)")

    args = parser.parse_args()
    sizes = [int(s) for s in args.sizes.split(',')]

    if not args.skip_timing:
        run_timing_benchmark(sizes, args.repeats, args.input_dir, args.out_dir)

    if not args.skip_quality:
        run_quality_benchmark(sizes, args.repeats, args.input_dir, args.out_dir)

    if args.comparison:
        run_comparison_benchmark(args.max_n, args.repeats, args.out_dir)


if __name__ == '__main__':
    main()
