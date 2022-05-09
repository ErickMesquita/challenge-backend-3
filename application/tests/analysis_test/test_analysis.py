import pandas as pd
import pytest
from application.tests.pytest_fixtures import app

from datetime import date, datetime
from decimal import Decimal

from application.controller.transactions_utils.analysis import get_transactions_from_month, get_sus_accounts, \
	get_sus_transactions, get_sus_branches


def test_get_transactions_from_month(app):
	month, year = 1, 2022

	results = get_transactions_from_month(month, year)

	print(results)


def test_get_sus_accounts(app):
	"""
	df = pd.DataFrame({"id": range(10),
					   "date_and_time": [date(2022, 4, i+1) for i in range(10)],
					   "sender_id":		[1, 2, 3, 4, 2, 3, 4, 1, 4, 2],
					   "recipient_id":	[2, 1, 1, 1, 1, 1, 3, 4, 2, 3],
					   "amount": [Decimal(100000 + 50000*i) for i in range(10)]
					   })
	"""
	df = get_transactions_from_month(1, 2022)

	results = get_sus_accounts(df, trigger=0)
	print(results)

	assert results["sent_amount"].sum() == results["received_amount"].sum()
	assert results["sent_amount"].sum() == df["amount"].sum()


def test_get_sus_transactions(app):
	df = get_transactions_from_month(1, 2022)

	results = get_sus_transactions(df, trigger=0)

	print(results)


def test_get_sus_branches(app):
	df = get_transactions_from_month(1, 2022)

	results = get_sus_branches(df, trigger=0)

	print(results)
