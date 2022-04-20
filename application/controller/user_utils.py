from application.models import db, User, login_manager, bcrypt
from secrets import randbelow


def user_from_db(username_or_email=None, **kwargs):
	if username_or_email is None:
		query = db.select(User).filter_by(**kwargs)
	else:
		query = db.select(User).\
			where(
				db.or_(User.username == username_or_email,
					   User.email == username_or_email)
			)

	return db.session.scalars(query).first()


@login_manager.user_loader
def load_user(user_id):
	query = db.select(User).where(User.login_id == user_id)
	return db.session.scalars(query).first()


def create_new_user(username: str, email: str) -> (bool, str):
	if username is None or email is None:
		return False, "Nome de usuário ou email inválidos"

	password = str(randbelow(1000000)).zfill(6)
	enc_password = bcrypt.generate_password_hash(password)

	user = User(username=username,
				password=enc_password,
				email=email,
				active=True)

	db.session.add(user)
	db.session.commit()

	return True, password
