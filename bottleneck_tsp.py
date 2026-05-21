"""
Bottleneck TSP - 3-aproksymacja
Algorytmy zaawansowane, projekt 2025/2026

Hubert Sobociński, Sandra Adamiec, Piotr Tyrakowski
"""

import sys
from collections import deque

# Wczytywanie danych

def load_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        n = int(f.readline().strip())
        matrix = []
        for _ in range(n):
            row = list(map(float, f.readline().split()))
            matrix.append(row)
    return n, matrix


def load_from_console():
    print("Podaj liczbę wierzchołków:")
    n = int(input().strip())
    print(f"Podaj macierz wag ({n}x{n}), wiersz po wierszu:")
    matrix = []
    for i in range(n):
        row = list(map(float, input().split()))
        matrix.append(row)
    return n, matrix


# Algorytm Prima — MST (O(V^2), skan liniowy)

def prim_mst(n, W):
    INF = float('inf')
    in_tree = [False] * n
    min_cost = [INF] * n
    parent = [-1] * n

    min_cost[0] = 0

    for _ in range(n):
        # Wybierz wierzchołek spoza drzewa o najmniejszym min_cost
        u = -1
        for v in range(n):
            if not in_tree[v] and (u == -1 or min_cost[v] < min_cost[u]):
                u = v
        in_tree[u] = True

        # Aktualizuj koszty sąsiadów
        for v in range(n):
            if not in_tree[v] and W[u][v] < min_cost[v]:
                min_cost[v] = W[u][v]
                parent[v] = u

    return parent


# Budowa listy sąsiedztwa drzewa z tablicy parent

def build_adjacency(parent, n):
    adj = {i: set() for i in range(n)}
    for v in range(n):
        p = parent[v]
        if p != -1:
            adj[v].add(p)
            adj[p].add(v)
    return adj


def get_mst_edges(parent, n):
    edges = []
    for v in range(1, n):
        edges.append((parent[v], v))
    return edges


# Wyodrębnienie wierzchołków poddrzewa (BFS)

def get_subtree_vertices(adj, start):
    visited = set()
    queue = deque([start])
    visited.add(start)
    while queue:
        node = queue.popleft()
        for nb in adj[node]:
            if nb not in visited:
                visited.add(nb)
                queue.append(nb)
    return visited


# Konstrukcja ścieżki Hamiltona — rekurencja T^3

def find_path_recursive(adj, vertices, start, end):
    n = len(vertices)

    if n == 1:
        return deque([start])
    if n == 2:
        return deque([start, end])
    if n == 3:
        middle = (vertices - {start, end}).pop()
        return deque([start, middle, end])

    adj[start].discard(end)
    adj[end].discard(start)

    subtree_start_vertices = get_subtree_vertices(adj, start)
    subtree_end_vertices = vertices - subtree_start_vertices

    sub_adj_start = {v: adj[v] & subtree_start_vertices for v in subtree_start_vertices}
    sub_adj_end = {v: adj[v] & subtree_end_vertices for v in subtree_end_vertices}

    if len(subtree_start_vertices) == 1:
        neighbor_start = start
    else:
        neighbor_start = next(iter(sub_adj_start[start]))

    if len(subtree_end_vertices) == 1:
        neighbor_end = end
    else:
        neighbor_end = next(iter(sub_adj_end[end]))

    path_left = find_path_recursive(sub_adj_start, subtree_start_vertices, start, neighbor_start)
    path_right = find_path_recursive(sub_adj_end, subtree_end_vertices, neighbor_end, end)

    path_left.extend(path_right)
    return path_left


# Rozwiązanie Bottleneck TSP

def solve_bottleneck_tsp(n, W):
    if n == 1:
        return [0, 0], 0, []
    if n == 2:
        return [0, 1, 0], W[0][1], [(0, 1)]

    parent = prim_mst(n, W)
    adj = build_adjacency(parent, n)
    mst_edges = get_mst_edges(parent, n)

    v, u = parent[1], 1
    vertices = set(range(n))

    path = find_path_recursive(adj, vertices, v, u)
    cycle = list(path) + [v] 

    bottleneck = 0
    for i in range(len(cycle) - 1):
        edge_weight = W[cycle[i]][cycle[i + 1]]
        if edge_weight > bottleneck:
            bottleneck = edge_weight

    return cycle, bottleneck, mst_edges


# Zapis wyników

def save_to_file(filepath, cycle, bottleneck):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Bottleneck (najcięższa krawędź): {bottleneck}\n")
        f.write("Cykl Hamiltona:\n")
        f.write(" -> ".join(str(v) for v in cycle) + "\n")

# Main

def main():
    args = sys.argv[1:]

    console_mode = '--console' in args
    viz_mode = '--viz' in args

    positional = [a for a in args if not a.startswith('--') and not a.startswith('-o')]

    output_file = 'output.txt'
    if '-o' in args:
        idx = args.index('-o')
        if idx + 1 < len(args):
            output_file = args[idx + 1]

    if console_mode:
        n, W = load_from_console()
    elif positional:
        n, W = load_from_file(positional[0])
    else:
        print("Użycie:")
        print("  python bottleneck_tsp.py <plik_wejściowy> [-o <plik_wyjściowy>] [--viz]")
        print("  python bottleneck_tsp.py --console [-o <plik_wyjściowy>] [--viz]")
        sys.exit(1)

    cycle, bottleneck, mst_edges = solve_bottleneck_tsp(n, W)

    print(f"Bottleneck (najcięższa krawędź): {bottleneck}")
    print(f"Cykl Hamiltona: {' -> '.join(str(v) for v in cycle)}")

    save_to_file(output_file, cycle, bottleneck)
    print(f"Wynik zapisano do: {output_file}")

    if viz_mode:
        from plots import visualize
        visualize(n, W, cycle, mst_edges)


if __name__ == '__main__':
    main()
