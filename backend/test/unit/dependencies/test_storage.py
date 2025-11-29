import pytest
from unittest.mock import MagicMock, patch
import os

from url_shortener.dependencies.storage import get_storage_service_dependency


class TestGetStorageServiceDependency:
    """Test the get_storage_service_dependency function."""

    def test_get_storage_service_dependency_aws(self):
        """Test getting storage service dependency with AWS."""
        mock_storage_service = MagicMock()

        with patch("url_shortener.dependencies.storage.get_storage_service", return_value=mock_storage_service):
            result = get_storage_service_dependency()

            assert result == mock_storage_service

    @patch.dict(os.environ, {"CLOUD_PROVIDER": "aws", "S3_MAIN_BUCKET_NAME": "test-bucket"}, clear=False)
    def test_get_storage_service_dependency_integration(self):
        """Test getting storage service dependency integration."""
        result = get_storage_service_dependency()

        # Should return a storage service instance
        assert result is not None
        assert hasattr(result, "get_presigned_url")
        assert hasattr(result, "put_presigned_url")
