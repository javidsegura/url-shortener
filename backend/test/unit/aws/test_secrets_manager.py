from moto import mock_aws
from typing import Dict
import pytest
import json
import boto3
from url_shortener.services.infra.secretsmanager import SecretsManager
from url_shortener.core.clients import secrets_manager_client

@pytest.fixture()
def secretsmanager_setup():
      # Create test secret 
      secret_name = "my-test-secret"
      secret_value = {"api_key": "12345"}     
      secrets_manager_client.create_secret(
            Name=secret_name,
            SecretString=json.dumps(secret_value)
      )
      yield secret_name, secret_value

@pytest.fixture()
def secretsmanager_binary_setup():
      secret_name = "my-binary-secret"
      secret_value = b'{"api_key": "67890"}'
      secrets_manager_client.create_secret(
            Name=secret_name,
            SecretBinary=secret_value
      )
      yield secret_name

class TestSecrestManagerHealthyInput:
      def test_secret_fetching(self, secretsmanager_setup):
            secret_name, secret_value = secretsmanager_setup
            print(f"Secret name: {secret_name} with type: {type(secret_name)}")
            secrets_manager = SecretsManager()
            fetched_secret = secrets_manager.fetch_secret(secret_name)
            print(f"Fetched secret: {fetched_secret}")
            assert fetched_secret == secret_value     
            


class TestSecrestManagerUnhealthyInput:
      def test_secret_fetching(self, secretsmanager_binary_setup):
            secret_name = secretsmanager_binary_setup
            secrets_manager = SecretsManager()
            with pytest.raises(ValueError, match=f"Secret {secret_name} doesnt have a Secret string"):
                  secrets_manager.fetch_secret(secret_key=secret_name)

