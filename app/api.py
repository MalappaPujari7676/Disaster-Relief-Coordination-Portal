from flask import Blueprint, jsonify

from .db import get_db
from .main import stats

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/stats")
def api_stats():
    return jsonify(stats())


@bp.route("/incidents")
def api_incidents():
    rows = get_db().execute(
        "SELECT id, title, type, severity, location, status, created_at FROM incidents"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@bp.route("/resources")
def api_resources():
    rows = get_db().execute(
        "SELECT id, name, category, quantity, unit, location FROM resources"
    ).fetchall()
    return jsonify([dict(r) for r in rows])
