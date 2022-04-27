from abc import ABC, abstractmethod
from typing import Union

from sqlalchemy.exc import IntegrityError

from application.controller.password_utils import generate_password, hash_password

from application.models import db
from application.models.user import User


class UserCreationStrategy(ABC):
	@classmethod
	@abstractmethod
	def execute(cls, username: str, email: str) -> (Union[str, None], Union[str, None]):
		pass


class CreateNewUserStrategy(UserCreationStrategy):
	@classmethod
	def execute(cls, username: str, email: str = None):
		if not email:
			return None, "Email inválido"

		if not username:
			return None, "Username inválido"

		password = generate_password()

		user = User(username=username,
					password=hash_password(password),
					email=email,
					active=True)

		db.session.add(user)
		try:
			db.session.commit()
		except IntegrityError:
			return None, "Erro: O usuário já existe"

		return password, None


class ReactivateUserStrategy(UserCreationStrategy):
	@classmethod
	def execute(cls, username: str, email: str = None):
		if not username:
			return None, "Nome de usuário inválido"

		from application.controller.user_utils import generate_login_id
		from application.controller.user_utils import user_from_db
		user = user_from_db(username=username, active_only=False)

		if not user:
			return None, "Não foi possível reativar a conta"

		if not email:
			email = user.email

		new_password = generate_password()

		user.password = hash_password(new_password)
		user.email = email
		user.active = True
		user.login_id = generate_login_id()

		db.session.add(user)
		try:
			db.session.commit()
		except IntegrityError as e:
			return None, e.__str__()

		return new_password, None


class DontCreateUserStrategy(UserCreationStrategy):
	@classmethod
	def execute(cls, username: str, email: str = None):
		return None, "Erro: Nome de usuário ou email indisponível"