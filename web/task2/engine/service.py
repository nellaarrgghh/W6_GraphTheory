import re
import time
import osmnx as ox
import networkx as nx
from task1.engine.osm_data import DEFAULT_CACHE_DIR, haversine_m, load_osm_once
from task1.engine.road_tour import edge_points
from task2.algorithm.chinese_postman import solve_dcpp

# The assignment asks for these road types. This also matches the "_link" ramps.
MAJOR_ROADS = re.compile("trunk|primary|secondary|tertiary")


def is_major_road(highway):
    # OSM sometimes stores a list of types for one road, str() handles both.
    return MAJOR_ROADS.search(str(highway)) is not None


def solve(lat, lng, radius_km):
    """
    Solves the Directed Chinese Postman Problem (DCPP) for Task 2 (DLH Simulator)
    using the saved Surabaya road network (the same cache as Task 1).
    """
    # Same saved road data as Task 1, so no download from Overpass every time.
    try:
        city = load_osm_once(DEFAULT_CACHE_DIR)
    except (OSError, ValueError, ImportError) as e:
        return {
            "status": "error",
            "message": f"Road data not loaded: {e}. Run python -m task1.engine.osm_data --download first."
        }
    G = city.graph
    radius_meters = radius_km * 1000

    # Keep only major roads that are fully inside the radius circle.
    inside = set()
    for node, data in G.nodes(data=True):
        if haversine_m(lat, lng, data['y'], data['x']) <= radius_meters:
            inside.add(node)
    keep = []
    for u, v, key, data in G.out_edges(inside, keys=True, data=True):
        if v in inside and is_major_road(data.get('highway')):
            keep.append((u, v, key))
    G_sub = G.edge_subgraph(keep).copy()

    if len(G_sub.nodes) == 0:
        return {"status": "no_roads_found"}

    # Find the nearest network node to the chosen base coordinates
    base_node = ox.distance.nearest_nodes(G_sub, X=lng, Y=lat)

    # Roads that can't be reached from the base (or can't get back to it) are ignored.
    if not nx.is_strongly_connected(G_sub):
        comp = next(c for c in nx.strongly_connected_components(G_sub) if base_node in c)
        G_sub = G_sub.subgraph(comp).copy()

    # Run the DCPP algorithm from the algorithm module
    start_time = time.time()
    G_aug, route_edges = solve_dcpp(G_sub, base_node)
    exec_time = time.time() - start_time

    total_distance_m = 0
    street_order = []
    route_coords = []

    for u, v, key in route_edges:
        d = G_aug[u][v][key]
        street_name = d.get('name', 'Unnamed Road')
        if isinstance(street_name, list):
            street_name = ", ".join(street_name)
        street_order.append(street_name)
        total_distance_m += d['length']
        # Follow the real shape of the road instead of a straight line.
        route_coords.append([list(point) for point in edge_points(G_aug, u, v, d)])

    total_distance_km = total_distance_m / 1000.0
    est_time_mins = (total_distance_km / 25.0) * 60  # Assumes 25 km/h urban truck speed

    return {
        "status": "Solved",
        "total_distance_km": round(total_distance_km, 2),
        "est_time_mins": round(est_time_mins, 1),
        "exec_time_sec": round(exec_time, 3),
        "base": [lat, lng],
        "street_order": street_order[:30],  # Preview of the first 30 streets
        "route_coords": route_coords
    }
