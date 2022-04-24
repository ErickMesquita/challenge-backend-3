from application.models import db, User, login_manager, bcrypt
from secrets import randbelow
from hashlib import sha512
from flask_bcrypt import check_password_hash


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


	user = User(username=username,
				password=hash_password(password),
				email=email,
				active=True)

	print(user)

	db.session.add(user)
	try:
		db.session.commit()
	except Exception as e:
		print(e)
		return False, ""

	return True, password


def hash_password(password: str) -> str:
	sha512hash = sha512(password.encode("utf-8")).digest()  # Bytes
	sha512hash_nilsafe = sha512hash.replace(b"\x00", b"\x45")  # Bytes # Avoid bcrypt ValueError
	enc_password = bcrypt.generate_password_hash(sha512hash_nilsafe)  # Bytes
	enc_password_str = str(enc_password, encoding="utf8")
	return enc_password_str


def check_password_hash(user_password_hash: str, candidate_password: str) -> bool:
	candidate_sha512 = sha512(candidate_password.encode("utf-8")).digest()  # Bytes
	candidate_sha512_safe = candidate_sha512.replace(b"\x00", b"\x45")  # Bytes # Avoid bcrypt ValueError

	return check_password_hash(user_password_hash, candidate_sha512_safe)
