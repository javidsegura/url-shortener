import os

class Settings:
	"""Application settings loaded from environment variables."""
	
	def __init__(self):
		self.ENVIRONMENT = os.getenv("ENVIRONMENT").lower()
		print(f"ENVIRONMENT IS: {self.ENVIRONMENT}")
		self._extract_all_variables()
	
	def _extract_all_variables(self):

		self._extract_database_variables()
		self._extract_aws_variables()
		self._extract_app_logic_variables()
		
		# Validate required environment variables
		self._validate_required_vars()

	def _extract_secret_manger_databaseb_credentials(self, secret_key):
		from url_shortener.services.infra.secretsmanager import SecretsManager 
		db_credentials = SecretsManager().fetch_secret(secret_key=secret_key)
		return db_credentials

	def _extract_database_variables(self):
		self.REDIS_URL = os.getenv("REDIS_URL")
		self.MYSQL_PORT = os.getenv("MYSQL_PORT")
		self.MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
		self.MYSQL_SYNC_DRIVER = os.getenv("MYSQL_SYNC_DRIVER")
		self.MYSQL_ASYNC_DRIVER = os.getenv("MYSQL_ASYNC_DRIVER")
		if self.ENVIRONMENT != "dev":
			self.MYSQL_HOST = os.getenv("RDS_MYSQL_HOST") 

			secret_key = os.getenv("SECRETS_MANAGER_DB_CREDENTIALS_KEY")
			if not secret_key:
				raise ValueError("RDS db credentials key is needed!")
			print("Secret key is: ", secret_key)

			db_credentials = self._extract_secret_manger_databaseb_credentials(secret_key)
			print(f"DB credentials is: {db_credentials}")
			self.MYSQL_USER = db_credentials["username"]
			self.MYSQL_PASSWORD = db_credentials["password"]
		else:
			self.MYSQL_HOST = os.getenv("MYSQL_HOST")
			self.MYSQL_USER = os.getenv("MYSQL_USER")
			self.MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

	def _extract_aws_variables(self):
		self.S3_MAIN_BUCKET_NAME = os.getenv("S3_MAIN_BUCKET_NAME")

	def _extract_app_logic_variables(self):
		self.SHORTENED_URL_LENGTH = int(os.getenv("SHORTENED_URL_LENGTH", "8"))
		self.MAX_MINUTES_STORAGE = int(os.getenv("MAX_MINUTES_STORAGE", "60"))
		self.MIN_MINUTES_STORAGE = int(os.getenv("MIN_MINUTES_STORAGE", "5"))
		
		
	
	def _validate_required_vars(self):
		"""Validate that all required environment variables are set."""
		required_vars = [
			"REDIS_URL", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_HOST",
			"MYSQL_PORT", "MYSQL_DATABASE", "MYSQL_SYNC_DRIVER", 
			"MYSQL_ASYNC_DRIVER", "S3_MAIN_BUCKET_NAME"
		]
		
		missing_vars = []
		for var in required_vars:
			if not getattr(self, var):
				missing_vars.append(var)
		
		if missing_vars:
			raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")



app_settings = Settings()
print(f"SETTINGS VLAUE: {app_settings.__dict__}") ## REMOVE IN PROD
