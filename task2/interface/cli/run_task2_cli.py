"""CLI runner for DLH Simulator."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from task2.engine.service import solve

def main():
    print("Running Task 2: Directed Chinese Postman Problem (DLH Simulator) [CLI Mode]")
    print("-" * 70)
    
    # Default East Surabaya coordinates (ITS Campus) and 1.5 km radius
    default_lat = -7.2825
    default_lng = 112.7944
    default_radius = 1.5
    
    # Prompt user for inputs (pressing Enter will use default values)
    lat_input = input(f"Enter Latitude [Default: {default_lat}]: ").strip()
    lat = float(lat_input) if lat_input else default_lat
    
    lng_input = input(f"Enter Longitude [Default: {default_lng}]: ").strip()
    lng = float(lng_input) if lng_input else default_lng
    
    radius_input = input(f"Enter Radius in km [Default: {default_radius}]: ").strip()
    radius_km = float(radius_input) if radius_input else default_radius
    
    print(f"\nFetching live road network from OpenStreetMap for ({lat}, {lng}) within {radius_km} km...")
    result = solve(lat, lng, radius_km)
    
    print("\n" + "="*30 + " Simulation Results " + "="*30)
    for key, value in result.items():
        if key == "street_order":
            print(f"Street Traversal Preview (first 5): {value[:5]} ... ({len(value)} total segments)")
        elif key == "route_coords":
            print(f"Route Coordinates Generated: {len(value)} segments")
        else:
            print(f"{key}: {value}")
    print("="*80)

if __name__ == "__main__":
    main()