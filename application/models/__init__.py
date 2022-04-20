from dataclasses import dataclass

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()


class BankAccount(db.Model):
	__tablename__ = 'bank_account'

	id = db.Column(db.Integer, primary_key=True)
	bank = db.Column(db.String(40), nullable=False)
	branch = db.Column(db.String(10), nullable=False)
	account = db.Column(db.String(15), nullable=False)

	__table_args__ = (db.UniqueConstraint(bank, branch, account,
										  name="unique_bank_accounts_constraint"),)


class Transaction(db.Model):
	id = db.Column(db.Integer, primary_key=True)

	sender_id	 = db.Column(db.Integer, db.ForeignKey('bank_account.id'))
	recipient_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'))

	sender	  = db.relationship("BankAccount", foreign_keys=[sender_id])
	recipient = db.relationship("BankAccount", foreign_keys=[recipient_id])

	amount		  = db.Column(db.Numeric, nullable=False)
	date_and_time = db.Column(db.DateTime, nullable=False)

	def __repr__(self):
		return f'<Transaction #{self.id}>'


class TransactionsFile(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	transactions_date = db.Column(db.Date, nullable=False)
	csv_filepath = db.Column(db.Text, nullable=False)
	upload_datetime = db.Column(db.DateTime, nullable=False)


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), nullable=False, unique=True)
	password = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), nullable=False, unique=True)
	login_id = db.Column(db.Integer, db.Identity(start=5000, increment=1), nullable=False, unique=True)
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

	@staticmethod
	def user_from_db(username_or_email=None, **kwargs):
		if username_or_email is None:
			query = db.select(User).filter_by(**kwargs)
		else:
			query = db.select(User). \
				where(
				db.or_(User.username == username_or_email,
					   User.email == username_or_email)
			)
		return db.session.scalars(query).first()

