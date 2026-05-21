# Bottleneck TSP - 3-aproksymacja

Algorytmy zaawansowane, projekt 2025/2026
Autorzy: Hubert Sobocinski, Sandra Adamiec, Piotr Tyrakowski

## Wymagania

- Python 3
- numpy
- matplotlib

## Pliki

| Plik | Opis |
|------|------|
| `bottleneck_tsp.py` | Glowny solver - algorytm 3-aproksymacji |
| `generator.py` | Generator plikow wejsciowych |
| `benchmark.py` | Pomiary czasowe i analiza jakosci |
| `plots.py` | Generowanie wykresow z wynikow |

## 1. Solver - rozwiazywanie problemu

```bash
# Z pliku wejsciowego
python bottleneck_tsp.py input.txt

# Z pliku + zapis do konkretnego pliku wyjsciowego
python bottleneck_tsp.py input.txt -o wynik.txt

# Z wizualizacja graficzna (MST + cykl Hamiltona)
python bottleneck_tsp.py input.txt --viz

# Wejscie z konsoli
python bottleneck_tsp.py --console
```

Format pliku wejsciowego:
```
3
0 10 15
10 0 20
15 20 0
```
Pierwsza linia: liczba wierzcholkow. Nastepne n linii: macierz wag n x n.

## 2. Generator plikow wejsciowych

```bash
# Pojedyncza instancja (10 wierzcholkow, tryb euklidesowy)
python generator.py 10

# Z konkretnym plikiem wyjsciowym i seedem
python generator.py 10 -o moj_test.txt --seed 42

# Tryb losowych wag (bez gwarancji nierownosci trojkata)
python generator.py 10 --mode random --min-w 1 --max-w 100

# Tryb wsadowy - wiele plikow naraz
python generator.py --batch --sizes 5,10,20,50,100,200,500 --repeats 10 --out-dir test_inputs --seed 42
```

## 3. Benchmarking

```bash
# Pelny benchmark (wymaga wczesniejszego wygenerowania plikow w test_inputs/)
python benchmark.py

# Z wlasnymi parametrami
python benchmark.py --sizes 5,10,20,50,100 --repeats 5

# Tylko pomiary czasowe (bez brute force)
python benchmark.py --skip-quality

# Tylko analiza jakosci (brute force dla n<=10)
python benchmark.py --skip-timing

# Porownanie z brute force (generuje instancje automatycznie, nie wymaga test_inputs/)
python benchmark.py --skip-timing --skip-quality --comparison

# Porownanie z wlasnym zakresem n (domyslnie do 11)
python benchmark.py --skip-timing --skip-quality --comparison --max-n 11 --repeats 5
```

Wyniki zapisywane do katalogu `results/`:
- `timing_results.csv` - czasy wykonania
- `quality_results.csv` - porownanie z optimum
- `comparison_results.csv` - porownanie aproksymacja vs brute force

## 4. Generowanie wykresow

```bash
# Generuje wszystkie wykresy z dostepnych wynikow (timing, quality, comparison)
python plots.py

# Dodatkowo: wykresy tras (aproksymacja vs brute force obok siebie)
python plots.py --routes

# Wykresy tras z wlasnymi rozmiarami instancji (domyslnie 6,8,10)
python plots.py --routes --route-sizes 5,7,9,11

# Wszystko naraz
python plots.py --routes
```

Wykresy zapisywane do katalogu `charts/`:

Zlozonosc czasowa:
- `time_complexity.png` - czas vs krzywa c*n^3
- `time_loglog.png` - zlozonosc w skali log-log

Jakosc aproksymacji:
- `approximation_quality.png` - jakosc aproksymacji
- `ratio_histogram.png` - histogram wspolczynnika aproksymacji

Porownanie z brute force:
- `comparison_time.png` - porownanie czasow: aproksymacja vs brute force
- `comparison_time_log.png` - j.w. w skali logarytmicznej
- `comparison_bottleneck.png` - porownanie wartosci bottleneck
- `comparison_ratio.png` - wspolczynnik aproksymacji

Wizualizacja tras (flaga `--routes`):
- `routes_n6.png`, `routes_n8.png`, `routes_n10.png` - trasy na grafach 2D, po lewej brute force (optimum), po prawej 3-aproksymacja, czerwona krawedz = bottleneck

## 5. Testy

```bash
pip install -r requirements-dev.txt
```

```bash
# Poprawnosc (szybkie)
pytest tests/test_correctness.py -v

# Wydajnosc + raport czasow w konsoli
pytest tests/test_performance.py -m performance -s
```

### Poprawnosc (`test_correctness.py`)

| Obszar | Opis |
|--------|------|
| Wejscie/wyjscie | Format macierzy z dokumentacji, `input.txt` |
| MST (Prim) | `n-1` krawedzi, spojnosc drzewa |
| Cykl Hamiltona | Kazdy wierzcholek raz, cykl zamkniety |
| 3-aproksymacja | Dla `n <= 8`: wynik <= 3 x opt (brute force) |
| MST vs opt | Najciezsza krawedz MST <= optymalny bottleneck |
| Dowod dokumentu | `Wynik <= 3 x max(MST)` |
| Regresja | Uruchomienie na `input.txt` z repo |

### Wydajnosc (`test_performance.py`)

| Test | Cel |
|------|-----|
| Czas Prima | Mediana dla `n in {10,20,30,50,75,100}` |
| Skalowanie | Stosunek czasow przy podwojeniu `n` (oczekiwane ~4x przy O(n^2)) |
| Caly solver | Czas pelnego algorytmu, brak jawnego O(n^3) |

Zlozonosc calkowita to **O(n^2)** (Prim na macierzy + rekurencja O(n) przy listach/deque).

### Uwaga o przykladzie z dokumentacji

Dla macierzy 4x4 z dokumentacji optymalny bottleneck wynosi **4**, algorytm zwraca **6** (nadal <= 3x4).

## Pelny pipeline - wszystko od zera

```bash
# Krok 1: Wygeneruj pliki testowe
python generator.py --batch --sizes 5,10,20,50,100,200,500 --repeats 10 --out-dir test_inputs --seed 42

# Krok 2: Uruchom benchmarki (timing + quality + comparison)
python benchmark.py --sizes 5,10,20,50,100,200,500 --repeats 10 --comparison --max-n 11

# Krok 3: Wygeneruj wszystkie wykresy
python plots.py --routes
```

Wykresy beda w katalogu `charts/`.
