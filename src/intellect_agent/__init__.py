# src/intellect_agent/__init__.py
from flask import Flask
from intellect_agent import routes

def create_app():
    """Application factory for the Flask app."""
    app = Flask(__name__)

    # Register the main blueprint
    app.register_blueprint(routes.main)

    return app
