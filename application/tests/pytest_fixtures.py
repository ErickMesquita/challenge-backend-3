import pandas as pd
import pytest
from datetime import datetime
from decimal import Decimal
import os

from flask_login import FlaskLoginClient

from application.app import create_app
from application.controller.routes import configure_routes
from application.models import db, login_manager
from application.controller.user_utils import load_user_from_id


@pytest.fixture
def app():
	app = create_app("testing")
	configure_routes(app)
	db.init_app(app)
	login_manager.init_app(app)
	app.test_client_class = FlaskLoginClient
	db.app = app
	yield app


@pytest.fixture
def client(app):
	return app.test_client()


@pytest.fixture
def logged_in_client(app):
	user = load_user_from_id(user_id=1)
	with app.test_client(user=user) as client:
		yield client


@pytest.fixture
def resources_path():
	return os.path.join(os.path.dirname(__file__), "resources")


@pytest.fixture
def uploads_path():
	return os.path.join(os.path.dirname(__file__), "uploads_mock")


@pytest.fixture
def bank():
	return "BANCO BANCÃO SA"


@pytest.fixture
def branch():
	return "0001"


@pytest.fixture
def account():
	return "00001-1"


@pytest.fixture
def bank2():
	return "BANCO EXEMPLO SA"


@pytest.fixture
def branch2():
	return "0002"


@pytest.fixture
def account2():
	return "00002-4"


@pytest.fixture
def columns_names_list():
	return ["Banco origem",
		  "Agência origem",
		  "Conta origem",
		  "Banco destino",
		  "Agência destino",
		  "Conta destino",
		  "Valor",
		  "Data e hora"]


@pytest.fixture
def transactions_df(columns_names_list,
					bank, branch, account,
					bank2, branch2, account2,):

	return pd.DataFrame([(bank, branch, account,
						bank2, branch2, account2,
						Decimal(1000),
						datetime(2022, 4, 11, 12, 30, 0)),
					   (bank2, branch2, account2,
						bank, branch, account,
						Decimal(1000),
						datetime(2022, 4, 11, 13, 30, 0))],
					  columns=columns_names_list)

