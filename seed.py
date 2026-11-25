"""Populate the database with demo data:  python seed.py"""
from werkzeug.security import generate_password_hash

from app import create_app
from app.db import get_db, init_db

app = create_app()

with app.app_context():
    init_db()
    db = get_db()
    users = [
        ("Admin", "admin@example.com", "admin123", "admin"),
        ("Casey Coordinator", "coord@example.com", "coord123", "coordinator"),
        ("Vic Volunteer", "vol@example.com", "vol123", "volunteer"),
    ]
    for name, email, pw, role in users:
        cur = db.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?,?,?,?)",
            (name, email, generate_password_hash(pw), role),
        )
        if role == "volunteer":
            db.execute(
                "INSERT INTO volunteers (user_id, skills, location) VALUES (?,?,?)",
                (cur.lastrowid, "First aid, driving", "Riverside"),
            )
    db.execute(
        "INSERT INTO incidents (title, type, severity, location, description, created_by) "
        "VALUES ('Riverside Flood', 'flood', 4, 'Riverside District', "
        "'River overflow, 300 households affected.', 2)"
    )
    db.execute(
        "INSERT INTO help_requests (incident_id, requester_name, contact, need_type, description, urgency) "
        "VALUES (1, 'Maria Lopez', '555-0101', 'water', 'Family of 5 without clean water.', 'high')"
    )
    db.execute(
        "INSERT INTO resources (incident_id, name, category, quantity, unit, location, low_threshold) "
        "VALUES (1, 'Bottled water', 'water', 120, 'cases', 'Central Depot', 50)"
    )
    db.execute(
        "INSERT INTO resources (incident_id, name, category, quantity, unit, location, low_threshold) "
        "VALUES (1, 'Blankets', 'shelter', 8, 'pcs', 'Central Depot', 20)"
    )
    db.commit()
    print("Seeded. Logins: admin@example.com/admin123, coord@example.com/coord123, vol@example.com/vol123")
