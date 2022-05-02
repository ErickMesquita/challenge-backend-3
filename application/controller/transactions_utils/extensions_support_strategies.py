from datetime import datetime
from abc import ABC, abstractmethod
import pandas as pd
from defusedxml import ElementTree as ET


class ExtensionsSupportStrategy(ABC):
	columns_names_list = ["Banco origem",
						  "Agência origem",
						  "Conta origem",
						  "Banco destino",
						  "Agência destino",
						  "Conta destino",
						  "Valor",
						  "Data e hora"]

	@classmethod
	@abstractmethod
	def read_file(cls, file_or_path) -> (pd.DataFrame, str):
		pass


class CsvStrategy(ExtensionsSupportStrategy):

	@classmethod
	def read_file(cls, file_or_path):
		from application.controller.transactions_utils import decimal_from_value
		df = pd.read_csv(file_or_path, names=cls.columns_names_list,
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
		return df, None


class XmlStrategy(ExtensionsSupportStrategy):
	"""
	It’s just XML, what could probably go wrong?
		- Christian Heimes <christian@python.org>
	"""

	@classmethod
	def read_file(cls, file_or_path):
		from application.controller.transactions_utils import decimal_from_value
		tree = ET.parse(file_or_path)
		root = tree.getroot()

		df = pd.DataFrame(columns=cls.columns_names_list)

		for transaction in root.iter('transacao'):
			amount = transaction.find('valor')
			amount = amount.text if amount else ""
			amount = decimal_from_value(amount)

			date_and_time = transaction.find('data')
			try:
				date_and_time = datetime.fromisoformat(date_and_time.text)
			except (AttributeError, ValueError, TypeError):
				date_and_time = pd.NaT

			sender = transaction.find('origem')
			sender_bank, sender_branch, sender_account = cls.parse_bank_account(sender)

			recipient = transaction.find('destino')
			recipient_bank, recipient_branch, recipient_account = cls.parse_bank_account(recipient)

			df_row = pd.DataFrame([(sender_bank, sender_branch, sender_account,
									recipient_bank, recipient_branch, recipient_account,
									amount, date_and_time)], columns=cls.columns_names_list)

			pd.concat([df, df_row], ignore_index=True)

		return df, None

	@classmethod
	def parse_bank_account(cls, bank_account) -> (str, str, str):
		"""
		Returns tuple (bank, branch, account) from given bank_account Element
		"""
		if not bank_account:
			return "", "", ""

		bank = bank_account.find('banco')
		bank = bank.text if bank else ""

		branch = bank_account.find('agencia')
		branch = branch.text if branch else ""

		account = bank_account.find('conta')
		account = account.text if account else ""

		return bank, branch, account


class NotSupportedExtensionStrategy(ExtensionsSupportStrategy):

	@classmethod
	def read_file(cls, file_or_path):
		return pd.DataFrame(), "Extensão de arquivo não suportada"
