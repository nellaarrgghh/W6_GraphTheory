"""
test_cases.py - Unit Tests for Task 1 TSP SPPG Simulator
Validates Digraph connectivity, Dijkstra routing, Exact Hamiltonian solver, and 2-Opt heuristic.
"""

import unittest
from task1_tsp.router import RoadDigraph, haversine
from task1_tsp.tsp_solver import TSPSolver

class TestTask1TSP(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.router = RoadDigraph()
        cls.solver = TSPSolver(cls.router)

    def test_haversine_distance(self):
        """Test Haversine distance formula."""
        # Distance between Bundaran ITS and Stasiun Gubeng is ~5.5 km straight-line
        dist = haversine(-7.2825, 112.7944, -7.2654, 112.7520)
        self.assertTrue(5000 < dist < 6500, f"Distance {dist} out of expected range")

    def test_dijkstra_shortest_path(self):
        """Test Dijkstra on Surabaya Digraph."""
        dist, tt, path = self.router.dijkstra("n_its_bundaran", "n_gubeng_stasiun")
        self.assertIsNotNone(dist)
        self.assertTrue(dist > 0)
        self.assertEqual(path[0], "n_its_bundaran")
        self.assertEqual(path[-1], "n_gubeng_stasiun")

    def test_exact_hamiltonian_solver(self):
        """Test Exact Branch & Bound Hamiltonian Cycle."""
        dist_matrix = [
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0]
        ]
        tour, cost = self.solver._solve_exact_branch_bound(dist_matrix, 4)
        self.assertEqual(tour[0], 0)
        self.assertEqual(tour[-1], 0)
        self.assertEqual(len(set(tour[:-1])), 4, "Must visit every node exactly once")
        # Optimal cost for this symmetric matrix: 0 -> 1 -> 3 -> 2 -> 0 = 10 + 25 + 30 + 15 = 80
        self.assertEqual(cost, 80)

    def test_heuristic_2opt_solver(self):
        """Test 2-Opt Hamiltonian cycle solver."""
        dist_matrix = [
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0]
        ]
        tour, cost = self.solver._solve_2opt(dist_matrix, 4)
        self.assertEqual(tour[0], 0)
        self.assertEqual(tour[-1], 0)
        self.assertEqual(len(set(tour[:-1])), 4)
        self.assertTrue(cost <= 85)

    def test_sppg_delivery_simulation(self):
        """Test full SPPG simulation with real sample schools."""
        sppg = (-7.2825, 112.7944)
        sample_schools = [
            {"id": "s1", "name": "School A", "lat": -7.2798, "lon": 112.7932, "district": "Sukolilo"},
            {"id": "s2", "name": "School B", "lat": -7.2885, "lon": 112.7845, "district": "Sukolilo"},
            {"id": "s3", "name": "School C", "lat": -7.2789, "lon": 112.7758, "district": "Sukolilo"}
        ]
        res = self.solver.solve_sppg_delivery(sppg, sample_schools, algorithm="exact")
        self.assertEqual(len(res["school_order"]), 3)
        self.assertTrue(res["total_distance_km"] > 0)
        self.assertTrue(res["total_time_min"] > 0)
        self.assertTrue(len(res["full_polyline"]) > 0)

if __name__ == "__main__":
    unittest.main()
