from typing import Union, List, Type
from sys import getsizeof
import pandas as pd
import datetime
from decimal import Decimal
from numpy import nan

from application.controller.transactions_utils.extensions_support_strategies import CsvStrategy,\
	XmlStrategy, \
	ExtensionsSupportStrategy, \
	NotSupportedExtensionStrategy
from application.models import db, BankAccount, Transaction, TransactionsFile
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
import os.path

from application.models.user import User


def decimal_from_value(value):
	if value is None or value == "" or value is nan or value is pd.NaT:
		return nan
	return Decimal(value)


def save_uploaded_file(file, upload_folder_path: str, user_id: int) -> (Union[str, None], Union[str, None]):
	filesize = len(file.read())
	print("len(file.read()): ", len(file.read()))
	file.seek(0)

	if filesize > 15 * 2**20:
		error = f"O tamanho do arquivo ({filesize}) excede o limite de 15MB"
		return None, error

	filename = secure_filename(file.filename)
	directory_path = os.path.join(upload_folder_path, str(user_id))

	if not os.path.exists(directory_path):
		print(f"Criando pasta {directory_path}")
		os.mkdir(directory_path)

	file_path = os.path.join(directory_path, filename)

	number = 2
	while os.path.exists(file_path):
		base, ext = os.path.splitext(filename)
		file_path = os.path.join(directory_path, base+f"_{number}"+ext)
		number += 1

	try:
		file.save(file_path)
	except Exception as e:
		return None, e.__str__()

	return file_path, None


def get_extension_strategy(filename: str) -> Union[None, Type[ExtensionsSupportStrategy]]:
	if not filename:
		return None

	_, ext = os.path.splitext(filename)
	ext = ext.lower()

	if ext == ".csv":
		return CsvStrategy

	if ext == ".xml":
		return XmlStrategy

	return NotSupportedExtensionStrategy


def clean_uploaded_transactions(df: pd.DataFrame) -> (pd.DataFrame, datetime.datetime, str):

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


def get_bank_account_from_id(bk_id: Union[int, List[int]], as_dataframe: bool = False)\
							-> Union[pd.DataFrame, List[BankAccount]]:
	if not bk_id:
		return list()

	if isinstance(bk_id, int):
		bk_id = [bk_id]

	query = db.select(BankAccount).where(BankAccount.id.in_(bk_id))

	if as_dataframe:
		return pd.read_sql_query(query, db.get_engine(), index_col="id", coerce_float=False)

	return db.session.scalars(query).all()


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


def push_transactions_to_db(df: pd.DataFrame, date: datetime.datetime, user: User, filepath: str)\
							-> (Union[str, None], Union[str, None]):
	if df.empty:
		return None, "Nenhuma transação no arquivo"

	if date_already_in_db(date):
		return None, f"As transações do dia {date} já foram adicionadas"

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

	try:
		db.session.commit()
	except IntegrityError as e:
		return None, e.__str__()

	return "Importação bem sucedida", None


def transactions_file_from_date(date: datetime.date) -> Union[TransactionsFile, None]:
	if not date:
		return None

	query = db.select(TransactionsFile).where(TransactionsFile.transactions_date == date)

	return db.session.scalars(query).all()


def date_already_in_db(date: datetime.date) -> Union[bool, None]:
	if not date:
		return None

	return len(transactions_file_from_date(date)) > 0


def get_transactions_files_list() -> List[TransactionsFile]:
	query = db.select(TransactionsFile)
	return db.session.scalars(query).all()


def transactions_file_from_id(tf_id: int) -> Union[TransactionsFile, None]:
	if tf_id is None:
		return None

	query = db.select(TransactionsFile).where(TransactionsFile.id == tf_id)

	return db.session.scalars(query).first()
