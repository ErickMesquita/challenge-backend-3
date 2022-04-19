import pandas as pd
import datetime
from decimal import Decimal
from numpy import nan
from application.models import db, BankAccount, Transaction
from sqlalchemy.exc import IntegrityError


def decimal_from_value(value):
	if value is None or value == "" or value is nan or value is pd.NaT:
		return nan
	return Decimal(value)


def clean_uploaded_transactions_csv(file_or_path) -> (pd.DataFrame, str):
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
		return None, "Error: Invalid Date"

	if df.empty:
		return None, "Error: Empty File"

	first_date = df["Data e hora"].iloc[0].date()
	df = df[df["Data e hora"].apply(lambda x: x.date()) == first_date]

	df.dropna(inplace=True)

	return df, ""


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
			print("This bank_account already exists")
			db.session.rollback()


def push_transactions_to_db(df: pd.DataFrame):
	if df.empty:
		return
	"""
	x = df[:1]
	print(f"x['Banco origem'][0]={x['Banco origem'][0]}")
	print(f"type(x['Banco origem'][0])={type(x['Banco origem'][0])}")
	q = db.select(BankAccount.id).filter_by(bank=x["Banco origem"][0],
											branch=x["Agência origem"][0],
											account=x["Conta origem"][0])
	executed_query = db.session.execute(q)
	print(f"executed_query= {executed_query}")

	lista = executed_query.first()
	print(f"lista={lista}")
	print(f"type(lista)= {type(lista)}")
	"""

	if not db.inspect(db.engine).has_table("transaction"):
		db.create_all()

	for index, row in df.iterrows():
		executed_query = db.session.execute(
			db.select(BankAccount.id).filter_by(bank=row["Banco origem"],
												branch=row["Agência origem"],
												account=row["Conta origem"])
		).first()
		sender_id = executed_query[0] if executed_query is not None else None
		df.loc[index, "sender_id"] = sender_id

		executed_query = db.session.execute(
			db.select(BankAccount.id).filter_by(bank=row["Banco destino"],
												branch=row["Agência destino"],
												account=row["Conta destino"])
		).first()
		recipient_id = executed_query[0] if executed_query is not None else None
		df.loc[index, "recipient_id"] = recipient_id

		transaction = Transaction(sender_id=sender_id, recipient_id=recipient_id,
								  amount=row["Valor"], date_and_time=row["Data e hora"])

		db.session.add(transaction)

	db.session.commit()
	return df