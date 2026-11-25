from flask import (Blueprint, abort, flash, g, redirect, render_template,
                   request, url_for)

from .auth import roles_required
from .db import get_db

bp = Blueprint("incidents", __name__, url_prefix="/incidents")
STAFF = ("admin", "coordinator")
TYPES = ["flood", "earthquake", "wildfire", "storm", "landslide", "other"]


@bp.route("/")
def list_incidents():
    rows = get_db().execute(
        "SELECT * FROM incidents ORDER BY (status = 'resolved'), severity DESC, created_at DESC"
    ).fetchall()
    return render_template("incidents.html", incidents=rows)


@bp.route("/new", methods=("GET", "POST"))
@roles_required(*STAFF)
def create():
    if request.method == "POST":
        title = request.form["title"].strip()
        location = request.form["location"].strip()
        try:
            severity = int(request.form.get("severity", 1))
        except ValueError:
            severity = 0
        if not title or not location or not 1 <= severity <= 5:
            flash("Title, location and severity (1-5) are required.", "error")
        else:
            db = get_db()
            cur = db.execute(
                "INSERT INTO incidents (title, type, severity, location, description, created_by) "
                "VALUES (?,?,?,?,?,?)",
                (title, request.form.get("type", "other"), severity, location,
                 request.form.get("description", "").strip(), g.user["id"]),
            )
            db.commit()
            flash("Incident created.", "success")
            return redirect(url_for("incidents.detail", incident_id=cur.lastrowid))
    return render_template("incident_form.html", types=TYPES)


@bp.route("/<int:incident_id>")
def detail(incident_id):
    db = get_db()
    incident = db.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    if incident is None:
        abort(404)
    reqs = db.execute(
        "SELECT * FROM help_requests WHERE incident_id = ? ORDER BY created_at DESC", (incident_id,)
    ).fetchall()
    res = db.execute("SELECT * FROM resources WHERE incident_id = ?", (incident_id,)).fetchall()
    return render_template("incident_detail.html", incident=incident, requests=reqs, resources=res)


@bp.route("/<int:incident_id>/status", methods=("POST",))
@roles_required(*STAFF)
def set_status(incident_id):
    status = request.form.get("status")
    if status not in ("active", "contained", "resolved"):
        abort(400)
    db = get_db()
    db.execute("UPDATE incidents SET status = ? WHERE id = ?", (status, incident_id))
    db.commit()
    flash("Incident status updated.", "success")
    return redirect(url_for("incidents.detail", incident_id=incident_id))
