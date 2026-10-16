"""
router.py - Digraph Routing Engine for Surabaya Road Network
Provides Dijkstra shortest path calculations on the Surabaya Digraph,
coordinate snapping, and optional OSRM online fallback.
"""

import json
import math
import heapq
import urllib.request
import urllib.parse
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two points in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    return 2.0 * R * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

class RoadDigraph:
    """Directed road network graph of Surabaya with Dijkstra routing."""

    def __init__(self, json_path: str = None):
        if json_path is None:
            json_path = str(DATA_DIR / "surabaya_roads.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.nodes = {n["id"]: n for n in data["nodes"]}
        # Adjacency list: node_id -> list of (neighbor_id, distance_m, travel_time_s, road_name)
        self.adj = {n_id: [] for n_id in self.nodes}
        for edge in data["edges"]:
            u = edge["from"]
            v = edge["to"]
            dist = edge["distance_m"]
            tt = edge["travel_time_s"]
            name = edge.get("road_name", "Street")
            if u in self.adj and v in self.nodes:
                self.adj[u].append((v, dist, tt, name))

    def snap_to_node(self, lat: float, lon: float) -> str:
        """Finds closest road intersection node to given coordinates."""
        best_node = None
        min_dist = float("inf")
        for node_id, node in self.nodes.items():
            d = haversine(lat, lon, node["lat"], node["lon"])
            if d < min_dist:
                min_dist = d
                best_node = node_id
        return best_node

    def dijkstra(self, start_id: str, end_id: str):
        """
        Runs Dijkstra algorithm on directed road graph.
        Returns: (distance_meters, travel_time_seconds, list_of_node_ids)
        """
        if start_id == end_id:
            return 0.0, 0.0, [start_id]

        dist = {n_id: float("inf") for n_id in self.nodes}
        time_sec = {n_id: float("inf") for n_id in self.nodes}
        parent = {n_id: None for n_id in self.nodes}

        dist[start_id] = 0.0
        time_sec[start_id] = 0.0
        pq = [(0.0, start_id)]

        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            if u == end_id:
                break

            for v, edge_dist, edge_tt, _ in self.adj[u]:
                new_d = d + edge_dist
                if new_d < dist[v]:
                    dist[v] = new_d
                    time_sec[v] = time_sec[u] + edge_tt
                    parent[v] = u
                    heapq.heappush(pq, (new_d, v))

        if dist[end_id] == float("inf"):
            # Fallback if disconnected
            return None, None, []

        # Reconstruct path
        path = []
        curr = end_id
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        path.reverse()

        return dist[end_id], time_sec[end_id], path

    def get_path_coordinates(self, node_ids: list) -> list:
        """Returns [[lat, lon], ...] polyline for list of node IDs."""
        coords = []
        for nid in node_ids:
            if nid in self.nodes:
                coords.append([self.nodes[nid]["lat"], self.nodes[nid]["lon"]])
        return coords

    def get_route(self, lat1: float, lon1: float, lat2: float, lon2: float, prefer_osrm: bool = False):
        """
        Finds shortest road route between two coordinate points.
        Optionally attempts OSRM driving API; falls back to Digraph Dijkstra.
        """
        # Try OSRM if requested
        if prefer_osrm:
            osrm_res = self._query_osrm(lat1, lon1, lat2, lon2)
            if osrm_res:
                return osrm_res

        # Dijkstra on Road Digraph
        u = self.snap_to_node(lat1, lon1)
        v = self.snap_to_node(lat2, lon2)

        dist, tt, path_nodes = self.dijkstra(u, v)
        if path_nodes:
            coords = [[lat1, lon1]] + self.get_path_coordinates(path_nodes) + [[lat2, lon2]]
            # Add snap connection distances
            snap_start = haversine(lat1, lon1, self.nodes[u]["lat"], self.nodes[u]["lon"])
            snap_end = haversine(lat2, lon2, self.nodes[v]["lat"], self.nodes[v]["lon"])
            total_dist = dist + snap_start + snap_end
            # Snap travel time at ~30 km/h (8.33 m/s)
            total_tt = tt + (snap_start + snap_end) / 8.33
            return {
                "distance_m": round(total_dist, 1),
                "travel_time_s": round(total_tt, 1),
                "coordinates": coords,
                "source": "digraph_dijkstra"
            }

        # Fallback to straight-line if graph path fails
        direct_dist = haversine(lat1, lon1, lat2, lon2)
        return {
            "distance_m": round(direct_dist, 1),
            "travel_time_s": round(direct_dist / 8.33, 1),
            "coordinates": [[lat1, lon1], [lat2, lon2]],
            "source": "euclidean_fallback"
        }

    def _query_osrm(self, lat1: float, lon1: float, lat2: float, lon2: float):
        """Queries OSRM driving service with 3-second timeout."""
        try:
            url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
            req = urllib.request.Request(url, headers={"User-Agent": "ITS_GraphTheory_W6/1.0"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("code") == "Ok" and data.get("routes"):
                    r = data["routes"][0]
                    coords = [[pt[1], pt[0]] for pt in r["geometry"]["coordinates"]]
                    return {
                        "distance_m": round(r["distance"], 1),
                        "travel_time_s": round(r["duration"], 1),
                        "coordinates": coords,
                        "source": "osrm"
                    }
        except Exception:
            pass
        return None
