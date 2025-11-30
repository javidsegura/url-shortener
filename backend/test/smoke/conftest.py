import os
from moto import mock_aws
from url_shortener.core.logger import initialize_logger
import pytest
from url_shortener.core.clients import initialize_aws_s3_client, initialize_aws_secrets_manager_client
import json

initialize_logger()

@pytest.fixture(scope="session", autouse=True)
def mock_aws_session():
    """Start mocking AWS before any imports"""
    with mock_aws():
        yield

@pytest.fixture(scope="session", autouse=True)
def s3_setup():
    """Setup mock S3 environment"""
    bucket_name = os.getenv("S3_MAIN_BUCKET_NAME", "test-bucket")
    s3_client = initialize_aws_s3_client()
    s3_client.create_bucket(Bucket=bucket_name)

    yield bucket_name

@pytest.fixture(scope="session", autouse=True)
def secretsmanager_setup():
      # Create test secret
      secret_name = "my-test-secret"
      secret_value = {"api_key": "12345"}
      secrets_manager_client = initialize_aws_secrets_manager_client()
      secrets_manager_client.create_secret(
            Name=secret_name,
            SecretString=json.dumps(secret_value)
      )
      yield secret_name, secret_value
