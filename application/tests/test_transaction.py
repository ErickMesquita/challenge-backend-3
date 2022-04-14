import os
from pytest_fixtures import app, client, resources_path


def test_response_200_when_access_homepage(client):
	response = client.get("/")
	assert response.status_code == 200


def test_response_200_when_access_transaction_form(client):
	response = client.get("/forms/transaction")
	assert response.status_code == 200
	assert b'<form method="post"' in response.data


def test_redirect_to_form_when_no_file_is_sent(client):
	"""
	GIVEN
	WHEN  POST HTTP request without file attached
	THEN  return redirect to form page
	"""
	response = client.post("/transaction")
	assert response.status_code == 303


def test_redirect_to_form_when_blank_filename(client):
	"""
	GIVEN User doesn't select a file
	WHEN  Request blank filename attached
	THEN  return redirect to form page
	"""
	from io import BytesIO
	response = client.post("/transaction", data={"file": (BytesIO(b""), "", "csv")})
	assert response.status_code == 303


def test_redirect_to_form_when_unallowed_file_extension(client):
	"""
	GIVEN File attached to request
	WHEN  File extension not in ALLOWED_EXTENSIONS
	THEN  return redirect to form page
	"""
	from io import BytesIO
	response = client.post("/transaction", data={"file": (BytesIO(b""), "filename", "exe")})
	assert response.status_code == 303


def test_save_csv_file_after_upload(app, client, resources_path):
	"""
	GIVEN File attached to request
	WHEN  File OK
	THEN  save it to UPLOAD_FOLDER
	"""
	filename = "146.csv"
	csv_file_146_bytes_path = os.path.join(resources_path, filename)
	uploaded_file_path = os.path.join(app.config.get("UPLOAD_FOLDER"), filename)

	if os.path.exists(uploaded_file_path):
		os.remove(uploaded_file_path)

	with open(csv_file_146_bytes_path, "rb") as csv_file_146_bytes:
		response = client.post("/transaction", data={"file": (csv_file_146_bytes, "146.csv", "csv")})

	assert response.status_code == 303
	assert os.path.exists(uploaded_file_path) == True
	assert os.path.getsize(uploaded_file_path) == 146

	if os.path.exists(uploaded_file_path):
		os.remove(uploaded_file_path)
