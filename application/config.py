class Config(object):
	"""Base configuration"""
	TESTING = False


class ProductionConfig(Config):
	"""Production configuration"""


class DevelopmentConfig(Config):
	"""Development configuration"""


class TestingConfig(Config):
	"""Testing configuration"""

	TESTING = True