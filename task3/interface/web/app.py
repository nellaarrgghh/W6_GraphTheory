"""Flask web application for the Knight's Tour."""

import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from task3.engine.service import solve_knights_tour

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/solve")
def solve():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        result = solve_knights_tour(None, None, None, None)
    else:
        result = solve_knights_tour(
            payload.get("cols"),
            payload.get("rows"),
            payload.get("start_col"),
            payload.get("start_row"),
        )
    return jsonify(result)
