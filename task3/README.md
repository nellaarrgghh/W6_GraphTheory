# Knight's Tour

## What it does

This project finds a knight's tour on a rectangular board from a selected starting square. It provides a command-line interface and an interactive 8x8 Flask board that animates the result.

## Install

From inside `task3/`, install the dependencies:

```bash
pip install -r requirements.txt
```

## Run the web app

From inside `task3/`, run:

```bash
flask --app interface/web/app.py run
```

Open the displayed local URL in a browser.

## Run the CLI

From inside `task3/`, provide the board dimensions and starting square:

```bash
printf "5 5\n2 2\n" | python -m interface.cli.main
```

The output contains zero-indexed `col,row` coordinates separated by spaces, or `path not found`.

## How the algorithm works

The algorithm uses depth-first search with backtracking. It marks each visited square, recursively explores legal unvisited knight moves, and unmarks squares when a branch fails. Candidate moves are sorted using Warnsdorff's rule, which tries the square with the fewest onward moves first. The worst-case complexity is exponential, but this ordering makes common boards such as 8x8 fast in practice.
