import os
import secrets

from flask import Flask, abort, request, session

from config import Config


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    from . import (api, auth, db, help_requests, incidents, main, resources,
                   volunteers)
    db.init_app(app)
    for module in (auth, main, incidents, help_requests, resources, volunteers, api):
        app.register_blueprint(module.bp)

    if not os.path.exists(app.config["DATABASE"]):
        with app.app_context():
            db.init_db()

    def csrf_token():
        if "_csrf" not in session:
            session["_csrf"] = secrets.token_hex(16)
        return session["_csrf"]

    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def check_csrf():
        if request.method == "POST" and not app.config.get("TESTING"):
            if not request.form.get("_csrf") or request.form["_csrf"] != session.get("_csrf"):
                abort(400, "Invalid CSRF token")

    return app
