from typing import Dict
import boto3
import os
import json

s3_client = boto3.client("s3", region_name=os.getenv("AWS_MAIN_REGION")) # FIX: are these multi-threading safe?
secrets_manager_client = boto3.client("secretsmanager", region_name=os.getenv("AWS_MAIN_REGION"))







