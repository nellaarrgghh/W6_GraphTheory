"""Flask website for the three Graph Theory tasks."""

import os
import sys
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parent
if str(WEB_DIR) not in sys.path:
    sys.path.insert(0, str(WEB_DIR))

from flask import Flask, jsonify, render_template, request

from task1.engine.osm_data import DEFAULT_CACHE_DIR, load_osm
from task1.engine.service import MAX_SCHOOLS, check_inputs, road_overlay, schools_in_radius
from task1.engine.service import solve as solve_task1
from task2.engine.service import solve as solve_task2
from task3.engine.service import solve as solve_task3

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

# The Surabaya road graph is big, so load it once on the first Task 1 request.
# Tests put a small demo dataset here instead.
task1_dataset = None


def get_task1_dataset():
    global task1_dataset
    if task1_dataset is None:
        cache_dir = os.environ.get("TASK1_CACHE_DIR", DEFAULT_CACHE_DIR)
        task1_dataset = load_osm(cache_dir, download=False)
    return task1_dataset


def task1_error(message, status_code=400):
    return jsonify({"status": "error", "message": message}), status_code


@app.get("/")
def home():
    return render_template("home.html")


@app.get("/task1")
def task1():
    return render_template("task1.html")


@app.get("/task2")
def task2():
    return render_template("task2.html")


@app.get("/task3")
def task3():
    return render_template("task3.html")


@app.get("/api/task1/schools")
def task1_schools():
    try:
        lat, lng, radius_km = check_inputs(request.args.get("lat", type=float),
                                           request.args.get("lng", type=float),
                                           request.args.get("radius_km", type=float))
    except ValueError as error:
        return task1_error(str(error))
    try:
        dataset = get_task1_dataset()
    except (OSError, ImportError) as error:
        return task1_error(f"Road data not loaded: {error}", 503)

    schools = schools_in_radius(dataset, lat, lng, radius_km)
    roads, roads_cut = road_overlay(dataset, lat, lng, radius_km)
    return jsonify({
        "status": "success",
        "source": dataset.source,
        "max_schools": MAX_SCHOOLS,
        "schools": [{"id": s.osm_id, "name": s.name, "lat": s.latitude, "lng": s.longitude,
                     "distance_km": distance} for s, distance in schools],
        "roads": roads,
        "roads_cut": roads_cut,
    })


@app.post("/api/task1/solve")
def solve_task1_api():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return task1_error("Send JSON with lat, lng and radius_km.")
    try:
        dataset = get_task1_dataset()
    except (OSError, ImportError) as error:
        return task1_error(f"Road data not loaded: {error}", 503)
    try:
        return jsonify(solve_task1(dataset, payload.get("lat"), payload.get("lng"), payload.get("radius_km")))
    except ValueError as error:
        return task1_error(str(error))


@app.post("/api/task2/solve")
def solve_task2_api():
    payload = request.get_json(silent=True) or {}
    lat = payload.get("lat", -7.2825)
    lng = payload.get("lng", 112.7944)
    radius_km = payload.get("radius_km", 1.5)
    
    return jsonify(solve_task2(lat, lng, radius_km))


@app.post("/api/task3/solve")
def solve_task3_api():
    payload = request.get_json(silent=True) or {}
    return jsonify(solve_task3(
        payload.get("cols"), 
        payload.get("rows"),
        payload.get("start_col"),
        payload.get("start_row")
    ))
