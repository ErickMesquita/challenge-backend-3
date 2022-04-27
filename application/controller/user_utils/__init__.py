from collections import namedtuple
from secrets import randbelow
from typing import Union, List, Type

from application.controller.user_utils.user_creation_strategies import UserCreationStrategy, CreateNewUserStrategy, \
	ReactivateUserStrategy, DontCreateUserStrategy
from application.controller.user_utils.user_edit_strategies import UserEditStrategy, SameUsernameStrategy, \
	NewAvailableUsernameStrategy, InactiveUsernameStrategy, DontEditUserStrategy
from application.models.user import User
from application.models import db, login_manager


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


def get_creation_strategy_from_conflicts_list(conflicts_list: List[str]) -> Type[UserCreationStrategy]:

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

	matching_users_list = list_matching_users(username, email)

	conflicts_list = conflicts_list_from_users_list(matching_users_list, username)

	strategy = get_creation_strategy_from_conflicts_list(conflicts_list)

	password, error = strategy.execute(username, email)

	if error:
		return None, error

	return password, None


def edit_user_account(current_user: User, new_username: str = None, new_email: str = None)\
											-> (Union[str, None], Union[str, None]):
	if not current_user:
		return None, "Usuário não encontrado"

	if not new_username and not new_email:
		return "Salvo com sucesso", None

	if not new_username:
		new_username = current_user.username

	if not new_email:
		new_email = current_user.email

	if new_email != current_user.email and not email_available(new_email):
		return None, "Email indisponível"

	matching_users_list = list_matching_users(new_username, new_email)

	if current_user in matching_users_list:
		matching_users_list.remove(current_user)

	conflicts_list = conflicts_list_from_users_list(matching_users_list, new_username)

	strategy = get_edit_strategy_from_conflicting_users_list(conflicts_list, new_username, current_user.username)

	return strategy.execute(current_user, new_username, new_email)


def get_edit_strategy_from_conflicting_users_list(conflicts_list: List[str],
												  new_username: str,
												  current_username: str)\
												-> Type[UserEditStrategy]:
	if current_username == new_username:
		return SameUsernameStrategy

	if "Forbidden" in conflicts_list:
		return DontEditUserStrategy

	if "Reactivate" in conflicts_list:
		return InactiveUsernameStrategy

	return NewAvailableUsernameStrategy


def email_available(new_email: str) -> bool:
	conflicting_users_list = list_matching_users(email=new_email, active=True)

	if len(conflicting_users_list) > 0:
		return False

	return True


def get_users_list(include_admin: bool = False, active: bool = True) -> list:
	query = db.select(User)

	if not include_admin:
		query = query.where(User.username != "Admin")

	if active is not None:
		query = query.where(User.active == active)

	return db.session.scalars(query).all()


def generate_login_id():
	"""
	Returns a randomly generated login_id, unique in the database
	"""
	new_login_id = randbelow(1000000)
	while db.session.scalars(db.select(User).where(User.login_id == new_login_id)).first() is not None:
		new_login_id = randbelow(1000000)
	return new_login_id
