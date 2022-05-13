from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
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

	sender	  = db.relationship("BankAccount", foreign_keys=[sender_id], backref="transactions_sent")
	recipient = db.relationship("BankAccount", foreign_keys=[recipient_id], backref="transactions_received")

	amount		  = db.Column(db.Numeric, nullable=False)
	date_and_time = db.Column(db.DateTime, nullable=False)

	file_id = db.Column(db.Integer, db.ForeignKey('transactions_file.id'))
	file = db.relationship("TransactionsFile", back_populates="transactions")

	def __repr__(self):
		return f'<Transaction #{self.id}>'


class TransactionsFile(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	transactions_date = db.Column(db.Date, unique=True, nullable=False)
	upload_datetime = db.Column(db.DateTime, nullable=False)

	user_id	 = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	user	  = db.relationship("User", foreign_keys=[user_id])

	transactions = db.relationship("Transaction", back_populates="file")


