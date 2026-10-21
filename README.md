# Graph Theory Implementation & Applications (Week 6)

**Group 6** 

| Name                 | NRP        | Class |
| -------------------- | ---------- | ----- |
| Lina Fatima Azzahra Badr | 5025251168 | IUP   |
| Naila Sa'ada Cahyani | 5025251258 | IUP   |

Comprehensive implementation of core graph algorithms solving combinatorial routing and pathfinding problems across CLI and Web environments. The platform applies the Held-Karp dynamic programming algorithm for the Traveling Salesperson Problem (TSP) on OpenStreetMap road networks, solves the Directed Chinese Postman Problem (CPP) through minimum-cost flow edge augmentation, and determines full chessboard traversals for the Knight's Tour Problem using Warnsdorff's heuristic backtracking.

---

## Project Architecture

```text
W6_GraphTheory/
├── cli/                                # CLI execution environment
│   ├── main.py                         # Interactive CLI entry point (Task 1-3 launcher)
│   ├── requirements.txt                # CLI dependencies (networkx, osmnx, scikit-learn)
│   ├── task1/                          # Task 1: School Meal Delivery (TSP)
│   │   ├── algorithm/
│   │   │   └── held_karp.py            # Held-Karp O(n^2 * 2^n) dynamic programming
│   │   ├── engine/
│   │   │   ├── osm_data.py             # OSM loader, dataset caching, demo 4x4 grid
│   │   │   ├── road_tour.py            # Snapping, Dijkstra distance matrix, polyline
│   │   │   └── service.py              # Filtering within radius, TSP coordinator
│   │   └── interface/cli/
│   │       └── run_task1_cli.py        # Task 1 CLI runner with argparse flags
│   ├── task2/                          # Task 2: Waste Collection Routing (DCPP)
│   │   ├── algorithm/
│   │   │   └── chinese_postman.py      # Degree balancing, min-cost flow, Eulerian circuit
│   │   ├── engine/
│   │   │   └── service.py              # OSMnx live graph fetch, base node snapping
│   │   └── interface/cli/
│   │       └── run_task2_cli.py        # Task 2 CLI runner with interactive prompts
│   └── task3/                          # Task 3: Knight's Tour Problem
│       ├── algorithm/
│       │   └── knight_tour.py          # Warnsdorff's heuristic DFS backtracking
│       ├── engine/
│       │   └── service.py              # Coordinate & dimension validator, execution timer
│       ├── interface/cli/
│       │   └── run_task3_cli.py        # Task 3 stdin parser and formatter
│       └── requirements.txt            # Zero external dependencies (standard library)
├── web/                                # Flask web application environment
│   ├── app.py                          # Flask application server and REST API endpoints
│   ├── requirements.txt                # Web dependencies (flask, networkx, osmnx)
│   ├── static/                         # Frontend styling, scripts, and media
│   │   ├── app.js                      # Task 2/3 UI interactions and Leaflet/DOM logic
│   │   ├── knight.jpg                  # Knight's Tour visual banner asset
│   │   ├── style.css                   # Global dashboard and component styling
│   │   ├── task1.css                   # Task 1 Leaflet map and route sidebar styling
│   │   └── task1.js                    # Task 1 interactive map client and API caller
│   ├── templates/                      # Jinja2 HTML templates
│   │   ├── base.html                   # Global navigation and shell layout
│   │   ├── home.html                   # Overview dashboard (/)
│   │   ├── task1.html                  # TSP map route visualizer (/task1)
│   │   ├── task2.html                  # Chinese Postman route inspector (/task2)
│   │   └── task3.html                  # Knight's Tour interactive chessboard (/task3)
│   ├── task1/                          # Web Task 1 engine and algorithms
│   │   ├── algorithm/
│   │   │   └── held_karp.py            # Held-Karp O(n^2 * 2^n) dynamic programming
│   │   └── engine/
│   │       ├── osm_data.py             # OSM loader and dataset caching
│   │       ├── road_tour.py            # Snapping, Dijkstra distance matrix, polyline
│   │       └── service.py              # Filtering within radius, GeoJSON overlay
│   ├── task2/                          # Web Task 2 engine and algorithms
│   │   ├── algorithm/
│   │   │   └── chinese_postman.py      # Degree balancing, min-cost flow, Eulerian circuit
│   │   └── engine/
│   │       └── service.py              # OSMnx live graph fetch, base node snapping
│   └── task3/                          # Web Task 3 engine and algorithms
│       ├── algorithm/
│       │   └── knight_tour.py          # Warnsdorff's heuristic DFS backtracking
│       └── engine/
│           └── service.py              # Coordinate & dimension validator, execution timer
├── data/                               # Cache and fixture storage
│   └── osm/                            # OSM road graphml and school geo-fixtures
│       ├── roads.graphml               # Surabaya drivable road network MultiDiGraph
│       └── schools.json                # Extracted school nodes and representative coordinates
├── Group6_GraphTheory.pdf              # Academic report documentation
└── README.md                           # Consolidated project documentation
```

---

## Task Overview & Algorithm Implementations

| Task | Domain / Problem | Algorithm Applied | Input / Data Source |
| :--- | :--- | :--- | :--- |
| **Task 1** | Traveling Salesperson Problem (TSP) | Held-Karp (Dynamic Programming) | Road Network / School Locations (`roads.graphml`, `schools.json`) |
| **Task 2** | Chinese Postman Problem (CPP) | Eulerian Path / Minimum Weight Matching | Graph Network Edge Coverage |
| **Task 3** | Knight's Tour Problem | Warnsdorff's Heuristic / Backtracking | Chessboard Grid Coordinates |

### Task 1: School Meal Delivery Route Optimization (SPPG TSP)
- **Problem Statement**: Find the minimal distance and travel time round-trip tour starting and ending at the central distribution center (SPPG, default at ITS Surabaya: `-7.2825, 112.7944`) visiting every designated school within radius $R$ exactly once.
- **Algorithm & Complexity**:
  - Distance computation: Filters school locations within the bounding radius using Haversine spherical distance, snaps stops to the nearest drive-network nodes within 500 meters, and constructs an asymmetric distance matrix via all-pairs Dijkstra on directed OpenStreetMap graphs (`nx.MultiDiGraph`).
  - Route optimization: Exact Held-Karp dynamic programming with bitmask state representation:
    $$\text{DP}[\text{mask}, i] = \min_{j \in \text{mask} \setminus \{i\}} \left( \text{DP}[\text{mask} \setminus \{i\}, j] + \text{cost}(j, i) \right)$$
  - Complexity: Time complexity $O(n^2 \cdot 2^n)$ and space complexity $O(n \cdot 2^n)$. Strict threshold of $n \le 16$ stops (1 SPPG depot + up to 15 schools) prevents exponential degradation.

### Task 2: Waste Collection Street Coverage (DLH Directed Chinese Postman)
- **Problem Statement**: Generate a closed traversal route for municipal street sweeping / waste collection trucks that traverses every drivable road segment in the target area at least once while minimizing total deadheading (duplicate traversal distance).
- **Algorithm & Complexity**:
  - Subgraph extraction: Fetches the drive network around target coordinates via OSMnx filtered for major highways (`trunk`, `primary`, `secondary`, `tertiary`, and associated link ways).
  - Graph Eulerianization:
    1. Extracts the strongly connected component containing the depot node.
    2. Identifies node degree imbalances ($\delta(v) = \text{deg}^+(v) - \text{deg}^-(v)$). Nodes with $\delta(v) > 0$ are designated supply sources, while nodes with $\delta(v) < 0$ are demand sinks.
    3. Computes shortest path distance matrix between imbalanced nodes via all-pairs Dijkstra.
    4. Formulates and solves a minimum-cost flow problem (`nx.min_cost_flow`) to determine optimal flow quantities between surplus and deficit vertices.
    5. Adds augmenting duplicate edges along the shortest paths to achieve an Eulerian directed multigraph.
  - Circuit construction: Applies Hierholzer's algorithm (`nx.eulerian_circuit`) to construct the final closed Eulerian tour.

### Task 3: Knight's Tour Problem (Chessboard Traversal)
- **Problem Statement**: Determine a sequence of valid knight moves on an $M \times N$ chessboard such that the knight visits every cell on the board exactly once from a chosen starting square $(c_0, r_0)$.
- **Algorithm & Complexity**:
  - Search strategy: Depth-First Search (DFS) with recursive backtracking. Visited squares are tracked in an $M \times N$ matrix.
  - Warnsdorff's heuristic: Candidate knight moves ($(\pm 1, \pm 2), (\pm 2, \pm 1)$) are evaluated dynamically and sorted in ascending order of their onward degree (number of unvisited legal moves available from the candidate square). Moving to squares with fewer onward options prevents early isolation of board vertices.
  - Complexity: Worst-case exponential $O(8^{M \cdot N})$, reduced to near $O(M \cdot N)$ linear convergence in practical executions for grid dimensions up to $12 \times 12$.

---

## Environment Setup

### 1. Python Environment Initialization
The project requires **Python 3.11+**. Create and activate a clean virtual environment:

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt)
py -m venv venv
venv\Scripts\activate

# Windows (PowerShell)
py -m venv venv
venv\Scripts\Activate.ps1
```

### 2. Dependency Installation
Install required packages for the respective interfaces:

```bash
# Install CLI dependencies (networkx, osmnx, scikit-learn)
pip install -r cli/requirements.txt

# Install Web dependencies (flask, networkx, osmnx)
pip install -r web/requirements.txt
```

*(Note: Task 3 CLI depends solely on the Python standard library and can run without external packages).*

### 3. OpenStreetMap Data Pre-Caching for Task 1
Task 1 reads road network definitions and school locations from cached files (`roads.graphml` and `schools.json`). If the web map fails to load on the web interface (returning HTTP 503), download the OpenStreetMap data before running the server:

```bash
# From the project root, download and cache OSM data for the web interface:
py -m task1.engine.osm_data --download --cache-dir web/data/osm

# macOS / Linux equivalent:
python3 -m cli.task1.engine.osm_data --download --cache-dir web/data/osm
```

To pre-cache for the CLI interface instead:
```bash
python -m cli.task1.engine.osm_data --download --cache-dir cli/data/osm
```

---

## CLI Execution Guide

Run all three tasks from the repository root using the single unified command:

```bash
python -m cli.main
```

This launches the interactive menu to select your desired task:

```text
Graph Theory [CLI Mode]
1. Task 1 - SPPG delivery (Held-Karp TSP)
2. Task 2 - DLH collection (Directed Chinese Postman)
3. Task 3 - Knight's Tour
0. Exit
Select task [1/2/3/0]:
```

You can either make a selection in the interactive menu or pass the task number and options directly to the unified command:

| Task | Command | Input & Option Details |
| :--- | :--- | :--- |
| **Task 1: SPPG Delivery (TSP)** | `python -m cli.main 1` | Prompts for SPPG Latitude, Longitude, and Radius (defaults: ITS Surabaya `-7.2825, 112.7944`, `1.0` km).<br>Optional flags: `--demo` (fast simulated grid, no OSM download), `--radius <km>`, `--lat <val>`, `--lng <val>`, `--offline` |
| **Task 2: Waste Collection (CPP)** | `python -m cli.main 2` | Prompts for Latitude (default `-7.2825`), Longitude (default `112.7944`), and Radius (default `1.5` km). Press Enter to accept defaults. |
| **Task 3: Knight's Tour** | `python -m cli.main 3` | Reads 2 lines from `stdin`: board dimensions (`cols rows`, 1–12) and starting square (`start_col start_row`). Outputs space-separated `(row,col)` visited path. |

#### Quick Examples via Unified CLI Command:
```bash
# Task 1: Run with fast demo road grid (instant, no download needed)
python -m cli.main 1 --demo --radius 1.0

# Task 1: Run with custom coordinates on real OSM network
python -m cli.main 1 --lat -7.2825 --lng 112.7944 --radius 1.0

# Task 2: Run with default East Surabaya coordinates (1.5 km radius)
printf "\n\n\n" | python -m cli.main 2

# Task 3: Solve a 5x5 chessboard starting at (2, 2)
printf "5 5\n2 2\n" | python -m cli.main 3

# Task 3: Solve a standard 8x8 chessboard starting at (0, 0)
printf "8 8\n0 0\n" | python -m cli.main 3
```

---

## Web Application Guide

Launch the entire web application from the repository root using the single unified command:

```bash
flask --app web/app.py run --port 5000
```
*(or `python -m flask --app web/app.py run --port 5000`)*

Open your browser at:
```text
http://127.0.0.1:5000
```

From the overview dashboard (`/`), navigate directly to any task visualizer:

| Module / Route | Purpose | Sample Inputs & Expected Output |
| :--- | :--- | :--- |
| **Overview Dashboard**<br>`/` | Central navigation hub | Overview of all three tasks and navigation links. |
| **Task 1: SPPG Delivery (TSP)**<br>`/task1` | Interactive TSP route visualizer (Leaflet) | **Inputs**: Lat `-7.2825`, Lng `112.7944`, Radius `1.0` km (ITS Surabaya).<br>**Output**: Selects schools inside radius, computes optimal Held-Karp round trip, and draws the delivery route on the map. |
| **Task 2: Waste Collection (CPP)**<br>`/task2` | Street sweeping coverage route inspector | **Inputs**: Lat `-7.2825`, Lng `112.7944`, Radius `1.5` km.<br>**Output**: Fetches live OSM road network, augments deadheading paths, and animates the closed Eulerian garbage truck tour. |
| **Task 3: Knight's Tour**<br>`/task3` | Interactive chessboard generator & animator | **Inputs**: Board `5` × `5`, Start Square `(2, 2)` *(or `8` × `8` at `(0, 0)`)*.<br>**Output**: Renders the chessboard, computes complete traversal via Warnsdorff's heuristic, and animates moves step-by-step. |

> **Task 1 Map Data Troubleshooting**:
> If the map fails to load for Task 1 (`/task1` returning HTTP 503), download and cache the OpenStreetMap data before starting Flask:
> ```bash
> py -m task1.engine.osm_data --download --cache-dir web/data/osm
> ```
> This saves `roads.graphml` and `schools.json` into `web/data/osm/`, which is the exact location read by `web/app.py`.
