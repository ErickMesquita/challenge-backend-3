"""
Autor: Leonardo Giordani
Obtido de: https://www.thedigitalcatonline.com/blog/2020/07/05/flask-project-setup-tdd-docker-postgres-and-more-part-1/
"""

from flask import Flask


def create_app(config_name: str) -> Flask:

    app = Flask(__name__)

    config_module = f"application.config.{config_name.capitalize()}Config"

    app.config.from_object(config_module)

    from application.models import db, migrate
    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/")
    def hello_world():
        return "Hello, World!"

    return app
