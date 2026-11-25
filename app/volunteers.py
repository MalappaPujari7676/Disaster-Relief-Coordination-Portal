from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from .auth import login_required, roles_required
from .db import get_db

bp = Blueprint("volunteers", __name__, url_prefix="/volunteers")


@bp.route("/")
@roles_required("admin", "coordinator")
def list_volunteers():
    rows = get_db().execute(
        "SELECT u.name, u.email, u.phone, v.* FROM volunteers v JOIN users u ON u.id = v.user_id "
        "ORDER BY v.available DESC, u.name"
    ).fetchall()
    return render_template("volunteers.html", volunteers=rows)


@bp.route("/profile", methods=("GET", "POST"))
@login_required
def profile():
    db = get_db()
    vol = db.execute("SELECT * FROM volunteers WHERE user_id = ?", (g.user["id"],)).fetchone()
    if vol is None:
        flash("Only registered volunteers have a volunteer profile.", "error")
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        db.execute(
            "UPDATE volunteers SET skills = ?, location = ?, available = ? WHERE user_id = ?",
            (request.form.get("skills", "").strip(), request.form.get("location", "").strip(),
             1 if request.form.get("available") else 0, g.user["id"]),
        )
        db.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("volunteers.profile"))
    return render_template("volunteer_profile.html", vol=vol)
