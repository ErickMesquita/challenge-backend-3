import datetime
import os
import pandas as pd
from numpy import datetime64

from application.tests.pytest_fixtures import resources_path
from application.controller.transactions_utils import clean_uploaded_transactions, CsvStrategy


def test_csv_ignore_csv_rows_with_different_dates_than_first_one(resources_path):
	"""
	GIVEN csv file with 10 rows, first row's date is 2022-01-01
	WHEN 6 rows have dates other than the first's
	THEN Only the 4 rows with matching dates shall be kept
	"""

	csv_file_path = os.path.join(resources_path, "transacoes-2022-01-01-6-different-dates.csv")
	expected_date = datetime.date(2022, 1, 1)

	df, error = CsvStrategy.read_file(csv_file_path)

	df, resulting_date, error2 = clean_uploaded_transactions(df)

	assert not error
	assert not error2
	assert df is not None
	assert len(df) == 4
	assert df["Data e hora"].iloc[0].date() == expected_date
	assert resulting_date == expected_date


def test_csv_ignore_csv_rows_with_NULL_values(resources_path):
	"""
	GIVEN csv file with 10 rows
	WHEN 6 rows (not the first one) have NULL values
	THEN Only the 4 rows without NULLs shall be kept
	"""

	csv_file_path = os.path.join(resources_path, "transacoes-2022-01-01-NULL-Values.csv")

	df, error = CsvStrategy.read_file(csv_file_path)

	df, resulting_date, error2 = clean_uploaded_transactions(df)

	assert not error
	assert not error2
	assert df is not None
	assert len(df) == 4


def test_csv_return_None_and_error_message_from_empty_file(resources_path):
	"""
	GIVEN
	WHEN empty csv file
	THEN return None and error message
	"""

	csv_file_path = os.path.join(resources_path, "vazio.csv")

	df, error = CsvStrategy.read_file(csv_file_path)

	df, resulting_date, error2 = clean_uploaded_transactions(df)

	assert not error
	assert error2 is not None
	assert df is None


def test_csv_consider_first_line_date_when_first_line_has_empty_values(resources_path):
	"""
	GIVEN csv file with 10 rows, the first one has empty origin_bank field
		  rows 2-4 have another date
	WHEN the first row has empty origin_bank field
	THEN the first row's date is considered anyway
	"""

	csv_file_path = os.path.join(resources_path, "transacoes-2022-01-01-first-line-bank-NULL.csv")

	df, error = CsvStrategy.read_file(csv_file_path)

	df, resulting_date, error2 = clean_uploaded_transactions(df)

	assert not error
	assert not error2
	assert df is not None
	assert len(df) == 6


def test_csv_consider_second_line_date_when_first_line_date_is_empty(resources_path):
	"""
	GIVEN csv file with 10 rows
	WHEN the first row has empty datetime field
	THEN the first non-empty date is considered anyway
	"""

	csv_file_path = os.path.join(resources_path, "transacoes-2022-01-01-first-line-date-NULL.csv")

	df, error = CsvStrategy.read_file(csv_file_path)

	df, resulting_date, error2 = clean_uploaded_transactions(df)

	assert not error
	assert not error2
	assert df is not None
	assert len(df) == 9


def test_csv_semicolon_separated_file(resources_path):
	"""
	GIVEN csv file separated with semicolon
	WHEN
	THEN
	"""

	csv_file_path = os.path.join(resources_path, "transacoes-2022-01-09-sus-transactions.csv")

	df, error = CsvStrategy.read_file(csv_file_path)

	df, resulting_date, error2 = clean_uploaded_transactions(df)

	assert not error
	assert not error2
	assert df is not None
	assert len(df) == 10
