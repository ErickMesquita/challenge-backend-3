import os


class Config(object):
	"""Base configuration"""
	TESTING = False

	database = os.environ.get("APPLICATION_DB")
	# Note que aqui não usamos "POSTGRES_DB". É uma boa prática separar a DB da nossa aplicação da DB padrão do Postgres

	user = os.environ.get("POSTGRES_USER")
	password = os.environ.get("POSTGRES_PASSWORD")
	host = os.environ.get("POSTGRES_HOSTNAME")
	port = os.environ.get("POSTGRES_PORT")

	encoding = os.environ.get("DB_ENCODING")
	SQLALCHEMY_ECHO = os.environ.get("DB_ECHO")
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQLALCHEMY_DATABASE_URI = \
	f"postgresql://{user}:{password}@{host}:{port}/{database}"

	UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
	ALLOWED_EXTENSIONS = {"csv"}


class ProductionConfig(Config):
	"""Production configuration"""


class DevelopmentConfig(Config):
	"""Development configuration"""
	SECRET_KEY = "senha123"

class TestingConfig(Config):
	"""Testing configuration"""
	SECRET_KEY = "senha123"
	TESTING = True
	SQLALCHEMY_TRACK_MODIFICATIONS = True
