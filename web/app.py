"""Unified Flask interface for the three assignment tasks."""

import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from task2.engine.service import solve as solve_task2
from task3.engine.service import solve as solve_task3

app = Flask(__name__)


@app.get("/")
def home():
    return render_template("home.html")


@app.get("/task2")
def task2():
    return render_template("task2.html")


@app.get("/task3")
def task3():
    return render_template("task3.html")


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
