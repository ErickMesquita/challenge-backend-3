import os

from application.app import create_app

app = create_app(config_name=os.getenv("FLASK_CONFIG", default="development"))
