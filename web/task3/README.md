# Task 3: Knight's Tour (web)

Open `/task3`, enter the board size (columns and rows, 1 to 12) and the
knight's starting square, then press **Generate board**. The chessboard is
built from those numbers with the knight on its start square. Press **Solve**
to animate the tour; the summary lists every move and the execution time.
**Reset** clears the form and the board. Invalid input (e.g. a start square
outside the board) is shown as an error instead of a board.

Coordinates are zero-indexed: column 0 is the left edge, row 0 is the top row.

The page calls `POST /api/task3/solve` with
`{"cols": 5, "rows": 5, "start_col": 2, "start_row": 2}` and gets back
`status` (`solved`, `path_not_found` or `invalid_input`), `path` as
`[col, row]` pairs, `execution_time_ms` and `message`.

## How it works

Depth-first search with backtracking. It marks each visited square, recursively
explores legal unvisited knight moves, and unmarks squares when a branch fails.
Candidate moves are sorted with Warnsdorff's rule (try the square with the
fewest onward moves first). The worst case is exponential, but this ordering
makes common boards such as 8x8 fast in practice.

Tests: `python -m pytest task3/tests -q`
