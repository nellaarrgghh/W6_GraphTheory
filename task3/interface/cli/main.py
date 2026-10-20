"""Command-line interface for the Knight's Tour."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from task3.engine.service import solve


def main() -> None:
    try:
        first = sys.stdin.readline()
        second = sys.stdin.readline()
        if not first or not second:
            raise ValueError("missing input line")
        first_tokens = first.split()
        second_tokens = second.split()
        if len(first_tokens) != 2 or len(second_tokens) != 2:
            raise ValueError("each line must contain exactly 2 integers")
        values = [int(token) for token in first_tokens + second_tokens]
    except ValueError as exc:
        sys.stderr.write(f"error: {exc}\n")
        sys.exit(1)

    outcome = solve(*values)
    if outcome["status"] == "solved":
        print(" ".join(f"{col},{row}" for col, row in outcome["path"]))
    elif outcome["status"] == "path_not_found":
        print("path not found")
    else:
        sys.stderr.write(f"error: {outcome['message']}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
