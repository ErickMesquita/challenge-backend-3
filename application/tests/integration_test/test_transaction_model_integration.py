import pandas as pd

from application.controller.transactions_utils import get_bank_account_from_id
from application.models import BankAccount, Transaction, db
from application.tests.pytest_fixtures import app, bank, branch, account,\
	bank2, branch2, account2, columns_names_list, transactions_df, logged_in_client
import pytest
from sqlalchemy.exc import IntegrityError
from application.controller import transactions_utils as t_utils
from datetime import datetime


def test_raise_error_when_create_two_bank_accounts_with_same_parameters_on_database(app, bank, branch, account):
	"""
	WHEN Try to create two BankAccounts with same Bank, Branch and Account numbers
	THEN Create the first one, Raise IntegrityError on the second
	"""
	bank_account = BankAccount(bank=bank, branch=branch, account=account)
	bank_account2 = BankAccount(bank=bank, branch=branch, account=account)

	with app.app_context():
		db.create_all()
		db.session.add(bank_account)
		db.session.add(bank_account2)
		with pytest.raises(IntegrityError):
			db.session.commit()
			print("This bank_account already exists")

	query = db.select(BankAccount).filter_by(bank=bank, branch=branch, account=account)
	bank_account = db.session.scalars(query).first()

	assert bank_account is not None
	assert bank_account.bank == bank
	assert bank_account.branch == branch
	assert bank_account.account == account


def test_bank_account_id_from_database(app, bank, branch, account):
	"""
	GIVEN Bank account is already at database
	THEN properly return its id number
	"""
	bk = BankAccount(bank=bank, branch=branch, account=account)

	assert bk.id is None
	id_bk = t_utils.bank_account_id_from_database(bk)
	assert id_bk is not None
	assert type(id_bk) == int


def test_get_bank_account_from_id(app):
	bk_id = db.session.scalars(db.select(BankAccount.id)).first()

	result = get_bank_account_from_id(bk_id)

	assert isinstance(result, list)
	assert len(result) == 1


def test_get_bank_account_from_id_as_dataframe(app):
	bk_id = db.session.scalars(db.select(BankAccount.id)).first()

	result = get_bank_account_from_id(bk_id, as_dataframe=True)

	print(result)

	assert isinstance(result, pd.DataFrame)
	assert len(result) == 1


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
