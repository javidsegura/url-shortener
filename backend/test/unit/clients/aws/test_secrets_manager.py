from moto import mock_aws
from typing import Dict
import pytest
import json
import boto3
from url_shortener.services.infra.secrets.aws import AWSSecretsManager
from url_shortener.core.clients.aws import initialize_aws_secrets_manager_client

@pytest.fixture()
def secretsmanager_setup():
      # Create test secret 
      secret_name = "my-test-secret"
      secret_value = {"api_key": "12345"}
      client = initialize_aws_secrets_manager_client()
      client.create_secret(
            Name=secret_name,
            SecretString=json.dumps(secret_value)
      )
      yield secret_name, secret_value

@pytest.fixture()
def secretsmanager_binary_setup():
      secret_name = "my-binary-secret"
      secret_value = b'{"api_key": "67890"}'
      client = initialize_aws_secrets_manager_client()
      client.create_secret(
            Name=secret_name,
            SecretBinary=secret_value
      )
      yield secret_name

class TestSecrestManagerHealthyInput:
      def test_secret_fetching(self, secretsmanager_setup):
            secret_name, secret_value = secretsmanager_setup
            print(f"Secret name: {secret_name} with type: {type(secret_name)}")
            # Use AWS region from environment or default
            import os
            region_name = os.getenv("AWS_MAIN_REGION", "us-east-1")
            secrets_manager = AWSSecretsManager(region_name=region_name)
            fetched_secret = secrets_manager.fetch_secret(secret_key=secret_name)
            print(f"Fetched secret: {fetched_secret}")
            assert fetched_secret == secret_value     
            


class TestSecrestManagerUnhealthyInput:
      def test_secret_fetching(self, secretsmanager_binary_setup):
            secret_name = secretsmanager_binary_setup
            # Use AWS region from environment or default
            import os
            region_name = os.getenv("AWS_MAIN_REGION", "us-east-1")
            secrets_manager = AWSSecretsManager(region_name=region_name)
            with pytest.raises(ValueError, match=f"Secret {secret_name} doesn't have a Secret string"):
                  secrets_manager.fetch_secret(secret_key=secret_name)

