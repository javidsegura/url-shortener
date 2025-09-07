import os

from dotenv import load_dotenv

class Settings:
	"""Application settings loaded from environment variables."""
	
	def __init__(self):
		ENVIRONMENT = os.getenv("ENVIRONMENT", "dev").lower()

		if "dev" in ENVIRONMENT:
			load_dotenv(f".env.dev.synced")
			print(f"Just loaded file via dotenv")

		# Database configuration
		self.REDIS_URL = os.getenv("REDIS_URL")
		self.MYSQL_USER = os.getenv("MYSQL_USER")
		self.MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
		self.MYSQL_HOST = os.getenv("MYSQL_HOST")
		self.MYSQL_PORT = os.getenv("MYSQL_PORT")
		self.MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
		self.MYSQL_SYNC_DRIVER = os.getenv("MYSQL_SYNC_DRIVER")
		self.MYSQL_ASYNC_DRIVER = os.getenv("MYSQL_ASYNC_DRIVER")
		
		# S3 configuration
		self.S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
		
		# Application settings with defaults
		self.SHORTENED_URL_LENGTH = int(os.getenv("SHORTENED_URL_LENGTH", "8"))
		self.MAX_MINUTES_STORAGE = int(os.getenv("MAX_MINUTES_STORAGE", "120"))
		
		# Validate required environment variables
		self._validate_required_vars()
	
	def _validate_required_vars(self):
		"""Validate that all required environment variables are set."""
		required_vars = [
			"REDIS_URL", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_HOST",
			"MYSQL_PORT", "MYSQL_DATABASE", "MYSQL_SYNC_DRIVER", 
			"MYSQL_ASYNC_DRIVER", "S3_BUCKET_NAME"
		]
		
		missing_vars = []
		for var in required_vars:
			if not getattr(self, var):
				missing_vars.append(var)
		
		if missing_vars:
			raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")


settings = Settings()
print(f"SETTINGS VLAUE: {settings.__dict__}")