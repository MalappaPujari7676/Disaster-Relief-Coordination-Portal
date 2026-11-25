# Disaster Relief Coordination Portal

A Flask + SQLite web app that helps coordinators, volunteers and affected people
work together during a disaster.

## Features
- **Public**: live incident overview, stats, and a "Request Help" form (no login needed)
- **Roles**: `admin`, `coordinator`, `volunteer`, `citizen`
- **Incidents**: create, track severity, change status (active / contained / resolved)
- **Help requests**: prioritised by urgency; coordinators assign volunteers; volunteers mark fulfilled
- **Resources**: inventory per incident with low-stock alerts and stock adjustments
- **Volunteers**: skills, area and availability
- **JSON API**: `/api/stats`, `/api/incidents`, `/api/resources`
- CSRF protection, hashed passwords, parameterised SQL

## Run
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python seed.py          # optional demo data
python run.py           # http://127.0.0.1:5000
```
Demo logins (after seeding): `admin@example.com / admin123`, `coord@example.com / coord123`, `vol@example.com / vol123`

## Test
```bash
pytest
```

## Structure
```
app/            Flask package (blueprints: auth, main, incidents, help_requests, resources, volunteers, api)
app/templates/  Jinja templates
app/schema.sql  Database schema
config.py       Settings (set SECRET_KEY and DATABASE via env vars)
seed.py         Demo data
tests/          Pytest suite
```
Set a strong `SECRET_KEY` and use a production WSGI server (e.g. gunicorn) when deploying.
