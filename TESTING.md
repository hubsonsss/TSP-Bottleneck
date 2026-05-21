# Testy — Bottleneck TSP

Repozytorium: [hubsonsss/TSP-Bottleneck](https://github.com/hubsonsss/TSP-Bottleneck)

## Instalacja

```bash
pip install -r requirements-dev.txt
```

## Uruchomienie

```powershell
.\run_tests.ps1
```

lub:

```bash
# Poprawność (szybkie)
pytest tests/test_correctness.py -v

# Wydajność + raport czasów w konsoli
pytest tests/test_performance.py -m performance -s
```

## Co testujemy

### Poprawność (`test_correctness.py`)

| Obszar | Opis |
|--------|------|
| Wejście/wyjście | Format macierzy z dokumentacji, `input.txt` |
| MST (Prim) | `n-1` krawędzi, spójność drzewa |
| Cykl Hamiltona | Każdy wierzchołek raz, cykl zamknięty |
| 3-aproksymacja | Dla `n ≤ 8`: wynik ≤ 3 × opt (brute force) |
| MST vs opt | Najcięższa krawędź MST ≤ optymalny bottleneck |
| Dowód dokumentu | `Wynik ≤ 3 × max(MST)` |
| Regresja | Uruchomienie na `input.txt` z repo |

### Wydajność (`test_performance.py`)

| Test | Cel |
|------|-----|
| Czas Prima | Mediana dla `n ∈ {10,20,30,50,75,100}` |
| Skalowanie | Stosunek czasów przy podwojeniu `n` (oczekiwane ~4× przy O(n²)) |
| Cały solver | Czas pełnego algorytmu, brak jawnego O(n³) |

Zgodnie z dokumentacją projektu złożoność całkowita to **O(n²)** (Prim na macierzy + rekurencja O(n) przy listach/deque).

## Uwaga o przykładzie z dokumentacji

Dla macierzy 4×4 z dokumentacji optymalny bottleneck wynosi **4**, algorytm zwraca **6** (nadal ≤ 3×4). Przykładowe `MAX_EDGE_WEIGHT 5` w LaTeX może odnosić się do innej numeracji wierzchołków lub wersji wyniku.
