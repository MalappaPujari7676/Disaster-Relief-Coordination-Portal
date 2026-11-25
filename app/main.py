from flask import Blueprint, g, render_template

from .auth import login_required
from .db import get_db

bp = Blueprint("main", __name__)


def stats():
    db = get_db()
    one = lambda q: db.execute(q).fetchone()[0]
    return {
        "active_incidents": one("SELECT COUNT(*) FROM incidents WHERE status != 'resolved'"),
        "pending_requests": one("SELECT COUNT(*) FROM help_requests WHERE status = 'pending'"),
        "fulfilled_requests": one("SELECT COUNT(*) FROM help_requests WHERE status = 'fulfilled'"),
        "available_volunteers": one("SELECT COUNT(*) FROM volunteers WHERE available = 1"),
        "low_stock": one("SELECT COUNT(*) FROM resources WHERE quantity <= low_threshold"),
    }


@bp.route("/")
def index():
    incidents = get_db().execute(
        "SELECT * FROM incidents WHERE status != 'resolved' ORDER BY severity DESC, created_at DESC LIMIT 5"
    ).fetchall()
    return render_template("index.html", stats=stats(), incidents=incidents)


@bp.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    urgent = db.execute(
        "SELECT r.*, i.title AS incident_title FROM help_requests r "
        "LEFT JOIN incidents i ON i.id = r.incident_id "
        "WHERE r.status = 'pending' "
        "ORDER BY CASE r.urgency WHEN 'critical' THEN 0 WHEN 'high' THEN 1 "
        "WHEN 'medium' THEN 2 ELSE 3 END, r.created_at LIMIT 10"
    ).fetchall()
    low = db.execute(
        "SELECT * FROM resources WHERE quantity <= low_threshold ORDER BY quantity"
    ).fetchall()
    mine = db.execute(
        "SELECT * FROM help_requests WHERE assigned_to = ? AND status = 'assigned'",
        (g.user["id"],),
    ).fetchall()
    return render_template("dashboard.html", stats=stats(), urgent=urgent, low=low, mine=mine)
