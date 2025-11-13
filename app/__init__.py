# app/__init__.py
from flask import Flask
from . import routes

def create_app():
    """Application factory for the Flask app."""
    app = Flask(__name__)

    # Register the main blueprint
    app.register_blueprint(routes.main)

    return app
