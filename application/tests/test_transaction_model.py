import datetime
import os
from application.models import Transaction, TransactionsFile


def test_transaction_object_creation():
	banco_origem = "BANCO BANCÃO SA"
	agencia_origem = "0001"
	conta_origem = "00001-1"
	banco_destino = "BANCO EXEMPLO S.A."
	agencia_destino = "0001"
	conta_destino = "000000000002-6"
	valor = 1000000.00
	data_e_hora = datetime.datetime(2022, 1, 1, 7, 30, 0)

	transaction = Transaction(banco_origem=banco_origem, agencia_origem=agencia_origem, conta_origem=conta_origem,
							  banco_destino=banco_destino, agencia_destino=agencia_destino, conta_destino=conta_destino,
							  valor=valor, data_e_hora=data_e_hora)

	assert transaction.banco_origem == banco_origem
	assert transaction.agencia_origem == agencia_origem
	assert transaction.conta_origem == conta_origem
	assert transaction.banco_destino == banco_destino
	assert transaction.agencia_destino == agencia_destino
	assert transaction.conta_destino == conta_destino
	assert transaction.valor == valor
	assert transaction.data_e_hora == data_e_hora


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