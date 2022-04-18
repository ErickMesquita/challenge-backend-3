import pytest
import os
from application.app import create_app
from application.controller.routes import configure_routes
from application.models import db


@pytest.fixture()
def app():
	app = create_app("testing")
	configure_routes(app)
	db.init_app(app)
	db.app = app
	yield app


@pytest.fixture()
def client(app):
	return app.test_client()


@pytest.fixture()
def resources_path():
	return os.path.join(os.path.dirname(__file__), "resources")


@pytest.fixture
def bank():
	return "BANCO BANCÃO SA"


@pytest.fixture
def branch():
	return "0001"


@pytest.fixture
def account():
	return "00001-1"