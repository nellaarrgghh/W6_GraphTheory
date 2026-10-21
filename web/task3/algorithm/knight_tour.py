"""Find tours with DFS backtracking and Warnsdorff move ordering.

Warnsdorff's rule visits candidates with the fewest onward moves first.
The worst-case time complexity is exponential, despite faster typical runs.
"""

from __future__ import annotations

_MOVES = (
    (1, 2),
    (2, 1),
    (2, -1),
    (1, -2),
    (-1, -2),
    (-2, -1),
    (-2, 1),
    (-1, 2),
)


def find_knights_tour(
    cols: int, rows: int, start_col: int, start_row: int
) -> list[tuple[int, int]] | None:
    """Return ordered (col, row) path visiting all squares, or None if impossible."""
    if cols <= 0 or rows <= 0:
        return None
    if not (0 <= start_col < cols and 0 <= start_row < rows):
        return None

    visited = [[False] * rows for _ in range(cols)]
    path: list[tuple[int, int]] = []

    def candidates(col: int, row: int) -> list[tuple[int, int]]:
        available = []
        for col_delta, row_delta in _MOVES:
            next_col = col + col_delta
            next_row = row + row_delta
            if (
                0 <= next_col < cols
                and 0 <= next_row < rows
                and not visited[next_col][next_row]
            ):
                # Warnsdorff counts each candidate's available onward moves.
                onward = sum(
                    0 <= next_col + move_col < cols
                    and 0 <= next_row + move_row < rows
                    and not visited[next_col + move_col][next_row + move_row]
                    for move_col, move_row in _MOVES
                )
                available.append((onward, next_col, next_row))
        available.sort()
        return [(next_col, next_row) for _, next_col, next_row in available]

    def search(col: int, row: int) -> bool:
        visited[col][row] = True
        path.append((col, row))
        # The base case means every board square has been visited.
        if len(path) == cols * rows:
            return True

        for next_col, next_row in candidates(col, row):
            # Each recursive call explores one candidate branch.
            if search(next_col, next_row):
                return True

        path.pop()
        # Unmarking lets another branch reuse this square during backtracking.
        visited[col][row] = False
        return False

    return path.copy() if search(start_col, start_row) else None
