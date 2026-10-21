# Task 3: Knight's Tour (CLI)

Finds a path for a knight that visits every square of the board exactly once.
Only uses the Python standard library.

## Run

From the `cli/` folder, give two lines on stdin: the board size
(`cols rows`, each 1 to 12) and the starting square (`start_col start_row`):

```sh
printf '5 5\n2 2\n' | python -m task3.interface.cli.run_task3_cli
```

or through the menu: `printf '5 5\n2 2\n' | python main.py 3`

In PowerShell: `@('5 5', '2 2') | python main.py 3`

The output is the tour on one line as zero-indexed `(row,col)` squares
separated by spaces, or `path not found`. Bad input prints `error: ...` to
stderr and exits with code 1.

## How it works

Depth-first search with backtracking. It marks each visited square, recursively
explores legal unvisited knight moves, and unmarks squares when a branch fails.
Candidate moves are sorted with Warnsdorff's rule (try the square with the
fewest onward moves first). The worst case is exponential, but this ordering
makes common boards such as 8x8 fast in practice.
