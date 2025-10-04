

import pytest 

import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch

# LOADING/UNLOADING CONFIG (i.e., Environmental variables)
def pytest_configure(config):
      """Mock all required environment variables for tests."""

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
      for key, value in test_env.items():
            os.environ[key] = value

def pytest_unconfigure(config):
      """
      This hook runs after the entire test session finishes,
      perfect for cleanup.
      """
      print("\nCleaning up environment variables...")
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
      for key in test_env.keys():
                  del os.environ[key]

@pytest.fixture()
def mock_aws_secrets():
    """Mock AWS Secrets Manager fetch_secret function."""
    return_value = {
        "username": "prod_user",
        "password": "prod_password"
    }
    with patch("url_shortener.core.settings.app_settings.fetch_secret") as mock_fetch_secrets:
        mock_fetch_secrets.return_value = return_value
        yield mock_fetch_secrets