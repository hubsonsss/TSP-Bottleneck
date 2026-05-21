"""
Generator plików wejściowych dla Bottleneck TSP
Algorytmy zaawansowane, projekt 2025/2026

Hubert Sobociński, Sandra Adamiec, Piotr Tyrakowski
"""

import sys
import os
import argparse
import numpy as np


def generate_euclidean(n, seed=None):
    """Generuje macierz wag na podstawie losowych punktów 2D (odległości euklidesowe).
    Spełnia nierówność trójkąta."""
    rng = np.random.default_rng(seed)
    points = rng.uniform(0, 1000, size=(n, 2))
    W = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = np.sqrt((points[i][0] - points[j][0]) ** 2 + (points[i][1] - points[j][1]) ** 2)
            W[i][j] = round(d, 2)
            W[j][i] = W[i][j]
    return W, points


def generate_random(n, min_w=1, max_w=1000, seed=None):
    """Generuje losową symetryczną macierz wag."""
    rng = np.random.default_rng(seed)
    W = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            w = rng.integers(min_w, max_w + 1)
            W[i][j] = w
            W[j][i] = w
    return W, None


def save_instance(filepath, n, W):
    """Zapisuje instancję do pliku."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"{n}\n")
        for i in range(n):
            row = " ".join(f"{W[i][j]:g}" for j in range(n))
            f.write(row + "\n")


def main():
    parser = argparse.ArgumentParser(description="Generator plików wejściowych dla Bottleneck TSP")

    parser.add_argument('n', type=int, nargs='?', help="Liczba wierzchołków")
    parser.add_argument('-o', '--output', type=str, default=None, help="Plik wyjściowy")
    parser.add_argument('--mode', choices=['euclidean', 'random'], default='euclidean',
                        help="Tryb generowania (domyślnie: euclidean)")
    parser.add_argument('--seed', type=int, default=None, help="Ziarno generatora losowego")
    parser.add_argument('--min-w', type=int, default=1, help="Minimalna waga (tryb random)")
    parser.add_argument('--max-w', type=int, default=1000, help="Maksymalna waga (tryb random)")

    parser.add_argument('--batch', action='store_true', help="Tryb wsadowy")
    parser.add_argument('--sizes', type=str, default='5,10,20,50,100,200,500',
                        help="Rozmiary instancji (tryb batch, rozdzielone przecinkami)")
    parser.add_argument('--repeats', type=int, default=10, help="Liczba powtórzeń na rozmiar (tryb batch)")
    parser.add_argument('--out-dir', type=str, default='test_inputs', help="Katalog wyjściowy (tryb batch)")

    args = parser.parse_args()

    if args.batch:
        sizes = [int(s) for s in args.sizes.split(',')]
        os.makedirs(args.out_dir, exist_ok=True)

        for size in sizes:
            for i in range(args.repeats):
                seed = (args.seed * 10000 + size * 100 + i) if args.seed is not None else None
                if args.mode == 'euclidean':
                    W, _ = generate_euclidean(size, seed=seed)
                else:
                    W, _ = generate_random(size, args.min_w, args.max_w, seed=seed)

                filename = f"test_n{size}_{i}.txt"
                filepath = os.path.join(args.out_dir, filename)
                save_instance(filepath, size, W)

            print(f"Wygenerowano {args.repeats} instancji dla n={size}")

        print(f"Pliki zapisano w: {args.out_dir}/")

    else:
        if args.n is None:
            parser.error("Podaj liczbę wierzchołków (n) lub użyj --batch")

        if args.mode == 'euclidean':
            W, _ = generate_euclidean(args.n, seed=args.seed)
        else:
            W, _ = generate_random(args.n, args.min_w, args.max_w, seed=args.seed)

        output = args.output or f"test_n{args.n}.txt"
        save_instance(output, args.n, W)
        print(f"Wygenerowano instancję n={args.n} -> {output}")


if __name__ == '__main__':
    main()
