from typing import Union

import pandas as pd
import datetime
from decimal import Decimal
from numpy import nan
from application.models import db, BankAccount, Transaction, TransactionsFile
from sqlalchemy.exc import IntegrityError

from application.models.user import User


def decimal_from_value(value):
	if value is None or value == "" or value is nan or value is pd.NaT:
		return nan
	return Decimal(value)


def clean_uploaded_transactions_csv(file_or_path) -> ((pd.DataFrame, datetime.datetime), str):
	columns_names_list = ["Banco origem",
						  "Agência origem",
						  "Conta origem",
						  "Banco destino",
						  "Agência destino",
						  "Conta destino",
						  "Valor",
						  "Data e hora"]

	df = pd.read_csv(file_or_path, names=columns_names_list,
					 infer_datetime_format=True,
					 parse_dates=[7],
					 converters={"Valor": decimal_from_value,
								 "Banco origem": str,
								 "Agência origem": str,
								 "Conta origem": str,
								 "Banco destino": str,
								 "Agência destino": str,
								 "Conta destino": str
	})

	while len(df) > 1 and (df["Data e hora"].iloc[0] is None or
						   df["Data e hora"].iloc[0] == "" or
						   df["Data e hora"].iloc[0] is pd.NaT):
		df = df[1:]

	if not df.empty and (df["Data e hora"].iloc[0] is None or
						 df["Data e hora"].iloc[0] == "" or
						 df["Data e hora"].iloc[0] is pd.NaT):
		return None, None, "Error: Invalid Date"

	if df.empty:
		return None, None, "Error: Empty File"

	first_date = df["Data e hora"].iloc[0].date()

	df = df.replace("", nan).dropna()

	df = df[df["Data e hora"].apply(lambda x: x.date()) == first_date]

	return df, first_date, ""


def bank_account_id_from_database(bk: BankAccount = None, bank=None, branch=None, account=None):
	if bk is None:
		bk = BankAccount(bank=bank, branch=branch, account=account)

	if bk.id is not None:
		return bk.id

	query = db.select(BankAccount).filter_by(bank=bk.bank,
											 branch=bk.branch,
											 account=bk.account)
	result = db.session.execute(query).first()

	if result is not None:  # Found on DB
		return result[0].id

	db.session.add(bk)
	db.session.commit()

	return bk.id


def push_bank_accounts_to_database(df: pd.DataFrame):
	if df.empty:
		return

	sender_accounts = df[["Banco origem",
						  "Agência origem",
						  "Conta origem"]]

	sender_accounts.rename(columns={"Banco origem": "bank",
							"Agência origem": "branch",
							"Conta origem": "account"}, inplace=True)

	recipient_accounts = df[["Banco destino",
						  "Agência destino",
						  "Conta destino"]]

	recipient_accounts.rename(columns={"Banco destino": "bank",
							"Agência destino": "branch",
							"Conta destino": "account"}, inplace=True)

	all_accounts = pd.concat([sender_accounts, recipient_accounts], ignore_index=True)
	unique_accounts = all_accounts.drop_duplicates()

	if not db.inspect(db.engine).has_table("bank_account"):
		db.create_all()

	for account in unique_accounts.itertuples():
		bank_account = BankAccount(bank=account.bank, branch=account.branch, account=account.account)
		db.session.add(bank_account)
		try:
			db.session.commit()
		except IntegrityError:
			db.session.rollback()


def push_transactions_to_db(df: pd.DataFrame, date: datetime.datetime, user: User, filepath: str):
	if df.empty:
		return

	if not db.inspect(db.engine).has_table("transaction"):
		db.create_all()

	t_file = TransactionsFile(transactions_date=date,
							  csv_filepath=filepath,
							  upload_datetime=datetime.datetime.now(),
							  user_id=user.id)
	db.session.add(t_file)

	for index, row in df.iterrows():
		sender_id = bank_account_id_from_database(bank=row["Banco origem"],
												  branch=row["Agência origem"],
												  account=row["Conta origem"])
		df.loc[index, "sender_id"] = sender_id

		recipient_id = bank_account_id_from_database(bank=row["Banco destino"],
													 branch=row["Agência destino"],
													 account=row["Conta destino"])
		df.loc[index, "recipient_id"] = recipient_id

		transaction = Transaction(sender_id=sender_id, recipient_id=recipient_id, file=t_file,
								  amount=row["Valor"], date_and_time=row["Data e hora"])

		db.session.add(transaction)

	db.session.commit()
	return df
