from hashlib import sha512
from secrets import randbelow

import pytest
from .pytest_fixtures import app, client
from ..models import bcrypt


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
def test_signup_malformed_credentials(client, username, email, message):
	response = client.post(
		'/users',
		data={'username': username, 'email': email},
		follow_redirects=True
	)
	assert message in response.data.decode(encoding="utf8")


def test_signup_with_credentials_ok(client):
	response = client.post(
		'/users',
		data={'username': "teste", 'email': "teste@exemple.com"},
		follow_redirects=True
	)
	print(response.data.decode(encoding="utf8"))
	assert "Error" not in response.data.decode(encoding="utf8")


def test_hash():
	#password = str(randbelow(1000000)).zfill(6)
	password = "782358"
	print(f"password={password}")
	sha512hash = sha512(password.encode("utf-8")).digest()  # Bytes
	print(f"sha512hash={sha512hash}")
	print(f"len(sha512hash)={len(sha512hash)}")
	print(f"type(sha512hash)={type(sha512hash)}")
	sha512hash_nilsafe = sha512hash.replace(b"\x00", b"\x45")  # Bytes
	print(f"len(sha512hash_nilsafe)={len(sha512hash_nilsafe)}")
	print(f"type(sha512hash_nilsafe)={type(sha512hash_nilsafe)}")
	enc_password = bcrypt.generate_password_hash(sha512hash_nilsafe)  # Bytes
	print(f"len(enc_password)={len(enc_password)}")
	print(f"type(enc_password)={type(enc_password)}")
	enc_password_str = str(enc_password, encoding="utf8")
	print(f"len(enc_password_str)={len(enc_password_str)}")
	print(f"type(enc_password_str)={type(enc_password_str)}")
