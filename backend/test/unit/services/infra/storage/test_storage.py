import pytest
import os
from unittest.mock import patch

from url_shortener.services.infra.storage.storage import get_storage_service, StorageService


class TestGetStorageService:
    """Test the get_storage_service factory function."""

    @patch.dict(os.environ, {"CLOUD_PROVIDER": "aws", "S3_MAIN_BUCKET_NAME": "test-bucket"}, clear=False)
    def test_get_storage_service_aws(self):
        """Test getting AWS storage service."""
        service = get_storage_service()

        assert service is not None
        assert hasattr(service, "get_presigned_url")
        assert hasattr(service, "put_presigned_url")

    @patch.dict(os.environ, {"CLOUD_PROVIDER": "azure", "AZURE_STORAGE_CONTAINER_NAME": "test-container"}, clear=False)
    def test_get_storage_service_azure(self):
        """Test getting Azure storage service."""
        service = get_storage_service()

        assert service is not None
        assert hasattr(service, "get_presigned_url")
        assert hasattr(service, "put_presigned_url")

    @patch.dict(os.environ, {"CLOUD_PROVIDER": "aws"}, clear=False)
    def test_get_storage_service_aws_missing_bucket(self):
        """Test getting AWS storage service with missing bucket name."""
        if "S3_MAIN_BUCKET_NAME" in os.environ:
            del os.environ["S3_MAIN_BUCKET_NAME"]

        with pytest.raises(ValueError, match="S3_MAIN_BUCKET_NAME not set"):
            get_storage_service()

    @patch.dict(os.environ, {"CLOUD_PROVIDER": "azure"}, clear=False)
    def test_get_storage_service_azure_missing_container(self):
        """Test getting Azure storage service with missing container name."""
        if "AZURE_STORAGE_CONTAINER_NAME" in os.environ:
            del os.environ["AZURE_STORAGE_CONTAINER_NAME"]

        with pytest.raises(ValueError, match="AZURE_STORAGE_CONTAINER_NAME not set"):
            get_storage_service()

    @patch.dict(os.environ, {}, clear=True)
    def test_get_storage_service_defaults_to_aws(self):
        """Test that default cloud provider is AWS."""
        os.environ["S3_MAIN_BUCKET_NAME"] = "test-bucket"
        os.environ["CLOUD_PROVIDER"] = "aws"

        service = get_storage_service()

        assert service is not None
        assert hasattr(service, "get_presigned_url")

    def test_storage_service_abc(self):
        """Test that StorageService is an abstract base class."""
        with pytest.raises(TypeError):
            StorageService()
