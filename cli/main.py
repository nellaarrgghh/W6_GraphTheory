"""Menu for running Task 1, 2 or 3 in the terminal.

Examples:
    python main.py
    python main.py 1 --demo --radius 1
    printf '5 5\n2 2\n' | python main.py 3
"""

import sys


def main(argv=None):
    args = sys.argv[1:] if argv is None else list(argv)
    if args:
        choice, options = args[0], args[1:]
    else:
        print("Graph Theory [CLI Mode]")
        print("1. Task 1 - SPPG delivery (Held-Karp TSP)")
        print("2. Task 2 - DLH collection (Directed Chinese Postman)")
        print("3. Task 3 - Knight's Tour")
        print("0. Exit")
        try:
            choice = input("Select task [1/2/3/0]: ").strip()
        except (EOFError, KeyboardInterrupt):
            return 0
        options = []

    # Import inside each branch so Task 3 still works without the map libraries.
    if choice == "1":
        from task1.interface.cli.run_task1_cli import main as run_task1
        return run_task1(options)
    if choice == "2":
        from task2.interface.cli.run_task2_cli import main as run_task2
        run_task2()
        return 0
    if choice == "3":
        from task3.interface.cli.run_task3_cli import main as run_task3
        if sys.stdin.isatty():
            # Hint goes to stderr so piped output stays just the path.
            print("Enter 'cols rows' then 'start_col start_row' (e.g. 5 5 / 2 2):", file=sys.stderr)
        run_task3()
        return 0
    if choice == "0":
        return 0
    print("Invalid choice, pick 1, 2, 3 or 0.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
