from abc import ABC, abstractmethod
from typing import Union

from markupsafe import escape
from sqlalchemy.exc import IntegrityError

from application.controller import user_utils as u_utils
from application.models import db
from application.models.user import User


class UserEditStrategy(ABC):
	@classmethod
	@abstractmethod
	def execute(cls, current_user: User, new_username: str, new_email: str) -> (Union[str, None], Union[str, None]):
		pass


class SameUsernameStrategy(UserEditStrategy):
	@classmethod
	def execute(cls, current_user: User, new_username: str, new_email: str) -> (Union[str, None], Union[str, None]):
		if not current_user:
			return None, "Usuário não encontrado"

		if not new_email or new_email == current_user.email:
			return "Salvo com sucesso", None

		if not u_utils.email_available(new_email):
			return None, "Email indisponível"

		current_user.email = new_email
		db.session.add(current_user)
		try:
			db.session.commit()
		except IntegrityError as e:
			return None, e.__str__()

		return "Email atualizado com sucesso", None


class NewAvailableUsernameStrategy(UserEditStrategy):
	@classmethod
	def execute(cls, current_user: User, new_username: str, new_email: str) -> (Union[str, None], Union[str, None]):
		if not current_user:
			return None, "Usuário não encontrado"

		if not new_email:
			new_email = current_user.email

		current_user.username = new_username
		current_user.email = new_email

		db.session.add(current_user)
		try:
			db.session.commit()
		except IntegrityError as e:
			return None, e.__str__()

		return f"Usuário {escape(new_username)} atualizado com sucesso", None


class InactiveUsernameStrategy(UserEditStrategy):
	@classmethod
	def execute(cls, current_user: User, new_username: str, new_email: str) -> (Union[str, None], Union[str, None]):
		if not current_user:
			return None, "Usuário não encontrado"

		matching_inactive_accounts = u_utils.list_matching_users(username=new_username, active=False)

		if len(matching_inactive_accounts) == 0:
			return None, "Nenhuma conta desativada foi encontrada, tente criar uma nova conta"

		new_user = matching_inactive_accounts[0]

		new_user.email = new_email
		new_user.login_id = current_user.login_id
		new_user.password = current_user.password
		new_user.active = True

		current_user.login_id = u_utils.generate_login_id()
		current_user.active = False


class DontEditUserStrategy(UserEditStrategy):
	@classmethod
	def execute(cls, current_user: User, new_username: str, new_email: str) -> (Union[str, None], Union[str, None]):
		return None, "Nome de usuário já existe"