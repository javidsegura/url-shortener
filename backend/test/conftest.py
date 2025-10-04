

import pytest 

import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch


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
            "SHORTENED_URL_LENGTH": "8",
            "MAX_MINUTES_STORAGE": "120",
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
            "SHORTENED_URL_LENGTH": "8",
            "MAX_MINUTES_STORAGE": "120",
      }
      for key in test_env.keys():
                  del os.environ[key]


@pytest.fixture(scope="session", autouse=True)
def mock_database():
      ...
#     db_path = "url_shortener.database.main"
    
#     # Create a mock session factory
#     mock_session = AsyncMock(spec=AsyncSession)
#     mock_sessionmaker = MagicMock(return_value=mock_session)
    
#     # Patch the global AsyncSessionLocal directly
#     with patch(f"{db_path}.AsyncSessionLocal", mock_sessionmaker):
#         yield mock_sessionmaker

@pytest.fixture()
async def mock_db_session():
      session = AsyncMock()
      session.commit = AsyncMock()
      session.rollback = AsyncMock()
      session.close = AsyncMock()
      session.execute = AsyncMock()
      session.add = MagicMock()
      session.delete = AsyncMock()
      session.refresh = AsyncMock()

      return session



@pytest.fixture
def mock_aws_secrets(scope="session"):
    """Mock AWS Secrets Manager fetch_secret function."""
    return_value = {
            "username": "prod_user",
            "password": "prod_password"
      }
    with patch("url_shortener.core.clients.aws.fetch_secret", return_value=return_value) as mock_fetch:
        yield 

