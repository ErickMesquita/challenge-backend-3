import datetime
import os
import pandas as pd
from numpy import datetime64

from pytest_fixtures import resources_path
from application.controller.transaction_analysis import clean_uploaded_transactions_csv


def test_ignore_csv_rows_with_different_dates_than_first_one(resources_path):
	"""
	GIVEN csv file with 10 rows, first row's date is 2022-01-01
	WHEN 6 rows have dates other than the first's
	THEN Only the 4 rows with matching dates shall be kept
	"""

	csv_file_path = os.path.join(resources_path, "transacoes-2022-01-01-6-different-dates.csv")
	date = datetime.date(2022, 1, 1)

	df, error = clean_uploaded_transactions_csv(csv_file_path)

	assert error is None or error == ""
	assert df is not None
	assert len(df) == 4
	assert df["Data e hora"].iloc[0].date() == date


def test_ignore_csv_rows_with_NULL_values(resources_path):
	"""
	GIVEN csv file with 10 rows
	WHEN 6 rows (not the first one) have NULL values
	THEN Only the 4 rows without NULLs shall be kept
	"""

	csv_file_path = os.path.join(resources_path, "transacoes-2022-01-01-NULL-Values.csv")

	df, error = clean_uploaded_transactions_csv(csv_file_path)

	assert error is None or error == ""
	assert df is not None
	assert len(df) == 4


def test_ignore_csv_rows_with_NULL_values(resources_path):
	"""
	GIVEN csv file with 10 rows
	WHEN 6 rows (not the first one) have NULL values
	THEN Only the 4 rows without NULLs shall be kept
	"""

	csv_file_path = os.path.join(resources_path, "transacoes-2022-01-01-NULL-Values.csv")

	df, error = clean_uploaded_transactions_csv(csv_file_path)

	assert error is None or error == ""
	assert df is not None
	assert len(df) == 4