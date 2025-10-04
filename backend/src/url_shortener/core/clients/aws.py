from typing import Dict
import boto3
import os
import json

s3_client = boto3.client("s3", region_name=os.getenv("AWS_MAIN_REGION"))
secrets_manager_client = boto3.client("secretsmanager", region_name=os.getenv("AWS_MAIN_REGION"))

def fetch_secret(secret_key: str) -> Dict:
      get_secret_value_response = secrets_manager_client.get_secret_value(
            SecretId=secret_key
      )

      if "SecretString" in get_secret_value_response:
            secret_value = get_secret_value_response["SecretString"]
            try:
                  parsed_secret = json.loads(secret_value)
                  return parsed_secret
            except json.JSONDecodeError:
                  return secret_value
      return None





