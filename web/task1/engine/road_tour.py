"""Turn a list of schools into a real road route.

1. Snap the SPPG and every school to the nearest road node.
2. Build a distance matrix with Dijkstra (shortest road distance).
3. Solve the matrix with Held-Karp.
4. Expand each leg back into road coordinates so we can draw it on a map.
"""

import time

import networkx as nx

from ..algorithm.held_karp import solve_held_karp
from .osm_data import School, haversine_m

# If the nearest road is further than this, the point is probably not on the map.
MAX_SNAP_M = 500


def nearest_node(graph, lat, lng):
    # ponytail: checks every node, fine for one city (~100k nodes)
    best_node = min(graph.nodes,
                    key=lambda n: haversine_m(lat, lng, graph.nodes[n]["y"], graph.nodes[n]["x"]))
    node = graph.nodes[best_node]
    return best_node, haversine_m(lat, lng, node["y"], node["x"])


def edge_points(graph, u, v, data):
    """(lat, lng) points along one road segment, in the u -> v direction."""
    if "geometry" in data:
        points = [(lat, lng) for lng, lat in data["geometry"].coords]
    else:
        points = [(graph.nodes[u]["y"], graph.nodes[u]["x"]), (graph.nodes[v]["y"], graph.nodes[v]["x"])]
    # A two-way road can share one geometry, so it may be stored backwards.
    start = (graph.nodes[u]["y"], graph.nodes[u]["x"])
    if haversine_m(*start, *points[-1]) < haversine_m(*start, *points[0]):
        points.reverse()
    return points


def plan_road_tour(dataset, lat, lng, schools):
    """Find the shortest round trip SPPG -> all schools -> SPPG on the road graph.

    Stop 0 is always the SPPG, stops 1..n are the schools in the given order.
    """
    start_time = time.perf_counter()
    graph = dataset.graph
    stops = [School("depot", "SPPG", lat, lng)] + list(schools)

    nodes = []
    snap_distances = []
    for stop in stops:
        node, distance = nearest_node(graph, stop.latitude, stop.longitude)
        if distance > MAX_SNAP_M:
            raise ValueError(f"{stop.name} is {distance:.0f} m from the nearest road "
                             f"(limit is {MAX_SNAP_M} m)")
        nodes.append(node)
        snap_distances.append(distance)

    matrix = []
    for i, source in enumerate(nodes):
        lengths = nx.single_source_dijkstra_path_length(graph, source, weight="length")
        row = []
        for j, target in enumerate(nodes):
            if target not in lengths:
                raise ValueError(f"no road path from {stops[i].name} to {stops[j].name}")
            row.append(lengths[target])
        matrix.append(row)
    preprocessing_time = time.perf_counter() - start_time

    solver_start = time.perf_counter()
    route, _ = solve_held_karp(matrix)
    solver_time = time.perf_counter() - solver_start

    total_distance = 0.0
    total_travel_time = 0.0
    coordinates = [(graph.nodes[nodes[0]]["y"], graph.nodes[nodes[0]]["x"])]
    for a, b in zip(route, route[1:]):
        path = nx.shortest_path(graph, nodes[a], nodes[b], weight="length")
        for u, v in zip(path, path[1:]):
            # There can be more than one edge between u and v, take the shortest one.
            data = min(graph[u][v].values(), key=lambda d: d["length"])
            total_distance += data["length"]
            total_travel_time += data["travel_time"]
            points = edge_points(graph, u, v, data)
            if points[0] == coordinates[-1]:
                points = points[1:]
            coordinates.extend(points)

    return {
        "stops": stops,
        "route": route,
        "matrix": matrix,
        "snap_distances_m": snap_distances,
        "coordinates": coordinates,
        "total_distance_m": total_distance,
        "total_travel_seconds": total_travel_time,
        "solver_seconds": solver_time,
        "preprocessing_seconds": preprocessing_time,
    }
