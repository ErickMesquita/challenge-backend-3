import pandas as pd

from application.models import BankAccount, Transaction, db
from application.tests.pytest_fixtures import app, bank, branch, account, bank2, branch2, account2, columns_names_list, transactions_df
import pytest
from sqlalchemy.exc import IntegrityError
from application.controller import transactions_utils as t_utils
from datetime import datetime


def test_bank_account_creation_on_database(app, bank, branch, account):
	"""
	WHEN Try to create two BankAccounts with same Bank, Branch and Account numbers
	THEN
	"""
	bank_account = BankAccount(bank=bank, branch=branch, account=account)

	with app.app_context():
		db.create_all()
		db.session.add(bank_account)
		try:
			db.session.commit()
		except IntegrityError:
			print("This bank_account already exists")

	bank_account = BankAccount.query.first()

	assert bank_account.bank == bank
	assert bank_account.branch == branch
	assert bank_account.account == account


def test_bank_account_table_existence_on_database(app):
	insp = db.inspect(db.engine)
	assert insp.has_table("bank_account") is True


def test_bank_account_uniqueness_constraint(app, bank, branch, account):
	"""
	WHEN Try to create two BankAccounts with same Bank, Branch and Account numbers
	THEN Raise IntegrityError
	"""
	bank_account1 = BankAccount(bank=bank, branch=branch, account=account)
	bank_account2 = BankAccount(bank=bank, branch=branch, account=account)

	with app.app_context():
		db.session.add(bank_account1)
		db.session.add(bank_account2)
		with pytest.raises(IntegrityError):
			db.session.commit()


def test_push_bank_accounts_df_to_database(app, transactions_df):
	t_utils.push_bank_accounts_to_database(transactions_df)


def test_push_transactions_df_to_database(app, columns_names_list, transactions_df,
										  bank, branch, account,
										  bank2, branch2, account2,):
	t_utils.push_transactions_to_db(transactions_df)
