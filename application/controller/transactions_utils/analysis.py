from typing import List

import pandas as pd

from application.controller.transactions_utils import get_bank_account_from_id
from application.models import db, Transaction, BankAccount
import datetime


def get_transactions_from_month(month: int = None, year: int = None, date: datetime.date = None) \
								-> pd.DataFrame:
	if (not month or not year) and not date:
		return pd.DataFrame()

	if month > 12:
		month = 12

	if month < 1:
		month = 1

	if not date:
		date = datetime.date(year, month, 1)

	query = db.select(Transaction).where(
		db.and_(db.extract("YEAR", Transaction.date_and_time) == date.year,
				db.extract("MONTH", Transaction.date_and_time) == date.month)
	)

	transactions = pd.read_sql_query(query, db.get_engine(), index_col="id", coerce_float=False, parse_dates=["date_and_time"])

	return join_bank_account_data(transactions)


def join_bank_account_data(transactions: pd.DataFrame) -> pd.DataFrame:
	if transactions.empty:
		df = pd.concat([transactions,
						pd.DataFrame(columns=["sender_bank", "sender_branch", "sender_account",
											  "recipient_bank", "recipient_branch", "recipient_account"])
						])
		return df

	account_ids_list = pd.concat([transactions["sender_id"], transactions["recipient_id"]]).drop_duplicates().to_list()

	bank_accounts = get_bank_account_from_id(account_ids_list, as_dataframe=True)

	bank_accounts_joined_sender = transactions. \
		join(bank_accounts, on="sender_id").rename(columns={"bank": "sender_bank",
															"branch": "sender_branch",
															"account": "sender_account"})

	bank_accounts_joined_sender_and_recipient = bank_accounts_joined_sender. \
		join(bank_accounts, on="recipient_id").rename(columns={"bank": "recipient_bank",
															   "branch": "recipient_branch",
															   "account": "recipient_account"})

	return bank_accounts_joined_sender_and_recipient


def get_sus_transactions(transactions: pd.DataFrame, trigger: int = 100000) -> pd.DataFrame:
	"""
	Uma transação deve ser considerada suspeita se o seu valor for
	igual ou superior a R$100.000,00.
	"""
	transactions = transactions[transactions["amount"] >= trigger]

	if transactions.empty:
		return pd.DataFrame()

	return transactions


def get_sus_accounts(transactions: pd.DataFrame, trigger: int = 1000000) -> pd.DataFrame:
	"""
	Uma conta bancária deve ser considerada suspeita se o somatório
	de sua movimentação no mês for superior a R$1.000.000,00, seja
	enviando ou recebendo tal quantia.
	"""

	sent_amount = transactions.groupby("sender_id")["amount"].sum().rename("sent_amount")
	received_amount = transactions.groupby("recipient_id")["amount"].sum().rename("received_amount")

	grouped_transactions = pd.concat([sent_amount, received_amount], axis="columns").fillna(0)
	grouped_transactions.rename_axis("bank_account_id", inplace=True)

	sus_accounts = grouped_transactions[(grouped_transactions["sent_amount"] > trigger) |
								(grouped_transactions["received_amount"] > trigger)]

	account_ids_list = sus_accounts.index.to_list()

	bank_accounts = get_bank_account_from_id(account_ids_list, as_dataframe=True)

	return sus_accounts.join(bank_accounts)


def get_sus_branches(transactions: pd.DataFrame, trigger: int = 1000000000) -> pd.DataFrame:
	"""
	Uma agência bancária deve ser considerada suspeita se o somatório das
	movimentações no mês de todas as suas contas for superior a
	R$1.000.000.000,00, seja enviando ou recebendo tal quantia.
	"""

	sent_amount = transactions.groupby(["sender_bank", "sender_branch"])["amount"].sum().rename("sent_amount")
	received_amount = transactions.groupby(["recipient_bank", "recipient_branch"])["amount"].sum().rename("received_amount")

	branches = pd.concat([sent_amount, received_amount], axis="columns").fillna(0)

	branches = branches.reset_index().rename(columns={"level_0": "bank",
													  "level_1": "branch"})

	sus_branches = branches[(branches["sent_amount"] > trigger) |
				   			(branches["received_amount"] > trigger)]

	return sus_branches


