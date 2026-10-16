"""
app.py - Flask Web Application for Task 1: SPPG Mealbox TSP Delivery Simulator
Provides interactive map endpoints to pick SPPG location, set delivery radius,
and compute Hamiltonian cycle TSP routes on the Surabaya road Digraph.
"""

import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from task1_tsp.router import RoadDigraph, haversine
from task1_tsp.tsp_solver import TSPSolver

app = Flask(__name__)

# Initialize router and solver
DATA_DIR = Path(__file__).resolve().parent / "data"
with open(DATA_DIR / "surabaya_schools.json", "r", encoding="utf-8") as f:
    ALL_SCHOOLS = json.load(f)

router = RoadDigraph()
solver = TSPSolver(router)

@app.route("/")
def index():
    """Serves the interactive SPPG simulator UI."""
    return render_template("index.html")

@app.route("/api/schools", methods=["GET"])
def get_schools():
    """Returns schools within radius of given center."""
    try:
        lat = float(request.args.get("lat", -7.2825))
        lon = float(request.args.get("lon", 112.7944))
        radius_km = float(request.args.get("radius", 2.5))
        radius_m = radius_km * 1000.0

        filtered = []
        for s in ALL_SCHOOLS:
            d = haversine(lat, lon, s["lat"], s["lon"])
            if d <= radius_m:
                s_copy = dict(s)
                s_copy["distance_from_sppg_km"] = round(d / 1000.0, 2)
                filtered.append(s_copy)

        return jsonify({
            "status": "success",
            "center": {"lat": lat, "lon": lon},
            "radius_km": radius_km,
            "count": len(filtered),
            "schools": filtered
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/solve_tsp", methods=["POST"])
def solve_tsp():
    """Solves TSP for schools within radius of SPPG location."""
    try:
        data = request.get_json() or {}
        lat = float(data.get("lat", -7.2825))
        lon = float(data.get("lon", 112.7944))
        radius_km = float(data.get("radius", 2.5))
        algo = data.get("algorithm", "auto")
        prefer_osrm = bool(data.get("prefer_osrm", False))

        radius_m = radius_km * 1000.0
        nearby_schools = [
            s for s in ALL_SCHOOLS
            if haversine(lat, lon, s["lat"], s["lon"]) <= radius_m
        ]

        result = solver.solve_sppg_delivery(
            sppg_coord=(lat, lon),
            schools=nearby_schools,
            algorithm=algo,
            prefer_osrm=prefer_osrm
        )

        return jsonify({
            "status": "success",
            "sppg": {"lat": lat, "lon": lon},
            "radius_km": radius_km,
            "schools_count": len(nearby_schools),
            "result": result
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
