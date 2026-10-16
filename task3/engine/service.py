"""Validate requests and run the Knight's Tour algorithm."""

import time
from typing import Any

from ..algorithm.knight_tour import find_knights_tour


def solve(cols: Any, rows: Any, start_col: Any, start_row: Any) -> dict[str, Any]:
    """Return a serializable solver response."""
    values = (cols, rows, start_col, start_row)
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        return _invalid("Board and start coordinates must be integers.")
    if cols <= 0 or rows <= 0:
        return _invalid("Board dimensions must be positive integers.")
    if not 0 <= start_col < cols or not 0 <= start_row < rows:
        return _invalid("The starting square must be within the board.")

    started = time.perf_counter()
    path = find_knights_tour(cols, rows, start_col, start_row)
    elapsed = (time.perf_counter() - started) * 1000
    if path is None:
        return {"path": [], "found": False, "execution_time_ms": elapsed, "message": "path not found"}
    return {
        "path": [[col, row] for col, row in path],
        "found": True,
        "execution_time_ms": elapsed,
        "message": "Solved",
    }


def _invalid(message: str) -> dict[str, Any]:
    return {"path": [], "found": False, "execution_time_ms": 0.0, "message": message}
