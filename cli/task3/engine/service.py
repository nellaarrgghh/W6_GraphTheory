"""Engine service for solving the Knight's Tour."""

import time
from typing import Any

from ..algorithm.knight_tour import find_knights_tour


def solve(cols: Any, rows: Any, start_col: Any, start_row: Any) -> dict[str, Any]:
    """Validate input, time the algorithm, and return the tour status."""
    if any(type(item) is not int for item in (cols, rows, start_col, start_row)):
        return _reject("all values must be whole numbers")
    if cols < 1 or rows < 1:
        return _reject("board needs at least 1 row and 1 column")
    if cols > 12 or rows > 12:
        return _reject("board side cannot exceed 12")
    if not 0 <= start_col < cols:
        return _reject(
            f"knight column {start_col} is outside the {cols}-column board (valid 0 to {cols - 1})"
        )
    if not 0 <= start_row < rows:
        return _reject(
            f"knight row {start_row} is outside the {rows}-row board (valid 0 to {rows - 1})"
        )

    start_time = time.perf_counter()
    path = find_knights_tour(cols, rows, start_col, start_row)
    duration_ms = (time.perf_counter() - start_time) * 1000

    if path is None:
        return {
            "status": "path_not_found",
            "path": [],
            "execution_time_ms": duration_ms,
            "message": "path not found",
        }
    return {
        "status": "solved",
        "path": [[col, row] for col, row in path],
        "execution_time_ms": duration_ms,
        "message": "",
    }


def _reject(message: str) -> dict[str, Any]:
    return {"status": "invalid_input", "path": [], "execution_time_ms": 0.0, "message": message}
