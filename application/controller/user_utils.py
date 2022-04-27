from abc import ABC, abstractmethod
from collections import namedtuple
from secrets import randbelow
from typing import Union, List, Type

from markupsafe import escape

from application.controller.password_utils import generate_password, hash_password
from application.models.user import User
from application.models import db, login_manager

from sqlalchemy.exc import IntegrityError


def user_from_db(username_or_email: Union[str, None] = None, active_only: bool = True, **kwargs):
	if username_or_email is None:
		query = db.select(User).filter_by(**kwargs)
	else:
		query = db.select(User). \
			where(
			db.or_(User.username == username_or_email,
				   User.email == username_or_email)
		)

	if active_only:
		query = query.where(User.active == True)  # This must be "==", not "is"

	return db.session.scalars(query).first()


@login_manager.user_loader
def load_user_from_id(login_id: Union[int, None] = None, user_id: Union[int, None] = None)\
					-> Union[User, None]:

	if login_id is not None:
		query = db.select(User).where(User.login_id == login_id)
	elif user_id is not None:
		query = db.select(User).where(User.id == user_id)
	else:
		return None

	return db.session.scalars(query).first()


def list_matching_users(username: Union[str, None] = None, email: Union[str, None] = None, active: bool = None)\
						-> List[User]:
	"""
	Returns a list of users with matching username OR email
	"""
	if username is None and email is None:
		return list()

	query = db.select(User).where(
		db.or_(User.username == username,
			   User.email == email)
	)

	if active is not None:
		query = query.where(User.active == active)

	return db.session.scalars(query).all()


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

		user = user_from_db(username=username)

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


def get_creation_strategy_from_conflicting_users_list(conflicting_users_list: List[User],
											 new_username: str) -> Type[UserCreationStrategy]:

	conflicts_list = conflicts_list_from_users_list(conflicting_users_list, new_username)

	if "Forbidden" in conflicts_list:
		return DontCreateUserStrategy

	if "Reactivate" in conflicts_list:
		return ReactivateUserStrategy

	return CreateNewUserStrategy


def conflicts_list_from_users_list(conflicting_users_list: List[User],
								   new_username: str)\
								-> List[str]:
	Conflict = namedtuple('Conflict', ['same_username', 'active'])

	strategies = {
		Conflict(same_username=False, active=False): "OK",
		Conflict(same_username=False, active=True): "Forbidden",
		Conflict(same_username=True, active=True): "Forbidden",
		Conflict(same_username=True, active=False): "Reactivate"
	}
	conflicts_list = list()

	for user in conflicting_users_list:
		same_username = user.username == new_username
		c = Conflict(same_username, user.active)
		conflicts_list.append(strategies.get(c))

	return conflicts_list


def create_or_reactivate_user(username: str, email: str) -> (Union[str, None], Union[str, None]):
	if username is None or email is None:
		return None, "Nome de usuário ou email inválidos"

	conflicting_users_list = list_matching_users(username, email)

	strategy = get_creation_strategy_from_conflicting_users_list(conflicting_users_list, username)

	password, error = strategy.execute(username, email)

	if error:
		return None, error

	return password, None


def edit_user_account(user_id: int, new_username: str = None, new_email: str = None)\
											-> (Union[str, None], Union[str, None]):
	if not user_id:
		return None, "Usuário não encontrado"

	if not new_username and not new_email:
		return "Salvo com sucesso", None

	current_user = load_user_from_id(user_id=user_id)

	if not current_user:
		return None, "Usuário não encontrado"

	if not new_username:
		new_username = current_user.username

	if not new_email:
		new_email = current_user.email

	matching_users_list = list_matching_users(new_username, new_email)

	if current_user in matching_users_list:
		matching_users_list.remove(current_user)

	strategy = get_edit_strategy_from_conflicting_users_list(matching_users_list, new_username, current_user.username)

	return strategy.execute(current_user, new_username, new_email)


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

		if not email_available(new_email):
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
		elif not email_available(new_email):
			return None, "Email indisponível"

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

		matching_inactive_accounts = list_matching_users(username=new_username, active=False)

		if len(matching_inactive_accounts) == 0:
			return None, "Nenhuma conta desativada foi encontrada, tente criar uma nova conta"

		new_user = matching_inactive_accounts[0]

		if not new_email:
			new_email = current_user.email
		elif not email_available(new_email):
			return None, "Email indisponível"

		new_user.email = new_email
		new_user.login_id = current_user.login_id
		new_user.password = current_user.password
		new_user.active = True

		current_user.login_id = generate_login_id()
		current_user.active = False


class DontEditUserStrategy(UserEditStrategy):
	@classmethod
	def execute(cls, current_user: User, new_username: str, new_email: str) -> (Union[str, None], Union[str, None]):
		return None, "Nome de usuário já existe"


def get_edit_strategy_from_conflicting_users_list(conflicting_users_list: List[User],
												  new_username: str,
												  current_username: str)\
												-> Type[UserEditStrategy]:
	if current_username == new_username:
		return SameUsernameStrategy

	conflicts_list = conflicts_list_from_users_list(conflicting_users_list, new_username)

	if "Forbidden" in conflicts_list:
		return DontEditUserStrategy

	if "Reactivate" in conflicts_list:
		return InactiveUsernameStrategy

	# TODO: Merge this function with get_creation_strategy_from_conflicting_users_list

	return NewAvailableUsernameStrategy


def email_available(new_email: str) -> bool:
	conflicting_users_list = list_matching_users(email=new_email, active=True)

	if len(conflicting_users_list) > 0:
		return False

	return True


def get_users_list(include_admin: bool = False) -> list:
	query = db.select(User)

	if not include_admin:
		query = query.where(User.username != "Admin")

	return db.session.scalars(query).all()


def generate_login_id():
	"""
	Returns a randomly generated login_id, unique in the database
	"""
	new_login_id = randbelow(1000000)
	while db.session.scalars(db.select(User).where(User.login_id == new_login_id)).first() is not None:
		new_login_id = randbelow(1000000)
	return new_login_id
