"""Held-Karp dynamic programming for the Traveling Salesman Problem.

dp[(mask, i)] = cheapest cost to start at city 0, visit every city in mask,
and end at city i. Time is O(n^2 * 2^n), so it only works for small n.
"""

import math

# 1 SPPG + 15 schools. Bigger than this gets too slow in Python.
MAX_LOCATIONS = 16


def solve_held_karp(matrix):
    """Return (route, cost) for the shortest round trip starting at city 0.

    matrix[i][j] is the distance from i to j. It can be directed, so
    matrix[i][j] does not have to equal matrix[j][i].
    The route looks like [0, 2, 1, 3, 0].
    """
    n = len(matrix)
    if n == 0 or n > MAX_LOCATIONS:
        raise ValueError(f"need between 1 and {MAX_LOCATIONS} locations, got {n}")
    for row in matrix:
        if len(row) != n:
            raise ValueError("distance matrix must be square")
    if n == 1:
        return [0, 0], 0.0

    # Cities 1..n-1 are stored as bits 0..n-2 of the mask.
    others = n - 1
    full_mask = (1 << others) - 1
    dp = {}
    parent = {}

    for i in range(others):
        dp[(1 << i, i)] = matrix[0][i + 1]
        parent[(1 << i, i)] = None

    for mask in range(1, full_mask + 1):
        for last in range(others):
            if not mask & (1 << last):
                continue
            prev_mask = mask ^ (1 << last)
            if prev_mask == 0:
                continue
            best = math.inf
            best_prev = None
            for prev in range(others):
                if prev_mask & (1 << prev):
                    cost = dp[(prev_mask, prev)] + matrix[prev + 1][last + 1]
                    if cost < best:
                        best = cost
                        best_prev = prev
            dp[(mask, last)] = best
            parent[(mask, last)] = best_prev

    # Close the loop back to city 0.
    best_cost = math.inf
    last = None
    for i in range(others):
        cost = dp[(full_mask, i)] + matrix[i + 1][0]
        if cost < best_cost:
            best_cost = cost
            last = i

    # Follow the parent pointers backwards to rebuild the route.
    route = []
    mask = full_mask
    while last is not None:
        route.append(last + 1)
        prev = parent[(mask, last)]
        mask ^= 1 << last
        last = prev
    route.reverse()
    return [0] + route + [0], best_cost
