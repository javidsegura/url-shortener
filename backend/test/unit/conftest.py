import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch
from moto import mock_aws
from url_shortener.core.settings import initialize_settings

@pytest.fixture(scope="function")
def get_mock_redis_client():
    REDIS_CLIENT_PATH = "url_shortener.core.clients.redis.RedisClientConnector.get_client"


    mock_redis_instance = AsyncMock()
    mock_redis_instance.set = AsyncMock()
    mock_redis_instance.get = AsyncMock(return_value="http://www.faker.com")
    mock_redis_instance.ttl = AsyncMock(return_value=600)
    mock_redis_instance.ping = AsyncMock(return_value="pong")


    # Patch the initialize_redis_client function
    with patch(REDIS_CLIENT_PATH, return_value=mock_redis_instance) as mock_initializer:
        yield mock_redis_instance

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
            "CLOUD_PROVIDER": "aws",
            "S3_MAIN_BUCKET_NAME": "test-bucket",
            "AWS_MAIN_REGION": "us-east-1",
            "AWS_ACCESS_KEY_ID": "testing",
            "AWS_SECRET_ACCESS_KEY": "testing",
            "AWS_SECURITY_TOKEN": "testing",
            "AWS_SESSION_TOKEN": "testing",
            "AWS_DEFAULT_REGION": "us-east-1",
            "AZURE_STORAGE_ACCOUNT_NAME": "test_storage_acc",
            "AZURE_STORAGE_ACCOUNT_KEY": "test_storage_acc_key",
            "AZURE_STORAGE_CONTAINER_NAME": "test_images_container",
      }
      for key, value in test_env.items():
            os.environ[key] = value
      initialize_settings()


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
            "CLOUD_PROVIDER": "aws",
            "S3_MAIN_BUCKET_NAME": "test-bucket",
            "AWS_MAIN_REGION": "us-east-1",
            "AWS_ACCESS_KEY_ID": "testing",
            "AWS_SECRET_ACCESS_KEY": "testing",
            "AWS_SECURITY_TOKEN": "testing",
            "AWS_SESSION_TOKEN": "testing",
            "AWS_DEFAULT_REGION": "us-east-1",
                        "AZURE_STORAGE_ACCOUNT_NAME": "test_storage_acc",
            "AZURE_STORAGE_ACCOUNT_KEY": "test_storage_acc_key",
            "AZURE_STORAGE_CONTAINER_NAME": "test_images_container",
      }
      for key in test_env.keys():
                  # Safely delete the environment variable
                  if key in os.environ:
                        del os.environ[key]

@pytest.fixture()
def mock_aws_secrets():
    """Mock AWS Secrets Manager fetch_secret function."""
    return_value = {
        "username": "prod_user",
        "password": "prod_password"
    }
    # Mock the secrets service factory to return a mock service
    mock_secrets_service = MagicMock()
    mock_secrets_service.fetch_secret.return_value = return_value
    with patch("url_shortener.services.infra.secrets.get_secrets_service", return_value=mock_secrets_service) as mock_get_secrets:
        yield mock_secrets_service


@pytest.fixture(scope="session", autouse=True)
def mock_aws_session():
    """Start mocking AWS before any imports"""
    with mock_aws():
        yield
