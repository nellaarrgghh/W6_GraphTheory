from task3.algorithm.knight_tour import find_knights_tour
from task3.engine.service import solve


def test_5_by_5_tour_is_valid():
    path = find_knights_tour(5, 5, 2, 2)
    assert path is not None
    assert len(path) == 25
    assert len(set(path)) == 25
    assert all(
        sorted((abs(next_col - col), abs(next_row - row))) == [1, 2]
        for (col, row), (next_col, next_row) in zip(path, path[1:])
    )


def test_3_by_3_center_has_no_tour():
    assert find_knights_tour(3, 3, 1, 1) is None


def test_invalid_service_input_returns_message():
    answer = solve(-5, 5, 2, 2)
    assert answer["found"] is False
    assert answer["message"]
