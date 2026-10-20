# Graph Theory Coding Assignment: Task 2 and Task 3

## Team Identity

- Team Name: 
- Member 1: 
  - Name: Naila Sa'ada Cahyani 
  - NRP: 5025251258
- Member 2: 
  - Name: Lina Fatima Azzahra Badr
  - NRP: 5025251168

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

  ---

  ## Running the CLI (Task 3: Knight's Tour)

  From the repository root:

  ```bash
  python task3/interface/cli/main.py
  ```

  Input is read from standard input, two lines of two whole numbers each:

  1. `cols rows`: board dimensions
  2. `start_col start_row`: the knight's starting square

  Example:

  ```bash
  printf "5 5\n0 0\n" | python task3/interface/cli/main.py
  ```

  Output is the tour as `(row,col)` squares separated by spaces, or `path not found`
  if no complete tour exists. Invalid input prints `error: ...` to stderr and exits with code 1.

  ---

  ## Running the CLI (Task 2: Directed Chinese Postman / DLH Simulator)

  From the repository root:

  ```bash
  python -m task2.interface.cli.run_task2_cli
  ```

  The program prompts for three values. Press Enter to accept the default:

  1. Latitude (default `-7.2825`)
  2. Longitude (default `112.7944`)
  3. Radius in km (default `1.5`)

  Example (all defaults):

  ```bash
  printf "\n\n\n" | python -m task2.interface.cli.run_task2_cli
  ```

  It fetches the live road network from OpenStreetMap, so an internet connection is required.
  The output is a summary of the simulation results.

  ## AI Involved
  AI Involved: https://share.gemini.google/ewMdqViiX2Jn | https://share.gemini.google/bTswYCwlnfqW
