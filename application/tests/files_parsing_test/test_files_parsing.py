import os

import pytest
from werkzeug.datastructures import FileStorage

from application.tests.pytest_fixtures import uploads_path, resources_path
from application.controller.transactions_utils import clean_uploaded_transactions,\
	save_uploaded_file,\
	get_extension_strategy
from application.controller.transactions_utils import extensions_support_strategies as x_strategies


@pytest.mark.parametrize(('filename', 'filesize'), (
		('146.csv', 146),
		('42.csv', 42)
))
def test_save_uploaded_file(uploads_path, resources_path, filename, filesize):
	"""
	GIVEN files with known disk size
	WHEN save_uploaded_file is called
	THEN saves them correctly to disk at correct folder
	"""
	user_id = 1

	original_file_path = os.path.join(resources_path, "uploaded_file", filename)
	stream = open(original_file_path, "rb")

	file = FileStorage(stream, filename=filename)

	resulting_file_path, error = save_uploaded_file(file, uploads_path, user_id)

	resulting_file_dirname = os.path.dirname(resulting_file_path)
	expected_file_dirname = os.path.join(uploads_path, str(user_id))

	assert os.path.exists(resulting_file_dirname)
	assert resulting_file_dirname == expected_file_dirname
	assert os.path.getsize(resulting_file_path) == filesize
	assert error is None


def test_dont_save_too_large_uploaded_file(uploads_path, resources_path):
	"""
	GIVEN large file with more than 15MB disk size
	WHEN save_uploaded_file is called
	THEN them correctly to disk at correct folder
	"""
	user_id = 2
	filename = "15,1MB.txt"

	original_file_path = os.path.join(resources_path, "uploaded_file", filename)
	stream = open(original_file_path, "rb")

	file = FileStorage(stream, filename=filename)

	resulting_file_path, error = save_uploaded_file(file, uploads_path, user_id)

	assert resulting_file_path is None
	assert error is not None


@pytest.mark.parametrize(('filename', 'expected_strategy'), (
		('42.csv', x_strategies.CsvStrategy),
		('42.txt', x_strategies.NotSupportedExtensionStrategy),
		('42.xml', x_strategies.XmlStrategy),
		('42_Upper.CSV', x_strategies.CsvStrategy),
		('42_Upper.XML', x_strategies.XmlStrategy),
))
def test_get_extension_strategy(filename, expected_strategy):
	"""
	GIVEN Files with different extensions
	WHEN get_extension_strategy called
	THEN return correct strategy
	"""
	returned_strategy = get_extension_strategy(filename)

	assert returned_strategy == expected_strategy
