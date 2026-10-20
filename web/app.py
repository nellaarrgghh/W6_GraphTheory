"""Unified Flask interface for the three assignment tasks."""

import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from task3.engine.service import solve

app = Flask(__name__)


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


@app.post("/api/task1/solve")
def solve_task1():
    return jsonify({"status": "not_implemented"})


@app.post("/api/task2/solve")
def solve_task2():
    return jsonify({"status": "not_implemented"})


@app.post("/api/task3/solve")
def solve_task3():
    body = request.get_json(silent=True) or {}
    return jsonify(
        solve(
            body.get("cols"),
            body.get("rows"),
            body.get("start_col"),
            body.get("start_row"),
        )
    ), 200
