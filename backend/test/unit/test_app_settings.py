import os
from unittest.mock import patch
import pytest
from url_shortener.core.settings.app_settings import Settings
from url_shortener.core.settings.environment.dev import DevSettings

# Healthy input
def test_settings_extract_env():
      test_env = {
            "ENVIRONMENT": "dev",
            "REDIS_URL": "redis://localhost:6379/0",
            "MYSQL_HOST": "localhost",
            "MYSQL_PORT": "3306",
            "MYSQL_DATABASE": "test_db",
            "MYSQL_USER": "test_user",
            "MYSQL_PASSWORD": "test_password",
            "MYSQL_SYNC_DRIVER": "pymysql",
            "MYSQL_ASYNC_DRIVER": "aiomysql",
            "CLOUD_PROVIDER": "aws",
            "S3_MAIN_BUCKET_NAME": "test-bucket",
            "AWS_MAIN_REGION": "us-east-1",
      }
      with patch.dict(os.environ, values=test_env, clear=True):
            app_settings: DevSettings = Settings().get_settings()
            
            assert app_settings.REDIS_URL == "redis://localhost:6379/0"
            assert app_settings.MYSQL_HOST == "localhost"
            assert app_settings.MYSQL_PORT == "3306"
            assert app_settings.MYSQL_DATABASE == "test_db"
            assert app_settings.MYSQL_USER == "test_user"
            assert app_settings.MYSQL_PASSWORD == "test_password"
            assert app_settings.MYSQL_SYNC_DRIVER == "pymysql"
            assert app_settings.MYSQL_ASYNC_DRIVER == "aiomysql"
            assert app_settings.CLOUD_PROVIDER == "aws"
            assert app_settings.S3_MAIN_BUCKET_NAME == "test-bucket"
            assert app_settings.AWS_MAIN_REGION == "us-east-1"
            assert app_settings.SHORTENED_URL_LENGTH == 8  
            assert app_settings.MAX_MINUTES_STORAGE == 60  
            assert app_settings.MIN_MINUTES_STORAGE == 5 

def test_settings_extract_prod(mock_aws_secrets):
      test_env = {
            "ENVIRONMENT": "production",
            "REDIS_URL": "redis://localhost:6379/0",
            "MYSQL_PORT": "3306",
            "MYSQL_DATABASE": "test_db",
            "MYSQL_SYNC_DRIVER": "pymysql",
            "MYSQL_ASYNC_DRIVER": "aiomysql",
            "CLOUD_PROVIDER": "aws",
            "RDS_MYSQL_HOST": "mysql_rds_host",
            "SECRETS_MANAGER_DB_CREDENTIALS_KEY": "test_aws_rds_db_keys",
            "S3_MAIN_BUCKET_NAME": "test-bucket",
            "AWS_MAIN_REGION": "us-east-1",
      }
      with patch.dict(os.environ, values=test_env, clear=True):
            app_settings = Settings().get_settings()
            assert app_settings.REDIS_URL == "redis://localhost:6379/0"
            assert app_settings.MYSQL_PORT == "3306"
            assert app_settings.MYSQL_DATABASE == "test_db"
            assert app_settings.MYSQL_SYNC_DRIVER == "pymysql"
            assert app_settings.MYSQL_ASYNC_DRIVER == "aiomysql"
            assert app_settings.CLOUD_PROVIDER == "aws"
            assert app_settings.MYSQL_HOST == "mysql_rds_host"
            assert app_settings.MYSQL_USER == "prod_user"
            assert app_settings.MYSQL_PASSWORD == "prod_password"
            assert app_settings.S3_MAIN_BUCKET_NAME == "test-bucket"
            assert app_settings.AWS_MAIN_REGION == "us-east-1"
            assert app_settings.MAX_MINUTES_STORAGE == 60  
            assert app_settings.MIN_MINUTES_STORAGE == 5  

            mock_aws_secrets.fetch_secret.assert_called_once_with(
                  secret_key="test_aws_rds_db_keys"
            )


# Unhealthy input
def test_missing_required_variables():
    """
    Test that the Settings class raises a ValueError when a required
    environment variable is missing.
    """
    test_env = {
        "ENVIRONMENT": "dev",
        "REDIS_URL": "redis://localhost:6379/0",
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3306",
    }
    
    with patch.dict(os.environ, values=test_env, clear=True):
        # Mock load_dotenv to prevent loading from .env file
        with patch("url_shortener.core.settings.environment.dev.load_dotenv"):
            with pytest.raises(Exception, match="Missing vars:"):
                Settings().get_settings()
      