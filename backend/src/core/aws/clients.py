import boto3
import os

s3_client = boto3.client("s3", region_name=os.getenv("AWS_MAIN_REGION"))
