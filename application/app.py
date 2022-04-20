"""
Autor: Leonardo Giordani
Obtido de: https://www.thedigitalcatonline.com/blog/2020/07/05/flask-project-setup-tdd-docker-postgres-and-more-part-1/
"""

from flask import Flask
from manage import configure_app


def create_app(config_name: str) -> Flask:

    app = Flask(__name__)

    configure_app(config_name)
    config_module = f"application.config.{config_name.capitalize()}Config"

    app.config.from_object(config_module)

    from application.models import db, migrate, login_manager, bcrypt
    db.init_app(app)
    db.app = app
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = "login"
    login_manager.login_message = "Por favor, faça login para continuar"
    login_manager.login_message_category = "warning"

    @app.route("/")
    def hello_world():
        return "Hello, World!"

    return app
