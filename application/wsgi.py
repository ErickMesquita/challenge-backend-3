from os import getenv
from application.app import create_app
from application.controller.routes import configure_routes

app = create_app(config_name=getenv("FLASK_CONFIG", default="development"))
configure_routes(app)
