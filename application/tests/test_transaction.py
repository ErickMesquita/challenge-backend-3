import pytest
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


def test_response_200_when_access_transaction_form(client):
	response = client.get("/forms/transaction")
	print(response.text)
	assert response.status_code == 200
	assert b'<form method="post"' in response.data


def test_response_200_when_access_homepage(client):
	response = client.get("/")
	assert response.status_code == 200

