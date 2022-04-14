import pytest
import os
from application.app import create_app
from application.controller.routes import configure_routes


@pytest.fixture()
def app():
	app = create_app("testing")
	configure_routes(app)
	yield app


@pytest.fixture()
def client(app):
	return app.test_client()


@pytest.fixture()
def resources_path():
	return os.path.join(os.path.dirname(__file__), "resources")