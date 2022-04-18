from dataclasses import dataclass

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


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


