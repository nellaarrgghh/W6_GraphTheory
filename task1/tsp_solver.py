"""
tsp_solver.py - Hamiltonian Cycle TSP Solver for SPPG Mealbox Delivery
Implements Exact Branch-and-Bound and 2-Opt Heuristic solvers
to find minimum-cost Hamiltonian cycles on road network metric closures.
"""

import time
import math
from typing import List, Dict, Any, Tuple
from task1_tsp.router import RoadDigraph, haversine

class TSPSolver:
    """Hamiltonian Cycle TSP Solver with Digraph road integration."""

    def __init__(self, router: RoadDigraph = None):
        self.router = router if router else RoadDigraph()

    def solve_sppg_delivery(
        self,
        sppg_coord: Tuple[float, float],
        schools: List[Dict[str, Any]],
        algorithm: str = "auto",
        prefer_osrm: bool = False
    ) -> Dict[str, Any]:
        """
        Computes the complete TSP route for delivering MBG mealboxes
        from the SPPG to all designated schools and returning to the SPPG.
        
        Args:
            sppg_coord: (lat, lon) of the catering facility
            schools: List of school dicts [{'id', 'name', 'lat', 'lon', ...}]
            algorithm: 'exact', 'heuristic_2opt', or 'auto'
            prefer_osrm: whether to prefer OSRM online over local Digraph
        """
        start_time = time.perf_counter()

        # If no schools in radius
        if not schools:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return {
                "tour_indices": [0],
                "school_order": [],
                "total_distance_km": 0.0,
                "total_time_min": 0.0,
                "solver_time_ms": round(elapsed_ms, 2),
                "algorithm_used": "none",
                "route_segments": [],
                "full_polyline": []
            }

        # Build list of all locations: index 0 is SPPG, 1..N are schools
        locations = [{"id": "SPPG", "name": "SPPG Hub (MBG Center)", "lat": sppg_coord[0], "lon": sppg_coord[1], "type": "SPPG"}]
        locations.extend(schools)
        num_locs = len(locations)

        # 1. Compute all-pairs shortest path matrix using Digraph Router
        # dist_matrix[i][j] holds road distance in meters
        dist_matrix = [[0.0] * num_locs for _ in range(num_locs)]
        route_cache = {}

        for i in range(num_locs):
            for j in range(num_locs):
                if i == j:
                    dist_matrix[i][j] = 0.0
                else:
                    route = self.router.get_route(
                        locations[i]["lat"], locations[i]["lon"],
                        locations[j]["lat"], locations[j]["lon"],
                        prefer_osrm=prefer_osrm
                    )
                    dist_matrix[i][j] = route["distance_m"]
                    route_cache[(i, j)] = route

        # 2. Select Hamiltonian Cycle Algorithm
        if algorithm == "auto":
            selected_algo = "exact" if num_locs <= 12 else "heuristic_2opt"
        else:
            selected_algo = algorithm

        tsp_calc_start = time.perf_counter()
        if selected_algo == "exact":
            tour, best_cost = self._solve_exact_branch_bound(dist_matrix, num_locs)
            algo_label = "Exact Hamiltonian (Branch & Bound)"
        else:
            tour, best_cost = self._solve_2opt(dist_matrix, num_locs)
            algo_label = "Heuristic Hamiltonian (2-Opt)"

        solver_time_ms = (time.perf_counter() - tsp_calc_start) * 1000.0

        # 3. Stitch road polyline and build visiting order
        full_polyline = []
        route_segments = []
        total_time_sec = 0.0
        total_dist_meters = 0.0
        school_order = []

        for step in range(len(tour) - 1):
            u_idx = tour[step]
            v_idx = tour[step + 1]
            seg_route = route_cache.get((u_idx, v_idx))

            total_dist_meters += seg_route["distance_m"]
            total_time_sec += seg_route["travel_time_s"]

            # Add to continuous polyline
            coords = seg_route["coordinates"]
            if not full_polyline:
                full_polyline.extend(coords)
            else:
                full_polyline.extend(coords[1:])

            route_segments.append({
                "from_name": locations[u_idx]["name"],
                "to_name": locations[v_idx]["name"],
                "distance_m": seg_route["distance_m"],
                "travel_time_s": seg_route["travel_time_s"],
                "coordinates": coords
            })

            # Record school in visiting order (exclude return to SPPG)
            if v_idx != 0:
                school_order.append({
                    "order": len(school_order) + 1,
                    "id": locations[v_idx]["id"],
                    "name": locations[v_idx]["name"],
                    "district": locations[v_idx].get("district", "-"),
                    "lat": locations[v_idx]["lat"],
                    "lon": locations[v_idx]["lon"],
                    "distance_from_prev_km": round(seg_route["distance_m"] / 1000.0, 2),
                    "travel_time_from_prev_min": round(seg_route["travel_time_s"] / 60.0, 1)
                })

        return {
            "tour_indices": tour,
            "school_order": school_order,
            "total_distance_km": round(total_dist_meters / 1000.0, 2),
            "total_time_min": round(total_time_sec / 60.0, 1),
            "solver_time_ms": round(solver_time_ms, 2),
            "algorithm_used": algo_label,
            "route_segments": route_segments,
            "full_polyline": full_polyline
        }

    def _solve_exact_branch_bound(self, dist_matrix: List[List[float]], n: int) -> Tuple[List[int], float]:
        """
        Exact Branch-and-Bound algorithm to find optimal Hamiltonian Cycle.
        Guarantees minimum cost tour starting and ending at node 0.
        """
        best_tour = None
        best_cost = float("inf")

        # Precompute minimum outgoing edges for lower bound estimation
        min_out = [min(dist_matrix[i][j] for j in range(n) if i != j) for i in range(n)]

        def branch_and_bound(curr_node: int, visited_mask: int, current_cost: float, path: List[int]):
            nonlocal best_tour, best_cost

            # Base case: all nodes visited, must return to start (node 0)
            if visited_mask == (1 << n) - 1:
                return_cost = current_cost + dist_matrix[curr_node][0]
                if return_cost < best_cost:
                    best_cost = return_cost
                    best_tour = path + [0]
                return

            # Compute lower bound: current cost + minimum edges out of unvisited nodes
            bound = current_cost
            for i in range(n):
                if not (visited_mask & (1 << i)):
                    bound += min_out[i]

            if bound >= best_cost:
                return  # Prune search branch

            # Order unvisited neighbors by edge cost
            unvisited = []
            for nxt in range(n):
                if not (visited_mask & (1 << nxt)):
                    unvisited.append((dist_matrix[curr_node][nxt], nxt))
            unvisited.sort(key=lambda x: x[0])

            for cost_edge, nxt in unvisited:
                if current_cost + cost_edge < best_cost:
                    branch_and_bound(nxt, visited_mask | (1 << nxt), current_cost + cost_edge, path + [nxt])

        branch_and_bound(0, 1, 0.0, [0])
        return best_tour, best_cost

    def _solve_2opt(self, dist_matrix: List[List[float]], n: int) -> Tuple[List[int], float]:
        """
        Heuristic Hamiltonian Cycle using Nearest Neighbor + 2-Opt local search.
        Finds high-quality TSP solutions in milliseconds.
        """
        # 1. Greedy Nearest Neighbor initial tour
        visited = [False] * n
        tour = [0]
        visited[0] = True

        for _ in range(n - 1):
            curr = tour[-1]
            next_node = None
            min_dist = float("inf")
            for j in range(n):
                if not visited[j] and dist_matrix[curr][j] < min_dist:
                    min_dist = dist_matrix[curr][j]
                    next_node = j
            tour.append(next_node)
            visited[next_node] = True
        tour.append(0)  # Close cycle

        def tour_cost(t: List[int]) -> float:
            return sum(dist_matrix[t[k]][t[k + 1]] for k in range(len(t) - 1))

        # 2. Iterative 2-Opt Edge Swaps
        improved = True
        best_cost = tour_cost(tour)

        while improved:
            improved = False
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    # Cost difference of swapping edge (i-1 -> i) and (j -> j+1)
                    # with (i-1 -> j) and (i -> j+1)
                    old_cost = dist_matrix[tour[i - 1]][tour[i]] + dist_matrix[tour[j]][tour[j + 1]]
                    new_cost = dist_matrix[tour[i - 1]][tour[j]] + dist_matrix[tour[i]][tour[j + 1]]

                    if new_cost < old_cost - 1e-6:
                        # Reverse subsegment tour[i:j+1]
                        tour[i:j + 1] = reversed(tour[i:j + 1])
                        best_cost = tour_cost(tour)
                        improved = True
                        break
                if improved:
                    break

        return tour, best_cost
