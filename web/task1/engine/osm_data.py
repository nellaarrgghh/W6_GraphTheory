"""Load the Surabaya road network and schools from OpenStreetMap.

Downloading takes a few minutes, so the result is saved in data/osm/
(roads.graphml + schools.json) and reused after that.
Run `python -m task1.engine.osm_data --download` to make the cache.
"""

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import networkx as nx

DEFAULT_CACHE_DIR = Path(__file__).resolve().parents[2] / "data" / "osm"
PLACE = "Surabaya, East Java, Indonesia"
OSM_SOURCE = "OpenStreetMap, Surabaya"


@dataclass
class School:
    osm_id: str
    name: str
    latitude: float
    longitude: float


@dataclass
class Dataset:
    graph: nx.MultiDiGraph
    schools: list
    source: str


def haversine_m(lat1, lng1, lat2, lng2):
    """Straight-line distance on the earth in meters."""
    lat1, lng1, lat2, lng2 = map(math.radians, (lat1, lng1, lat2, lng2))
    a = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lng2 - lng1) / 2) ** 2)
    return 2 * 6371009 * math.asin(math.sqrt(min(1.0, a)))


def load_demo(center_lat=-7.2575, center_lng=112.7521):
    """Small fake 4x4 road grid for tests and the --demo flag. Not real data.

    The top and bottom rows are one-way streets so the graph is directed.
    """
    graph = nx.MultiDiGraph(crs="EPSG:4326")
    for row in range(4):
        for col in range(4):
            graph.add_node(row * 4 + col,
                           x=center_lng + (col - 1.5) * 0.003,
                           y=center_lat + (row - 1.5) * 0.003)

    def add_road(a, b, one_way):
        length = haversine_m(graph.nodes[a]["y"], graph.nodes[a]["x"],
                             graph.nodes[b]["y"], graph.nodes[b]["x"])
        # 30 km/h = 8.33 m/s
        graph.add_edge(a, b, length=length, travel_time=length / (30 / 3.6), speed_kph=30.0)
        if not one_way:
            graph.add_edge(b, a, length=length, travel_time=length / (30 / 3.6), speed_kph=30.0)

    for row in range(4):
        for col in range(4):
            node = row * 4 + col
            if col < 3:
                if row == 0:
                    add_road(node, node + 1, one_way=True)
                elif row == 3:
                    add_road(node + 1, node, one_way=True)
                else:
                    add_road(node, node + 1, one_way=False)
            if row < 3:
                add_road(node, node + 4, one_way=False)

    schools = []
    for number, node in enumerate([0, 3, 5, 10, 12, 15], start=1):
        schools.append(School(f"demo/{node}", f"Demo School {number}",
                              graph.nodes[node]["y"], graph.nodes[node]["x"]))
    return Dataset(graph, schools, "Demo grid (fake data, not OpenStreetMap)")


def remove_bad_speed_edges(graph):
    # Some OSM roads have maxspeed=0, which gives an infinite travel time.
    # We just drop those roads instead of guessing a speed.
    bad = []
    for u, v, key, data in graph.edges(keys=True, data=True):
        speed = data.get("speed_kph")
        if not isinstance(speed, (int, float)) or not math.isfinite(speed) or speed <= 0:
            bad.append((u, v, key))
    graph.remove_edges_from(bad)


def read_schools(features):
    """Turn the OSMnx school GeoDataFrame into a list of School objects."""
    schools = {}
    for (element_type, element_id), row in features.to_crs("EPSG:4326").iterrows():
        osm_id = f"{element_type}/{element_id}"
        if osm_id in schools or row.geometry is None or row.geometry.is_empty:
            continue
        # Schools are often polygons, so use a point that is inside the shape.
        point = row.geometry.representative_point()
        name = row.get("name")
        if not isinstance(name, str) or not name.strip():
            name = f"Unnamed school ({osm_id})"
        schools[osm_id] = School(osm_id, name.strip(), float(point.y), float(point.x))
    return [schools[key] for key in sorted(schools)]


def load_osm(cache_dir=DEFAULT_CACHE_DIR, download=False):
    cache_dir = Path(cache_dir)
    graph_file = cache_dir / "roads.graphml"
    schools_file = cache_dir / "schools.json"
    has_cache = graph_file.is_file() and schools_file.is_file()
    if not has_cache and not download:
        raise FileNotFoundError(
            f"No OSM cache in {cache_dir}. Run: python -m task1.engine.osm_data --download")

    import osmnx as ox

    ox.settings.requests_timeout = 120
    ox.settings.cache_folder = str(cache_dir / "http_cache")
    ox.settings.use_cache = True

    if has_cache:
        graph = ox.load_graphml(filepath=graph_file)
        remove_bad_speed_edges(graph)
        records = json.loads(schools_file.read_text(encoding="utf-8"))
        schools = [School(**record) for record in records]
        return Dataset(graph, schools, OSM_SOURCE + " (cached)")

    print("Downloading Surabaya roads, this can take a few minutes...")
    cache_dir.mkdir(parents=True, exist_ok=True)
    graph = ox.graph_from_place(PLACE, network_type="drive", retain_all=True)
    print("Downloading schools...")
    schools = read_schools(ox.features_from_place(PLACE, tags={"amenity": "school"}))
    graph = ox.routing.add_edge_speeds(graph, fallback=30.0)
    remove_bad_speed_edges(graph)
    graph = ox.routing.add_edge_travel_times(graph)

    ox.save_graphml(graph, filepath=graph_file)
    schools_file.write_text(json.dumps([asdict(s) for s in schools], indent=2, ensure_ascii=False),
                            encoding="utf-8")
    return Dataset(graph, schools, OSM_SOURCE + " (downloaded)")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Download or check the OSM cache for Task 1.")
    parser.add_argument("--download", action="store_true", help="download if the cache is missing")
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    args = parser.parse_args(argv)
    try:
        dataset = load_osm(args.cache_dir, download=args.download)
    except (OSError, ValueError, ImportError) as error:
        print(f"Error: {error}")
        return 1
    print(f"Source: {dataset.source}")
    print(f"Nodes: {dataset.graph.number_of_nodes()}, edges: {dataset.graph.number_of_edges()}, "
          f"schools: {len(dataset.schools)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
