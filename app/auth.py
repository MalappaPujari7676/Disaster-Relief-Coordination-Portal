import functools

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint("auth", __name__)


@bp.before_app_request
def load_user():
    uid = session.get("user_id")
    g.user = (
        get_db().execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        if uid else None
    )


def login_required(view):
    @functools.wraps(view)
    def wrapped(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login", next=request.path))
        return view(**kwargs)
    return wrapped


def roles_required(*roles):
    def decorator(view):
        @functools.wraps(view)
        def wrapped(**kwargs):
            if g.user is None:
                return redirect(url_for("auth.login", next=request.path))
            if g.user["role"] not in roles:
                flash("You do not have permission to do that.", "error")
                return redirect(url_for("main.dashboard"))
            return view(**kwargs)
        return wrapped
    return decorator


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        role = request.form.get("role", "citizen")
        if role not in ("citizen", "volunteer"):
            role = "citizen"
        error = None
        if not name or not email or len(password) < 6:
            error = "Name, email and a password of 6+ characters are required."
        if error is None:
            db = get_db()
            try:
                cur = db.execute(
                    "INSERT INTO users (name, email, password_hash, role, phone) VALUES (?,?,?,?,?)",
                    (name, email, generate_password_hash(password), role,
                     request.form.get("phone", "").strip()),
                )
                if role == "volunteer":
                    db.execute(
                        "INSERT INTO volunteers (user_id, skills, location) VALUES (?,?,?)",
                        (cur.lastrowid, request.form.get("skills", "").strip(),
                         request.form.get("location", "").strip()),
                    )
                db.commit()
            except db.IntegrityError:
                error = "That email is already registered."
            else:
                flash("Account created. Please log in.", "success")
                return redirect(url_for("auth.login"))
        flash(error, "error")
    return render_template("register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        user = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user is None or not check_password_hash(user["password_hash"], request.form["password"]):
            flash("Invalid email or password.", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            nxt = request.args.get("next", "")
            return redirect(nxt if nxt.startswith("/") and not nxt.startswith("//")
                            else url_for("main.dashboard"))
    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.index"))
