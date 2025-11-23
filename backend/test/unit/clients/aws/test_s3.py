import time
import pytest
import boto3
from urllib.parse import urlparse, parse_qs
import requests

from url_shortener.core.clients.aws import initialize_aws_s3_client
from url_shortener.services.infra.storage.aws import AWSS3Storage, PresignedUrlActionsType


@pytest.fixture
def s3_setup():
    """Setup mock S3 environment"""
    bucket_name = "test-bucket"
    client = initialize_aws_s3_client()
    client.create_bucket(Bucket=bucket_name)
    
    yield bucket_name, client


class TestPresignedUrlHealthyInput:
    
    def test_get_presigned_url_generation(self, s3_setup):
        """Test that GET presigned URL is generated correctly"""
        bucket_name, s3_client = s3_setup
        presigned_url_service = AWSS3Storage(bucket_name)
        
        key = "test-file.txt"
        expiration = 1800
        
        # Create object first for GET operation
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=b"test content")
        
        url = presigned_url_service.get_presigned_url(
            file_path=key,
            expiration_time_secs=expiration
        )
        
        # Verify URL is generated
        assert url is not None
        assert isinstance(url, str)
        assert bucket_name in url
        assert key in url
        
        # Parse URL and verify parameters
        parsed = urlparse(url)
        assert parsed.scheme in ["http", "https"]

    
    def test_put_presigned_url_generation(self, s3_setup):
        """Test that PUT presigned URL is generated correctly"""
        bucket_name, s3_client = s3_setup
        presigned_url_service = AWSS3Storage(bucket_name)
        
        key = "upload-file.txt"
        
        url = presigned_url_service.put_presigned_url(
            file_path=key
        )
        
        assert url is not None
        assert isinstance(url, str)
        assert bucket_name in url
        assert key in url

        # Parse URL and verify parameters
        parsed = urlparse(url)
        assert parsed.scheme in ["http", "https"]
    
    def test_presigned_url_with_custom_expiration(self, s3_setup):
        """Test presigned URL with custom expiration time"""
        bucket_name, s3_client = s3_setup
        presigned_url_service = AWSS3Storage(bucket_name)
        
        key = "test-file.txt"
        custom_expiration_secs = 7200
        
        # Create object first for GET operation
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=b"test content")
        
        url = presigned_url_service.get_presigned_url(
            file_path=key,
            expiration_time_secs=custom_expiration_secs
        )
        
        # Parse URL and check expiration
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        resolve_time_difference(query_params, custom_time_secs=custom_expiration_secs)
    
    def test_presigned_url_with_additional_params(self, s3_setup):
        """Test presigned URL with additional S3 parameters"""
        bucket_name, s3_client = s3_setup
        presigned_url_service = AWSS3Storage(bucket_name)
        
        key = "test-file.txt"
        
        # Create object first for GET operation
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=b"test content")
        
        url = presigned_url_service.get_presigned_url(
            file_path=key,
            ResponseContentType="application/json",
            ResponseContentDisposition="attachment; filename=download.json"
        )
        
        assert url is not None
        assert "response-content-type" in url.lower()
    
    def test_put_presigned_url_upload(self, s3_setup):
        """Test actual file upload using PUT presigned URL"""
        bucket_name, s3_client = s3_setup
        presigned_url_service = AWSS3Storage(bucket_name)
        
        key = "uploaded-file.txt"
        content = b"Test file content"
        
        # Generate PUT presigned URL
        url = presigned_url_service.put_presigned_url(
            file_path=key
        )
        
        # Upload file using the presigned URL
        response = requests.put(url, data=content)
        assert response.status_code == 200
        
        # Verify file was uploaded
        obj = s3_client.get_object(Bucket=bucket_name, Key=key)
        assert obj["Body"].read() == content
    
    def test_get_presigned_url_download(self, s3_setup):
        """Test actual file download using GET presigned URL"""
        bucket_name, s3_client = s3_setup
        presigned_url_service = AWSS3Storage(bucket_name)
        
        key = "download-file.txt"
        content = b"Download me!"
        
        # Upload file first
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=content)
        
        # Generate GET presigned URL
        url = presigned_url_service.get_presigned_url(
            file_path=key
        )
        
        # Download file using the presigned URL
        response = requests.get(url)
        assert response.status_code == 200
        assert response.content == content
    
    def test_default_expiration(self, s3_setup):
        """Test that default expiration is 3600 seconds"""
        bucket_name, s3_client = s3_setup
        presigned_url_service = AWSS3Storage(bucket_name)
        
        key = "test-file.txt"
        
        # Create object first for GET operation
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=b"test content")
        
        url = presigned_url_service.get_presigned_url(
            file_path=key
        )
        
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        resolve_time_difference(query_params, custom_time_secs=3600)

def resolve_time_difference(query_params, custom_time_secs: int):
        current_time = int(time.time())
        expected_expires = current_time + custom_time_secs
        
        actual_expires = int(query_params["Expires"][0])
        
        assert expected_expires - 5 <= actual_expires <= expected_expires + 5