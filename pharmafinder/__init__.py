
"""Main Flask application."""

import os

from flask import Flask, send_from_directory

from . import db
from .config import Config
from .errors import register_error_handlers


# Find the frontend folder
PUBLIC_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "public")
)


# Create the Flask application
def create_app(overrides=None):

    app = Flask(__name__, static_folder=None)

    # Load application settings
    app.config.from_object(Config)

    if overrides:
        app.config.update(overrides)

    # Connect the database
    db.init_app(app)

    # Set up error handling
    register_error_handlers(app)

    # Register all API routes
    from .routes import auth, doctor, patient, pharmacy, search, admin

    app.register_blueprint(auth.bp)
    app.register_blueprint(doctor.bp)
    app.register_blueprint(patient.bp)
    app.register_blueprint(pharmacy.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(admin.bp)

    # Check whether the database is working
    @app.get("/api/health")
    def health():
        db.query_one("SELECT 1")
        return {"status": "ok"}

    # Add security headers to responses
    @app.after_request
    def add_security_headers(response):

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"

        if response.mimetype == "application/json":
            response.headers["Cache-Control"] = "no-store"

        return response

    # Display the frontend homepage
    @app.get("/")
    def homepage():
        return send_from_directory(PUBLIC_DIR, "index.html")

    # Serve CSS, JavaScript and image files
    @app.get("/<path:path>")
    def frontend_files(path):
        return send_from_directory(PUBLIC_DIR, path)

    return app
