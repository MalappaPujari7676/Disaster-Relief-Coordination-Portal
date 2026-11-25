from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)

from .auth import login_required, roles_required
from .db import get_db

bp = Blueprint("resources", __name__, url_prefix="/resources")
STAFF = ("admin", "coordinator")
CATEGORIES = ["water", "food", "shelter", "medical", "clothing", "fuel", "equipment", "other"]


@bp.route("/")
@login_required
def list_resources():
    rows = get_db().execute(
        "SELECT r.*, i.title AS incident_title FROM resources r "
        "LEFT JOIN incidents i ON i.id = r.incident_id ORDER BY r.category, r.name"
    ).fetchall()
    return render_template("resources.html", resources=rows)


@bp.route("/new", methods=("GET", "POST"))
@roles_required(*STAFF)
def create():
    db = get_db()
    if request.method == "POST":
        try:
            qty = int(request.form.get("quantity", 0))
            threshold = int(request.form.get("low_threshold", 10))
        except ValueError:
            qty = -1
            threshold = 0
        name = request.form["name"].strip()
        if not name or qty < 0 or threshold < 0:
            flash("Name and non-negative numbers are required.", "error")
        else:
            db.execute(
                "INSERT INTO resources (incident_id, name, category, quantity, unit, location, low_threshold) "
                "VALUES (?,?,?,?,?,?,?)",
                (request.form.get("incident_id") or None, name,
                 request.form.get("category", "other"), qty,
                 request.form.get("unit", "units").strip() or "units",
                 request.form.get("location", "").strip(), threshold),
            )
            db.commit()
            flash("Resource added.", "success")
            return redirect(url_for("resources.list_resources"))
    incidents = db.execute("SELECT id, title FROM incidents").fetchall()
    return render_template("resource_form.html", incidents=incidents, categories=CATEGORIES)


@bp.route("/<int:resource_id>/adjust", methods=("POST",))
@roles_required(*STAFF)
def adjust(resource_id):
    delta = request.form.get("delta", type=int)
    if delta is None:
        abort(400)
    db = get_db()
    row = db.execute("SELECT quantity FROM resources WHERE id = ?", (resource_id,)).fetchone()
    if row is None:
        abort(404)
    new_qty = row["quantity"] + delta
    if new_qty < 0:
        flash("Stock cannot go below zero.", "error")
    else:
        db.execute("UPDATE resources SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                   (new_qty, resource_id))
        db.commit()
        flash("Stock updated.", "success")
    return redirect(url_for("resources.list_resources"))
