import os
from unittest.mock import patch
import pytest
from url_shortener.core.settings.app_settings import Settings

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
            "S3_MAIN_BUCKET_NAME": "test-bucket",
      }
      with patch.dict(os.environ, values=test_env, clear=True):
            app_settings = Settings()
            
            assert app_settings.ENVIRONMENT == "dev"
            assert app_settings.REDIS_URL == "redis://localhost:6379/0"
            assert app_settings.MYSQL_HOST == "localhost"
            assert app_settings.MYSQL_PORT == "3306"
            assert app_settings.MYSQL_DATABASE == "test_db"
            assert app_settings.MYSQL_USER == "test_user"
            assert app_settings.MYSQL_PASSWORD == "test_password"
            assert app_settings.MYSQL_SYNC_DRIVER == "pymysql"
            assert app_settings.MYSQL_ASYNC_DRIVER == "aiomysql"
            assert app_settings.S3_MAIN_BUCKET_NAME == "test-bucket"
            assert app_settings.SHORTENED_URL_LENGTH == 8  
            assert app_settings.MAX_MINUTES_STORAGE == 60  
            assert app_settings.MIN_MINUTES_STORAGE == 5 

def test_settings_extract_prod(mock_aws_secrets):
      test_env = {
            "ENVIRONMENT": "prod",
            "REDIS_URL": "redis://localhost:6379/0",
            "MYSQL_PORT": "3306",
            "MYSQL_DATABASE": "test_db",
            "MYSQL_SYNC_DRIVER": "pymysql",
            "MYSQL_ASYNC_DRIVER": "aiomysql",
            "RDS_MYSQL_HOST": "mysql_rds_host",
            "SECRETS_MANAGER_DB_CREDENTIALS_KEY": "test_aws_rds_db_keys",
            "S3_MAIN_BUCKET_NAME": "test-bucket",
      }
      with patch.dict(os.environ, values=test_env, clear=True):
            app_settings = Settings()
            assert app_settings.ENVIRONMENT == "prod"
            assert app_settings.REDIS_URL == "redis://localhost:6379/0"
            assert app_settings.MYSQL_PORT == "3306"
            assert app_settings.MYSQL_DATABASE == "test_db"
            assert app_settings.MYSQL_SYNC_DRIVER == "pymysql"
            assert app_settings.MYSQL_ASYNC_DRIVER == "aiomysql"
            assert app_settings.MYSQL_HOST == "mysql_rds_host"
            assert app_settings.MYSQL_USER ==  mock_aws_secrets.return_value["username"]
            assert app_settings.MYSQL_PASSWORD == mock_aws_secrets.return_value["password"]
            assert app_settings.S3_MAIN_BUCKET_NAME == "test-bucket"
            assert app_settings.MAX_MINUTES_STORAGE == 60  
            assert app_settings.MIN_MINUTES_STORAGE == 5  

            mock_aws_secrets.assert_called_once_with(
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
        with pytest.raises(ValueError, match="Missing required environment variables: MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_SYNC_DRIVER, MYSQL_ASYNC_DRIVER, S3_MAIN_BUCKET_NAME"):
            Settings()
      