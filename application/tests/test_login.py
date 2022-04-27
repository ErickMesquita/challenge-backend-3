import pytest

from application.controller.user_utils import user_from_db
from application.tests.pytest_fixtures import app, client, logged_in_client
from application.controller.password_utils import hash_password, check_password_hash
from application.models.user import User
from application.controller import user_utils as u_utils


def test_response_200_when_access_loginpage(client):
	response = client.get("/login")
	assert response.status_code == 200
	assert b'<form method="post"' in response.data


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', "Digite seu nome de usuário ou email"),
    ('a', '', "Digite sua senha"),
    ('test', '12345', "A senha deve ter 6 caracteres"),
))
def test_login_malformed_credentials(client, username, password, message):
	response = client.post(
		'/login',
		data={'username': username, 'password': password}
	)
	assert message in response.data.decode(encoding="utf8")


@pytest.mark.parametrize(('username', 'email', 'message'), (
		('', '', "Digite um nome de usuário"),
		('a', '', "Digite um email"),
		('a', 'not-an-email', "Email inválido"),
))
def test_signup_malformed_credentials(logged_in_client, username, email, message):
	response = logged_in_client.post(
		'/users',
		data={'username': username, 'email': email},
		follow_redirects=True
	)
	response_html = response.data.decode(encoding="utf8")
	#print(response_html)

	assert message in response_html


def test_signup_with_new_credentials_ok(logged_in_client):
	response = logged_in_client.post(
		'/users',
		data={'username': "teste", 'email': "teste@exemple.com"},
		follow_redirects=True
	)
	#print(response.data.decode(encoding="utf8"))
	assert "Error" not in response.data.decode(encoding="utf8")


def test_hash_creation_and_checking():
	"""
	"782358" generates a SHA512 hash with a NIL byte, which breaks Bcrypt
	"""
	correct_password = "782358"
	wrong_password = "wrong_password"

	hashed = hash_password(correct_password)

	assert check_password_hash(hashed, correct_password)
	assert not check_password_hash(hashed, wrong_password)


def test_user_from_db_admin(app):
	user_admin = user_from_db(username_or_email="Admin")

	assert user_admin.email == "admin@email.com.br"


def test_user_edit_page(app):
	user = u_utils.load_user_from_id(user_id=1)
	with app.test_client(user=user) as client:
		# this request has user 1 already logged in!

		response = client.get(
			'/users/2',
			follow_redirects=True
		)
	print(response.data.decode(encoding="utf8"))


def test_admin_creation_and_checking():
	"""
	"123999" generates a SHA512 hash with a NIL byte, which breaks Bcrypt
	"""
	correct_password = "123999"
	wrong_password = "wrong_password"

	hashed = hash_password(correct_password)
	print(hashed)

	assert check_password_hash(hashed, correct_password)
	assert not check_password_hash(hashed, wrong_password)
