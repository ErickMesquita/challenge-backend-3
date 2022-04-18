import datetime
import os

import pytest
from application.tests.pytest_fixtures import bank, branch, account

from application.models import BankAccount, Transaction, TransactionsFile, db


def test_bank_account_object_creation(bank, branch, account):
	bank_account = BankAccount(bank=bank, branch=branch, account=account)

	assert bank_account.bank == bank
	assert bank_account.branch == branch
	assert bank_account.account == account


def test_transaction_object_creation(bank, branch, account):
	recipient_bank = "BANCO EXEMPLO S.A."
	recipient_branch = "0001"
	recipient_account = "000000000002-6"

	amount = 1000000.00
	date_and_time = datetime.datetime(2022, 1, 1, 7, 30, 0)

	sender = BankAccount(bank=bank, branch=branch, account=account)
	recipient = BankAccount(bank=recipient_bank, branch=recipient_branch, account=recipient_account)

	transaction = Transaction(sender=sender, recipient=recipient,
							  amount=amount, date_and_time=date_and_time)

	assert transaction.sender.bank == bank
	assert transaction.sender.branch == branch
	assert transaction.sender.account == account
	assert transaction.sender.id == sender.id

	assert transaction.recipient.bank == recipient_bank
	assert transaction.recipient.branch == recipient_branch
	assert transaction.recipient.account == recipient_account
	assert transaction.recipient.id == recipient.id

	assert transaction.amount == amount
	assert transaction.date_and_time == date_and_time


def test_transactionsFile_object_creation():
	transactions_date = datetime.date(2022, 1, 1)
	csv_filepath = os.path.dirname(__file__)
	upload_datetime = datetime.datetime(2022, 4, 11, 12, 0, 0)

	transactions_file = TransactionsFile(transactions_date= transactions_date,
										 csv_filepath= csv_filepath,
										 upload_datetime= upload_datetime)

	assert transactions_file.transactions_date	== transactions_date
	assert transactions_file.csv_filepath		== csv_filepath
	assert transactions_file.upload_datetime	== upload_datetime