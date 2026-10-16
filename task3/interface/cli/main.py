"""Command-line interface for the Knight's Tour."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from task3.engine.service import solve_knights_tour


def main() -> None:
    first_line = input().split()
    second_line = input().split()
    try:
        values = [int(value) for value in first_line + second_line]
        if len(values) != 4:
            raise ValueError
    except ValueError:
        print("path not found")
        return

    result = solve_knights_tour(*values)
    if result["found"]:
        print(" ".join(f"{col},{row}" for col, row in result["path"]))
    else:
        print("path not found")


if __name__ == "__main__":
    main()
