"""Task 1: pick every school inside the radius and find the best delivery route."""

import math

from ..algorithm.held_karp import MAX_LOCATIONS
from .osm_data import haversine_m
from .road_tour import plan_road_tour

MAX_SCHOOLS = MAX_LOCATIONS - 1


def check_inputs(lat, lng, radius_km):
    """Make sure the inputs are real numbers in a valid range."""
    values = []
    for name, value in (("lat", lat), ("lng", lng), ("radius_km", radius_km)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{name} must be a number")
        values.append(float(value))
    lat, lng, radius_km = values
    if not -90 <= lat <= 90:
        raise ValueError("lat must be between -90 and 90")
    if not -180 <= lng <= 180:
        raise ValueError("lng must be between -180 and 180")
    if radius_km < 0:
        raise ValueError("radius_km cannot be negative")
    return lat, lng, radius_km


def schools_in_radius(dataset, lat, lng, radius_km):
    """List of (school, distance_km) for every school inside the circle."""
    found = []
    for school in dataset.schools:
        distance_km = haversine_m(lat, lng, school.latitude, school.longitude) / 1000
        if distance_km <= radius_km:
            found.append((school, distance_km))
    return found


def solve(dataset, lat, lng, radius_km):
    lat, lng, radius_km = check_inputs(lat, lng, radius_km)
    schools = [school for school, _ in schools_in_radius(dataset, lat, lng, radius_km)]
    if len(schools) > MAX_SCHOOLS:
        raise ValueError(f"Found {len(schools)} schools, but Held-Karp can only handle "
                         f"{MAX_SCHOOLS}. Please use a smaller radius.")

    # Even with 0 schools we still run this, so a bad SPPG location gets caught.
    tour = plan_road_tour(dataset, lat, lng, schools)
    route = tour["route"]
    stops = tour["stops"]

    school_order = []
    for order in range(1, len(route) - 1):
        school = stops[route[order]]
        school_order.append({
            "order": order,
            "id": school.osm_id,
            "name": school.name,
            "lat": school.latitude,
            "lng": school.longitude,
        })

    return {
        "status": "success",
        "sppg": {"lat": lat, "lng": lng},
        "radius_km": radius_km,
        "schools_count": len(schools),
        "route": route,
        "school_order": school_order,
        "total_distance_km": tour["total_distance_m"] / 1000,
        "total_time_min": tour["total_travel_seconds"] / 60,
        "solver_time_ms": tour["solver_seconds"] * 1000,
        "polyline": [list(point) for point in tour["coordinates"]],
    }
