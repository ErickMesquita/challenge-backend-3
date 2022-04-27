import pytest
from application.controller import user_utils as u_utils
from application.models.user import User
from application.models import db
from application.tests.pytest_fixtures import app, logged_in_client


@pytest.fixture
def user():
	users_list = u_utils.get_users_list()
	if not users_list:
		pytest.fail(msg="No users on database")

	return users_list[0]


@pytest.fixture
def new_username():
	new_username_base = "test{}"
	number = 1
	n_username = new_username_base.format(number)
	while len(u_utils.list_matching_users(username=n_username)) > 0:
		number += 1
		n_username = new_username_base.format(number)

	return n_username


@pytest.fixture
def new_email():
	new_email_base = "test{}@example.com"
	number = 1
	n_email = new_email_base.format(number)
	while len(u_utils.list_matching_users(email=n_email)) > 0:
		number += 1
		n_email = new_email_base.format(number)

	return n_email


@pytest.mark.parametrize(('username', 'email', 'message'), (
		('', '', "Digite um nome de usuário"),
		('a', '', "Digite um email"),
		('a', 'not-an-email', "Email inválido"),
))
def test_create_user_with_malformed_credentials(logged_in_client, username, email, message):
	response = logged_in_client.post(
		'/users',
		data={'username': username, 'email': email},
		follow_redirects=True
	)
	response_html = response.data.decode(encoding="utf8")
	# print(response_html)

	assert message in response_html


def test_create_new_user_with_credentials_ok(logged_in_client, new_username, new_email):
	"""
	GIVEN NEW credentials that are not in the DataBase
	WHEN Create new user account
	THEN User account is created and password returned
	"""

	response = logged_in_client.post(
		'/users',
		data={'username': new_username, 'email': new_email},
		follow_redirects=True
	)
	response_html = response.data.decode(encoding="utf8")
	assert "Erro: " not in response_html
	assert "Senha: " in response_html
	assert response.status_code == 200
	assert "<td>"+new_username+"</td>" in response_html
	assert "<td>"+new_email+"</td>" in response_html


def test_change_user_email(logged_in_client, user, new_email):
	old_username = user.username
	old_email = user.email
	old_login_id = user.login_id
	old_id = user.id

	response = logged_in_client.post(
		'/users/'+str(user.id),
		follow_redirects=True,
		data={'username': old_username, 'email': new_email}
	)

	response_html = response.data.decode(encoding="utf8")
	assert "<td>"+old_username+"</td>" in response_html
	assert "<td>"+old_email+"</td>" not in response_html
	assert "<td>"+new_email+"</td>" in response_html
	assert "Erro: " not in response_html
	assert response.status_code == 200

	db.session.add(user)
	db.session.commit()

	assert user.email == new_email
	assert user.email != old_email
	assert user.id == old_id
	assert user.login_id == old_login_id


def test_change_username_with_new_username(logged_in_client, user, new_username):
	"""
	GIVEN new_username NOT in the Database
	WHEN Change username
	THEN Change Username ONLY. Keep id, login_id, password, etc
	"""
	print(f"new_username={new_username}")
	print(f"type(new_username)={type(new_username)}")
	old_username = user.username
	old_email = user.email
	old_login_id = user.login_id
	old_id = user.id

	response = logged_in_client.post(
		'/users/'+str(user.id),
		follow_redirects=True,
		data={'username': new_username, 'email': old_email}
	)

	response_html = response.data.decode(encoding="utf8")
	assert "<td>"+new_username+"</td>" in response_html
	assert "<td>"+old_username+"</td>" not in response_html
	assert "<td>"+old_email+"</td>" in response_html
	assert "Erro: " not in response_html
	assert response.status_code == 200

	db.session.add(user)
	db.session.commit()

	assert user.username == new_username
	assert user.username != old_username
	assert user.id == old_id
	assert user.login_id == old_login_id


def test_deactivate_user_account(logged_in_client, user):
	"""
		GIVEN user in the Database
		WHEN Remove its account
		THEN user.active will turn False, won't appear anymore in /users
		"""
	old_active = user.active

	response = logged_in_client.delete(
		'/users/' + str(user.id),
		follow_redirects=True
	)

	response_html = response.data.decode(encoding="utf8")
	assert "<td>"+user.username+"</td>" not in response_html
	assert "<td>"+user.email+"</td>" not in response_html
	db.session.add(user)
	db.session.commit()

	assert user.active == False
