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
	echo = os.environ.get("DB_ECHO")

	SQLALCHEMY_DATABASE_URI = \
	f"postgresql://{user}:{password}@{host}:{port}/{database}"


class ProductionConfig(Config):
	"""Production configuration"""


class DevelopmentConfig(Config):
	"""Development configuration"""


class TestingConfig(Config):
	"""Testing configuration"""

	TESTING = True