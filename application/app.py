"""
Autor: Leonardo Giordani
Obtido de: https://www.thedigitalcatonline.com/blog/2020/07/05/flask-project-setup-tdd-docker-postgres-and-more-part-1/
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import sys

from manage import configure_app


def create_app(config_name: str) -> Flask:

    app = Flask(__name__)

    configure_app(config_name)
    config_module = f"application.config.{config_name.capitalize()}Config"

    app.config.from_object(config_module)

    if os.environ.get("PGDATABASE") is None:
        print("Error: PG env variables not set!")
        print(f"os.environ.get(\"PGDATABASE\")={os.environ.get('PGDATABASE')}")
        print(f"os.environ.get(\"PGUSER\")={os.environ.get('PGUSER')}")
        print(f"os.environ.get(\"PGPASSWORD\")={os.environ.get('PGPASSWORD')}")
        print(f"os.environ.get(\"PGHOST\")={os.environ.get('PGHOST')}")
        print(f"os.environ.get(\"PGPORT\")={os.environ.get('PGPORT')}")
        sys.exit(9)

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


def create_admin(db: SQLAlchemy):
    from application.controller.user_utils import user_from_db
    if user_from_db("Admin") is not None:
        return

    from application.models.user import User
    admin = User(username="Admin",
                 password="$2b$12$Iqh8RlvTanfs3GAKSwQXy.zXfz5B9rQ7t1cxPTPJGI3MehjWwW2Jq",
                 email="admin@email.com.br",
                 active=True
    )
    db.session.add(admin)
    try:
        db.session.commit()
    except Exception:
        pass

