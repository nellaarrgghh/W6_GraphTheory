"""Task 1 in the terminal: SPPG school delivery route with Held-Karp."""

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from task1.engine.osm_data import DEFAULT_CACHE_DIR, load_demo, load_osm
from task1.engine.service import solve

# Default SPPG location is ITS Surabaya.
DEFAULT_LAT = -7.2825
DEFAULT_LNG = 112.7944
DEFAULT_RADIUS = 1.0


def make_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lat", type=float, help=f"SPPG latitude (default {DEFAULT_LAT})")
    parser.add_argument("--lng", type=float, help=f"SPPG longitude (default {DEFAULT_LNG})")
    parser.add_argument("--radius", type=float, help=f"radius in km (default {DEFAULT_RADIUS})")
    parser.add_argument("--demo", action="store_true", help="use a small fake road grid instead of OSM")
    parser.add_argument("--offline", action="store_true", help="never download, only use the cache")
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR, help="where the OSM cache is")
    return parser


def ask_number(prompt, default):
    text = input(f"{prompt} [Default: {default}]: ").strip()
    return float(text) if text else default


def print_results(result):
    print("\n========== Results ==========")
    print("School visiting order:")
    print("  Start: SPPG")
    for school in result["school_order"]:
        print(f"  {school['order']}. {school['name']}")
    print("  End: SPPG")
    print(f"\nTotal distance: {result['total_distance_km']:.3f} km")
    print(f"Estimated travel time: {result['total_time_min']:.2f} minutes")
    print(f"TSP solver execution time: {result['solver_time_ms']:.3f} ms")


def main(argv=None):
    args = make_parser().parse_args(argv)
    print("Running Task 1: SPPG School Delivery (Held-Karp TSP) [CLI Mode]")
    print("-" * 60)
    try:
        if args.lat is None and args.lng is None and args.radius is None:
            lat = ask_number("Enter Latitude", DEFAULT_LAT)
            lng = ask_number("Enter Longitude", DEFAULT_LNG)
            radius = ask_number("Enter Radius in km", DEFAULT_RADIUS)
        else:
            lat = DEFAULT_LAT if args.lat is None else args.lat
            lng = DEFAULT_LNG if args.lng is None else args.lng
            radius = DEFAULT_RADIUS if args.radius is None else args.radius

        if args.demo:
            print("\nUsing the fake demo grid (not real OpenStreetMap data).")
            dataset = load_demo(lat, lng)
        else:
            print(f"\nLoading OSM roads and schools from {args.cache_dir} ...")
            dataset = load_osm(args.cache_dir, download=not args.offline)

        result = solve(dataset, lat, lng, radius)
    except (ValueError, OSError, ImportError, EOFError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 130

    print_results(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
