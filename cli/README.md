# Graph Theory: CLI version

Terminal version of all three tasks. Run every command from this `cli/` folder.

## Install

Python 3.11 or newer.

```sh
python -m pip install -r requirements.txt
```

Task 3 only uses the standard library, so you can skip this if you only run Task 3.

## Menu

```sh
python main.py
```

Pick 1, 2 or 3 (0 exits). You can also pick the task directly and pass its options:

```sh
python main.py 1 --demo --radius 1
python main.py 2
printf '5 5\n2 2\n' | python main.py 3
```

## Task 1: SPPG school delivery

```sh
python -m task1.interface.cli.run_task1_cli
```

It asks for latitude, longitude and radius. Press Enter to use the defaults
(ITS, `-7.2825, 112.7944`, 1 km). Passing `--lat`, `--lng` or `--radius`
skips the questions.

Options:

- `--demo` uses a small fake road grid instead of OpenStreetMap (no internet needed)
- `--offline` never downloads, only uses the saved data
- `--cache-dir PATH` where the OSM data is saved (default `cli/data/osm/`)

Output: school visiting order, total distance, estimated travel time and TSP
solver execution time.

The first real run downloads the Surabaya roads and schools, which takes a few
minutes. You can also download them first:

```sh
python -m task1.engine.osm_data --download
```

How it works: every school inside the radius is selected, every stop is snapped
to the nearest road node (max 500 m), Dijkstra builds the road distance matrix
and Held-Karp finds the exact shortest round trip. Held-Karp is O(n^2 * 2^n),
so at most 15 schools are allowed. Use a smaller radius if there are more.

## Task 2: DLH garbage truck route

```sh
python -m task2.interface.cli.run_task2_cli
```

Asks for latitude, longitude and radius (Enter = ITS and 1.5 km). Downloads
roads from OpenStreetMap, so it needs internet.

## Task 3: Knight's Tour

```sh
printf '5 5\n2 2\n' | python -m task3.interface.cli.run_task3_cli
```

See [task3/README.md](task3/README.md) for the input and output format.

## Tests

```sh
python -m pytest -q
```

The Task 1 tests use the fake demo grid, so no download is needed.
