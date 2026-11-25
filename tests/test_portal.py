from werkzeug.security import generate_password_hash

from app.db import get_db


def make_user(app, email, role, pw="secret123"):
    with app.app_context():
        db = get_db()
        cur = db.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?,?,?,?)",
            (role.title(), email, generate_password_hash(pw), role))
        if role == "volunteer":
            db.execute("INSERT INTO volunteers (user_id) VALUES (?)", (cur.lastrowid,))
        db.commit()
        return cur.lastrowid


def login(client, email, pw="secret123"):
    return client.post("/login", data={"email": email, "password": pw}, follow_redirects=True)


def test_public_pages(client):
    assert client.get("/").status_code == 200
    assert client.get("/requests/new").status_code == 200
    assert client.get("/api/stats").json["active_incidents"] == 0


def test_register_and_login(client):
    r = client.post("/register", data={"name": "Ann", "email": "ann@x.org",
                                       "password": "secret123", "role": "volunteer"},
                    follow_redirects=True)
    assert b"Account created" in r.data
    assert b"Dashboard" in login(client, "ann@x.org").data


def test_dashboard_requires_login(client):
    assert client.get("/dashboard").status_code == 302


def test_incident_permissions(client, app):
    make_user(app, "cit@x.org", "citizen")
    login(client, "cit@x.org")
    r = client.post("/incidents/new", data={"title": "T", "location": "L", "severity": 3})
    assert r.status_code == 302  # redirected away, not created
    with app.app_context():
        assert get_db().execute("SELECT COUNT(*) FROM incidents").fetchone()[0] == 0


def test_full_flow(client, app):
    make_user(app, "co@x.org", "coordinator")
    vid = make_user(app, "vo@x.org", "volunteer")
    login(client, "co@x.org")
    client.post("/incidents/new", data={"title": "Flood", "type": "flood",
                                        "severity": 4, "location": "Town"})
    client.post("/requests/new", data={"requester_name": "Bob", "contact": "555",
                                       "need_type": "water", "urgency": "high",
                                       "incident_id": 1})
    client.post("/requests/1/assign", data={"volunteer_id": vid})
    with app.app_context():
        row = get_db().execute("SELECT * FROM help_requests WHERE id = 1").fetchone()
        assert row["status"] == "assigned" and row["assigned_to"] == vid
    client.post("/resources/new", data={"name": "Water", "category": "water",
                                        "quantity": 5, "low_threshold": 10})
    client.post("/resources/1/adjust", data={"delta": -10})  # would go negative
    with app.app_context():
        assert get_db().execute("SELECT quantity FROM resources").fetchone()[0] == 5
    assert client.get("/api/resources").json[0]["name"] == "Water"
