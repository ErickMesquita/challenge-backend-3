from os import getenv
from application.app import create_app, create_admin
from application.controller.routes import configure_routes
from application import models
from flask_migrate import upgrade, migrate, init, stamp


app = create_app(config_name=getenv("FLASK_CONFIG", default="testing"))
configure_routes(app)

with app.app_context():
	models.db.create_all()


