# Graph Theory: web version

Flask website with all three tasks. Run every command from this `web/` folder.

## Install and run

Python 3.11 or newer.

```sh
python -m pip install -r requirements.txt
python -m flask --app app run
```

Then open http://127.0.0.1:5000

- `/task1` SPPG delivery route (Held-Karp TSP)
- `/task2` DLH garbage truck route (Directed Chinese Postman)
- `/task3` Knight's Tour

## Task 1 data

Task 1 needs the Surabaya road network and school list from OpenStreetMap.
Download it once (takes a few minutes and needs internet):

```sh
python -m task1.engine.osm_data --download
```

It is saved in `data/osm/` and the website only reads from there, it never
downloads by itself. If the folder is missing the API answers with an error
(HTTP 503). To use a cache somewhere else, set `TASK1_CACHE_DIR` before
starting Flask.

How Task 1 works:

1. Every school within the radius of the SPPG is selected.
2. The SPPG and the schools are snapped to the nearest road node (max 500 m).
3. Dijkstra gives the shortest road distance between every pair of stops.
   Roads can be one-way, so this matrix is directed.
4. Held-Karp finds the exact shortest round trip. It is O(n^2 * 2^n), so we
   allow at most 15 schools. With more, the API asks for a smaller radius.

Travel time uses the road speeds from OSMnx, not live traffic. OSM does not
have every school, so some may be missing.

## Task 2

Task 2 downloads its roads live from OpenStreetMap through OSMnx every time,
so it needs internet. It does not use the Task 1 cache.

## Task 3

Knight's Tour with backtracking and Warnsdorff's rule. No data needed.
See [task3/README.md](task3/README.md).

## Folders

```text
web/
  app.py            Flask routes
  task1/            Held-Karp (algorithm/) and OSM loading + routing (engine/)
  task2/            Chinese Postman
  task3/            Knight's Tour
  templates/        HTML pages
  static/           CSS and JS
  tests/            pytest tests
```

## Tests

```sh
python -m pytest -q
```

The Task 1 tests use a small fake road grid, so they don't need the OSM cache.
