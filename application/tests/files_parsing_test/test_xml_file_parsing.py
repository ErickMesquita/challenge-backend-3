import datetime
import os
import pandas as pd
from numpy import datetime64

from application.tests.pytest_fixtures import resources_path
from application.controller.transactions_utils import clean_uploaded_transactions, XmlStrategy


def test_parse_xml_to_df(resources_path):
	"""
	GIVEN XML file with 10 rows, first row's date is 2022-01-02
	WHEN All rows are perfectly according to rules
	THEN Parse XML file to pandas.DataFrame
	"""

	xml_file_path = os.path.join(resources_path, "transacoes-2022-01-02.xml")
	expected_date = datetime.date(2022, 1, 2)

	df, error = XmlStrategy.read_file(xml_file_path)
	print(df)

	assert not error
	assert len(df) == 10
	assert df["Data e hora"].iloc[0].date() == expected_date


def test_clean_xml(resources_path):
	"""
	GIVEN XML file with 10 rows, first row's date is 2022-01-02
	WHEN 6 rows have NULL values
	THEN Parse XML file to pandas.DataFrame
	"""

	xml_file_path = os.path.join(resources_path, "transacoes-2022-01-02-6-NULL-Values.xml")

	expected_date = datetime.date(2022, 1, 2)

	df, error = XmlStrategy.read_file(xml_file_path)

	df, date, error = clean_uploaded_transactions(df)

	print(df)

	assert not error
	assert len(df) == 4
	assert df["Data e hora"].iloc[0].date() == expected_date
