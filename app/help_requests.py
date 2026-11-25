from flask import (Blueprint, abort, flash, g, redirect, render_template,
                   request, url_for)

from .auth import login_required, roles_required
from .db import get_db

bp = Blueprint("requests", __name__, url_prefix="/requests")
STAFF = ("admin", "coordinator")
NEEDS = ["water", "food", "shelter", "medical", "rescue", "transport", "other"]
URGENCIES = ["low", "medium", "high", "critical"]


@bp.route("/")
@login_required
def list_requests():
    status = request.args.get("status")
    sql = ("SELECT r.*, u.name AS volunteer_name FROM help_requests r "
           "LEFT JOIN users u ON u.id = r.assigned_to")
    args = ()
    if status in ("pending", "assigned", "fulfilled", "cancelled"):
        sql += " WHERE r.status = ?"
        args = (status,)
    sql += (" ORDER BY CASE r.urgency WHEN 'critical' THEN 0 WHEN 'high' THEN 1 "
            "WHEN 'medium' THEN 2 ELSE 3 END, r.created_at DESC")
    db = get_db()
    volunteers = db.execute(
        "SELECT u.id, u.name FROM users u JOIN volunteers v ON v.user_id = u.id WHERE v.available = 1"
    ).fetchall()
    return render_template("requests.html", requests=db.execute(sql, args).fetchall(),
                           volunteers=volunteers, status=status)


@bp.route("/new", methods=("GET", "POST"))
def create():
    """Public form: anyone affected by a disaster can ask for help."""
    db = get_db()
    if request.method == "POST":
        name = request.form["requester_name"].strip()
        contact = request.form["contact"].strip()
        need = request.form.get("need_type", "other")
        urgency = request.form.get("urgency", "medium")
        if not name or not contact:
            flash("Name and contact details are required.", "error")
        elif urgency not in URGENCIES or need not in NEEDS:
            abort(400)
        else:
            incident_id = request.form.get("incident_id") or None
            db.execute(
                "INSERT INTO help_requests (incident_id, requester_name, contact, need_type, description, urgency) "
                "VALUES (?,?,?,?,?,?)",
                (incident_id, name, contact, need, request.form.get("description", "").strip(), urgency),
            )
            db.commit()
            flash("Your request has been submitted. Help is being coordinated.", "success")
            return redirect(url_for("main.index"))
    incidents = db.execute("SELECT id, title FROM incidents WHERE status != 'resolved'").fetchall()
    return render_template("request_form.html", incidents=incidents, needs=NEEDS, urgencies=URGENCIES)


@bp.route("/<int:request_id>/assign", methods=("POST",))
@roles_required(*STAFF)
def assign(request_id):
    volunteer_id = request.form.get("volunteer_id", type=int)
    db = get_db()
    if not db.execute("SELECT 1 FROM volunteers WHERE user_id = ?", (volunteer_id,)).fetchone():
        flash("Choose a valid volunteer.", "error")
    else:
        db.execute("UPDATE help_requests SET assigned_to = ?, status = 'assigned' WHERE id = ?",
                   (volunteer_id, request_id))
        db.commit()
        flash("Volunteer assigned.", "success")
    return redirect(url_for("requests.list_requests"))


@bp.route("/<int:request_id>/status", methods=("POST",))
@login_required
def set_status(request_id):
    status = request.form.get("status")
    if status not in ("pending", "assigned", "fulfilled", "cancelled"):
        abort(400)
    db = get_db()
    row = db.execute("SELECT * FROM help_requests WHERE id = ?", (request_id,)).fetchone()
    if row is None:
        abort(404)
    if g.user["role"] not in STAFF and row["assigned_to"] != g.user["id"]:
        abort(403)
    db.execute("UPDATE help_requests SET status = ? WHERE id = ?", (status, request_id))
    db.commit()
    flash("Request updated.", "success")
    return redirect(request.referrer or url_for("requests.list_requests"))
