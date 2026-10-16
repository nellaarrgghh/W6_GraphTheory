# Graph Theory Coding Assignment: Task 1 and Task 3

## Team Identity

- Team Name: 
- Member 1: 
  - Name: 
  - NRP: 
- Member 2: 
  - Name: 
  - NRP: 
- Member 3: 
  - Name: 
  - NRP: 

---

## Prerequisites

- Python 3.9+
- Dependencies:
  ```bash
  pip install -r requirements.txt
  ```

  ---

  ## Running the web app

  From the repository root, run `pip install -r requirements.txt`.
  Start it with `flask --app web/app.py run`.
  Visit http://localhost:5000.

## How to Run

### Task 1: Travelling Salesman Problem (SPPG Simulator)

#### 1. Interactive Web Map (Browser UI)
Start the local server:
```bash
python3 -m task1_tsp.app
```
Open `http://127.0.0.1:5000` in your web browser. You can:
- Select preset SPPG facilities or click anywhere on the map to set a custom SPPG.
- Adjust the delivery radius slider (in km).
- Select the TSP solver (Auto, Exact Hamiltonian, or 2-Opt Heuristic).
- View the optimal route overlaid on the road network, visiting sequence, travel distance, estimated travel time, and execution time.

#### 2. Command Line Interface (CLI)
Run directly from terminal:
```bash
# Run with preset location (its, gubeng, downtown, wonokromo, rungkut)
python3 -m task1_tsp.tsp_cli --preset its --radius 2.0 --algo exact

# Run with custom SPPG coordinates
python3 -m task1_tsp.tsp_cli --lat -7.2825 --lon 112.7944 --radius 2.5 --algo auto
```

#### 3. Run Unit Tests
```bash
python3 -m unittest task1_tsp/test_cases.py
```

---

### Task 3: The Knight's Tour Simulator

#### 1. Command Line Interface (Standard Input)
Run interactively:
```bash
python3 -m task3_knights_tour.cli
```
Input format (matching slide 6):
```
5 5
2 2
```
Or via pipe:
```bash
printf "5 5\n2 2\n" | python3 -m task3_knights_tour.cli
```

Optional flags:
- `--grid`: Display the solved step matrix on the chessboard.
- `--stats`: Display execution time and total square statistics.

Example:
```bash
printf "5 5\n2 2\n" | python3 -m task3_knights_tour.cli --grid --stats
```

#### 2. Terminal Visualizer (Step-by-Step Animation)
```bash
python3 -m task3_knights_tour.visualizer 5 5 2 2
```

#### 3. Run Unit Tests
```bash
python3 -m unittest task3_knights_tour/test_cases.py
```

---

## Sample Cases and Expected Outputs

### Task 1 Sample Case

Command:
```bash
python3 -m task1_tsp.tsp_cli --preset its --radius 2.0 --algo exact
```

Expected Output:
```
======================================================================
 TASK 1: SPPG MBG MEALBOX DELIVERY SIMULATOR (SURABAYA)
======================================================================
SPPG Facility Location : Bundaran ITS Sukolilo
Coordinates            : (-7.28250, 112.79440)
Delivery Radius        : 2.0 km
Algorithm Selected     : exact
Routing Network        : Surabaya Digraph (Dijkstra)
----------------------------------------------------------------------
Identified 7 schools within delivery radius.
----------------------------------------------------------------------
 OPTIMAL HAMILTONIAN CYCLE ROUTE SUMMARY
----------------------------------------------------------------------
Algorithm Used         : Exact Hamiltonian (Branch & Bound)
TSP Solver Time        : ~5.8 ms
Total Distance         : 15.69 km
Estimated Travel Time  : 25.2 minutes
Total Stops            : 7 schools + return to SPPG
----------------------------------------------------------------------
 SCHOOL VISITING ORDER:
----------------------------------------------------------------------
Step   School Name                         District     Dist (km)  Time (min)
----------------------------------------------------------------------
Start  [SPPG Hub] Bundaran ITS Sukolilo    -            0.00       0.0
Stop 1  SD Laboratorium UNESA               Sukolilo     0.33       0.7  
Stop 2  SDIT Al Uswah Surabaya              Sukolilo     1.30       2.6  
Stop 3  SD Negeri Keputih No. 245           Sukolilo     2.23       4.0  
Stop 4  SD Negeri Gebang Putih No. 405      Sukolilo     2.08       3.3  
Stop 5  SMP Negeri 19 Surabaya              Sukolilo     0.66       1.3  
Stop 6  SD Negeri Manyar Sabrangan II       Mulyorejo    2.46       3.8  
Stop 7  SMP Negeri 29 Surabaya              Mulyorejo    2.10       3.1  
End    [SPPG Hub] Return to Facility       -            4.53       6.5  
======================================================================
```

---

### Task 3 Sample Case 1: Standard Solvable Board (Slide 6)

Input:
```
5 5
2 2
```

Command:
```bash
printf "5 5\n2 2\n" | python3 -m task3_knights_tour.cli
```

Expected Output:
```
(2, 2)
(3, 4)
(4, 2)
(3, 0)
(1, 1)
(0, 3)
(2, 4)
(4, 3)
(3, 1)
(1, 0)
(0, 2)
(1, 4)
(3, 3)
(4, 1)
(2, 0)
(0, 1)
(1, 3)
(3, 2)
(4, 4)
(2, 3)
(0, 4)
(1, 2)
(0, 0)
(2, 1)
(4, 0)
```

---

### Task 3 Sample Case 2: Unsolvable Board

Input:
```
3 3
0 0
```

Command:
```bash
printf "3 3\n0 0\n" | python3 -m task3_knights_tour.cli
```

Expected Output:
```
path not found
```
