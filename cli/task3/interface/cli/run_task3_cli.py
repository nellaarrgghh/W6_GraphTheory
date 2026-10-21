"""Command-line interface for solving the Knight's Tour.

Reads board dimensions and start position from standard input.
Prints the solved tour squares as (row,col) or an error message.
"""

import sys
from pathlib import Path

# Add the repository root so the engine service can be imported anywhere.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from task3.engine.service import solve


def parse_line(line: str) -> tuple[int, int]:
    """Parse one input line into a pair of integers."""
    # Split the input line into whitespace-separated tokens.
    tokens = line.split()
    if len(tokens) != 2:
        raise ValueError("each line must contain exactly two numbers")

    # Convert both tokens into whole numbers.
    try:
        first_number = int(tokens[0])
        second_number = int(tokens[1])
    except ValueError:
        raise ValueError("all values must be whole numbers")

    return first_number, second_number


def main() -> None:
    """Read inputs, solve the tour, and print the resulting path."""
    # Read two input lines for dimensions and knight start position.
    first_line = sys.stdin.readline()
    second_line = sys.stdin.readline()

    # Parse board dimensions and starting position coordinates.
    try:
        cols, rows = parse_line(first_line)
        start_col, start_row = parse_line(second_line)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)

    # Run the knight's tour algorithm via the engine.
    outcome = solve(cols, rows, start_col, start_row)
    status = outcome["status"]

    # Exit with an error when input validation fails in the engine.
    if status == "invalid_input":
        print(f"error: {outcome['message']}", file=sys.stderr)
        sys.exit(1)

    # Report when no complete tour exists for the given inputs.
    if status == "path_not_found":
        print("path not found")
        return

    # Swap each square from engine (col, row) order to output (row, col).
    if status == "solved":
        squares = []
        for col, row in outcome["path"]:
            squares.append(f"({row},{col})")
        print(" ".join(squares))


# Run the command-line interface when invoked directly.
if __name__ == "__main__":
    main()
