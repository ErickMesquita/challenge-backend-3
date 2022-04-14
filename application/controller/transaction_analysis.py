import pandas as pd
import datetime
from decimal import Decimal
from numpy import nan


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
					 converters={"Valor": decimal_from_value})

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
