from flask_login import UserMixin
from application.models import db, login_manager, bcrypt
from hashlib import sha512
from secrets import randbelow
from flask_bcrypt import check_password_hash as bcrypt_check_password_hash


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), nullable=False, unique=True)
	password = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), nullable=False)
	login_id = db.Column(db.Integer, db.Identity(start=5000, increment=1, cycle=True), nullable=False, unique=True)
	active = db.Column(db.Boolean, db.ColumnDefault(True), nullable=False)

	__table_args__ = (db.CheckConstraint("login_id <> id",
										  name="id_and_login_id_are_different"),)

	def __repr__(self):
		return f"<User {self.username}>"

	def get_id(self):
		if self.login_id is not None:
			return str(self.login_id)
		query = db.select(User.login_id).filter_by(id=self.id)
		return db.session.scalars(query).first()

	def deactivate_account(self):
		self.active = False
		db.session.add(self)
		db.session.commit()

	@staticmethod
	def user_from_db(username_or_email=None, **kwargs):
		if username_or_email is None:
			query = db.select(User).filter_by(**kwargs)
		else:
			query = db.select(User). \
				where(
				db.or_(User.username == username_or_email,
					   User.email == username_or_email)
			).where(User.active == True)  # This must be "==", not "is"
		return db.session.scalars(query).first()

	@staticmethod
	@login_manager.user_loader
	def load_user(login_id: int = None, user_id: int = None):
		if login_id is not None:
			query = db.select(User).where(User.login_id == login_id)
		elif user_id is not None:
			query = db.select(User).where(User.id == user_id)
		else:
			return None

		return db.session.scalars(query).first()

	@staticmethod
	def check_existing_users(username: str, email: str) -> list:
		"""
		Returns True if
		"""
		if username is None and email is None:
			return ["OK"]

		query = db.select(User).where(
			db.or_(User.username == username,
				   User.email == email)
		)

		result = db.session.execute(query)

		strategies = {
			# active, user, email
			(False, False, False): "OK",
			(False, False, True): "OK",
			(False, True, False): "Reactivate",
			(False, True, True): "Reactivate",
			(True, False, False): "OK",
			(True, False, True): "Error",
			(True, True, False): "Error",
			(True, True, True): "Error"
		}

		result_list = list()
		for user in result.scalars().all():
			same_user = user.username == username
			same_email = user.email == email
			result_list.append(strategies.get((user.active, same_user, same_email)))

		return result_list

	@classmethod
	def reactivate_account(cls, username: str) -> (bool, str):
		if username is None or username == "":
			return False, "Nome de usuário inválido"

		query = db.select(User).\
			where(User.username == username).\
			where(User.active is False)

		user = db.session.scalars(query).first()

		if user is None:
			return False, "Não foi possível reativar a conta"

		user.active = True

		password = generate_password()
		user.password = hash_password(password)

		new_login_id = randbelow(1000000)
		while db.session.scalars(db.select(User).where(User.login_id == new_login_id)).first() is not None:
			new_login_id = randbelow(1000000)

		user.login_id = new_login_id

		db.session.add(user)
		try:
			db.session.commit()
		except Exception as e:
			return False, e.__str__()

		return True, password

	@classmethod
	def create_user(cls, username: str, email: str) -> (bool, str):
		if username is None or email is None:
			return False, "Nome de usuário ou email inválidos"

		check_list = cls.check_existing_users(username, email)

		if "Error" in check_list:
			return False, "Nome de usuário ou email já cadastrado"

		elif "Reactivate" in check_list:
			return cls.reactivate_account(username)

		else:
			password = generate_password()
			user = User(username=username,
						password=hash_password(password),
						email=email,
						active=True)

			db.session.add(user)
			try:
				db.session.commit()
			except Exception as e:
				print(e)
				return False, "Erro desconhecido"

			return True, password


def generate_password() -> str:
	return str(randbelow(1000000)).zfill(6)


def hash_password(password: str) -> str:
	sha512hash = sha512(password.encode("utf-8")).digest()  # Bytes
	sha512hash_nilsafe = sha512hash.replace(b"\x00", b"\x45")  # This avoids bcrypt ValueError
	enc_password = bcrypt.generate_password_hash(sha512hash_nilsafe)  # Bytes
	enc_password_str = str(enc_password, encoding="utf8")
	return enc_password_str


def check_password_hash(user_password_hash: str, candidate_password: str) -> bool:
	candidate_sha512 = sha512(candidate_password.encode("utf-8")).digest()  # Bytes
	candidate_sha512_safe = candidate_sha512.replace(b"\x00", b"\x45")  # Bytes # Avoid bcrypt ValueError

	return bcrypt_check_password_hash(user_password_hash, candidate_sha512_safe)


def get_users_list() -> list:
	query = db.select(User). \
		where(User.username != "Admin")

	return db.session.scalars(query).all()
