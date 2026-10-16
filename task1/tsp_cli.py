"""
tsp_cli.py - Command Line Interface for Task 1: SPPG Mealbox TSP Delivery Simulator
Allows testing and grading TSP routes directly from terminal without a browser.
"""

import argparse
import json
from pathlib import Path
from task1_tsp.router import RoadDigraph, haversine
from task1_tsp.tsp_solver import TSPSolver

PRESETS = {
    "its": (-7.2825, 112.7944, "Bundaran ITS Sukolilo"),
    "gubeng": (-7.2654, 112.7520, "Stasiun Gubeng"),
    "downtown": (-7.2625, 112.7480, "Balai Kota / Genteng"),
    "wonokromo": (-7.2885, 112.7385, "Taman Bungkul / Wonokromo"),
    "rungkut": (-7.3180, 112.7750, "MERR Rungkut Madya")
}

def main():
    parser = argparse.ArgumentParser(
        description="SPPG MBG Mealbox Delivery Simulator - TSP Hamiltonian Solver (Surabaya)"
    )
    parser.add_argument("--preset", choices=list(PRESETS.keys()), default="its",
                        help="Choose a preset SPPG hub location (default: its)")
    parser.add_argument("--lat", type=float, default=None, help="Custom SPPG Latitude")
    parser.add_argument("--lon", type=float, default=None, help="Custom SPPG Longitude")
    parser.add_argument("--radius", type=float, default=2.5, help="Delivery radius in km (default: 2.5)")
    parser.add_argument("--algo", choices=["auto", "exact", "heuristic_2opt"], default="auto",
                        help="TSP Hamiltonian solver algorithm (default: auto)")
    parser.add_argument("--osrm", action="store_true", help="Prefer OSRM online routing if available")

    args = parser.parse_args()

    # Determine SPPG coordinates
    if args.lat is not None and args.lon is not None:
        sppg_lat, sppg_lon = args.lat, args.lon
        location_desc = f"Custom ({sppg_lat:.4f}, {sppg_lon:.4f})"
    else:
        sppg_lat, sppg_lon, location_desc = PRESETS[args.preset]

    print("=" * 70)
    print(" TASK 1: SPPG MBG MEALBOX DELIVERY SIMULATOR (SURABAYA)")
    print("=" * 70)
    print(f"SPPG Facility Location : {location_desc}")
    print(f"Coordinates            : ({sppg_lat:.5f}, {sppg_lon:.5f})")
    print(f"Delivery Radius        : {args.radius:.1f} km")
    print(f"Algorithm Selected     : {args.algo}")
    print(f"Routing Network        : {'OSM OSRM (Online)' if args.osrm else 'Surabaya Digraph (Dijkstra)'}")
    print("-" * 70)

    # Load schools
    data_dir = Path(__file__).resolve().parent / "data"
    with open(data_dir / "surabaya_schools.json", "r", encoding="utf-8") as f:
        all_schools = json.load(f)

    radius_m = args.radius * 1000.0
    schools_in_radius = [
        s for s in all_schools
        if haversine(sppg_lat, sppg_lon, s["lat"], s["lon"]) <= radius_m
    ]

    print(f"Identified {len(schools_in_radius)} schools within delivery radius.")

    if not schools_in_radius:
        print("No schools found within the given radius. Try increasing --radius.")
        return

    # Solve TSP
    router = RoadDigraph()
    solver = TSPSolver(router)
    res = solver.solve_sppg_delivery(
        sppg_coord=(sppg_lat, sppg_lon),
        schools=schools_in_radius,
        algorithm=args.algo,
        prefer_osrm=args.osrm
    )

    print("-" * 70)
    print(" OPTIMAL HAMILTONIAN CYCLE ROUTE SUMMARY")
    print("-" * 70)
    print(f"Algorithm Used         : {res['algorithm_used']}")
    print(f"TSP Solver Time        : {res['solver_time_ms']:.2f} ms")
    print(f"Total Distance         : {res['total_distance_km']:.2f} km")
    print(f"Estimated Travel Time  : {res['total_time_min']:.1f} minutes")
    print(f"Total Stops            : {len(res['school_order'])} schools + return to SPPG")
    print("-" * 70)
    print(" SCHOOL VISITING ORDER:")
    print("-" * 70)
    print(f"{'Step':<6} {'School Name':<35} {'District':<12} {'Dist (km)':<10} {'Time (min)'}")
    print("-" * 70)
    print(f"{'Start':<6} {'[SPPG Hub] ' + location_desc:<35} {'-':<12} {'0.00':<10} {'0.0'}")

    for s in res["school_order"]:
        print(f"Stop {s['order']:<2} {s['name'][:34]:<35} {s['district']:<12} {s['distance_from_prev_km']:<10.2f} {s['travel_time_from_prev_min']:<5.1f}")

    # Return to SPPG
    last_seg = res["route_segments"][-1] if res["route_segments"] else None
    return_dist = (last_seg["distance_m"] / 1000.0) if last_seg else 0.0
    return_time = (last_seg["travel_time_s"] / 60.0) if last_seg else 0.0
    print(f"{'End':<6} {'[SPPG Hub] Return to Facility':<35} {'-':<12} {return_dist:<10.2f} {return_time:<5.1f}")
    print("=" * 70)

if __name__ == "__main__":
    main()
