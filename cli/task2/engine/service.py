import time
import osmnx as ox
import networkx as nx
from task2.algorithm.chinese_postman import solve_dcpp

def solve(lat, lng, radius_km):
    """
    Solves the Directed Chinese Postman Problem (DCPP) for Task 2 (DLH Simulator)
    using live OpenStreetMap road network data.
    """
    start_time = time.time()
    center_point = (lat, lng)
    radius_meters = radius_km * 1000
    
    # Filter for major road classifications as required by the assignment guidelines
    custom_filter = '["highway"~ "trunk|primary|secondary|tertiary|trunk_link|primary_link|secondary_link|tertiary_link"]'
    
    # Always fetch directly from OpenStreetMap via OSMnx
    try:
        G_sub = ox.graph_from_point(
            center_point=center_point,
            dist=radius_meters,
            custom_filter=custom_filter,
            network_type="drive",
            simplify=True,
            retain_all=False
        )
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch road network from OpenStreetMap: {str(e)}"
        }

    if len(G_sub.nodes) == 0:
        return {"status": "no_roads_found"}

    # Find the nearest network node to the chosen base coordinates
    base_node = ox.distance.nearest_nodes(G_sub, X=lng, Y=lat)

    # Ensure the subgraph is strongly connected containing the base node
    if not nx.is_strongly_connected(G_sub):
        sccs = list(nx.strongly_connected_components(G_sub))
        comp = next((c for c in sccs if base_node in c), sccs[0] if sccs else {base_node})
        G_sub = G_sub.subgraph(comp).copy()
        if base_node not in G_sub and len(G_sub.nodes) > 0:
            base_node = list(G_sub.nodes())[0]

    # Run the DCPP algorithm from the algorithm module
    G_aug, route_edges = solve_dcpp(G_sub, base_node)
    exec_time = time.time() - start_time

    total_distance_m = 0
    street_order = []
    route_coords = []
    
    for u, v in route_edges:
        edge_data = G_aug.get_edge_data(u, v)
        street_name = "Unnamed Road"
        length = 0
        if edge_data:
            first_key = list(edge_data.keys())[0]
            d = edge_data[first_key]
            street_name = d.get('name', 'Unnamed Road')
            if isinstance(street_name, list):
                street_name = ", ".join(street_name)
            length = d.get('length', 0)
            total_distance_m += length
            
        street_order.append(street_name)
        if u in G_sub.nodes and v in G_sub.nodes:
            route_coords.append([
                [G_sub.nodes[u]['y'], G_sub.nodes[u]['x']], 
                [G_sub.nodes[v]['y'], G_sub.nodes[v]['x']]
            ])

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