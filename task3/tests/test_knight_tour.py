"""Tests for the Knight's Tour engine service."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from task3.engine.service import solve

_OFFSETS = {(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)}


def test_5_by_5_tour_is_valid():
    outcome = solve(5, 5, 2, 2)
    assert outcome["status"] == "solved"
    tour = outcome["path"]
    assert len(tour) == 25
    assert len(set(tuple(square) for square in tour)) == 25
    assert all(
        (next_col - col, next_row - row) in _OFFSETS
        for (col, row), (next_col, next_row) in zip(tour, tour[1:])
    )


def test_3_by_3_center_has_no_tour():
    outcome = solve(3, 3, 1, 1)
    assert outcome["status"] == "path_not_found"
    assert outcome["path"] == []
    assert outcome["message"] == "path not found"


def test_start_column_out_of_bounds():
    outcome = solve(5, 5, 5, 0)
    assert outcome["status"] == "invalid_input"
    assert "column" in outcome["message"]


def test_invalid_dimensions():
    first = solve(5, 2.5, 2, 2)
    second = solve(13, 13, 0, 0)
    assert first["status"] == "invalid_input"
    assert second["status"] == "invalid_input"
