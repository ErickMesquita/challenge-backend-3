from dataclasses import dataclass

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


class Transaction(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	banco_origem	= db.Column(db.String(40), nullable=False)
	agencia_origem	= db.Column(db.String(10), nullable=False)
	conta_origem	= db.Column(db.String(15), nullable=False)
	banco_destino	= db.Column(db.String(40), nullable=False)
	agencia_destino	= db.Column(db.String(10), nullable=False)
	conta_destino	= db.Column(db.String(15), nullable=False)
	valor			= db.Column(db.Numeric, nullable=False)
	data_e_hora		= db.Column(db.DateTime, nullable=False)

	def __repr__(self):
		return f'<Transaction #{self.id}>'


class TransactionsFile(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	transactions_date = db.Column(db.Date, nullable=False)
	csv_filepath = db.Column(db.Text, nullable=False)
	upload_datetime = db.Column(db.DateTime, nullable=False)


