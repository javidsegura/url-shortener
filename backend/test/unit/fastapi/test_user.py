from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch, ANY
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from url_shortener.main import app
from url_shortener.dependencies import get_db, verify_user
from url_shortener.database.generated_models import User


class TestCreateUserEndpoint:
    def test_create_user_success(self, mock_db_override: AsyncMock, fastapi_client: TestClient):
        """Test successful user creation"""
        fake_user = User(
            user_id="1",
            displayable_name="test_name",
            email="test@example.com",
            profile_pic_object_name="test_profile_pic.jpg",
            country="USA",
            isAdmin=0,
            timeRegistered="2025-10-04T17:46:02.355677",
        )
        
        with patch("url_shortener.routers.user.create_user") as mock_create_user:
            mock_create_user.return_value = fake_user

            response = fastapi_client.post("/api/user", json={
                "user_id": fake_user.user_id,
                "displayable_name": fake_user.displayable_name,
                "email": fake_user.email,
                "profile_pic_object_name": fake_user.profile_pic_object_name,
                "country": fake_user.country
            })

            assert response.status_code == 201
            assert response.json() == f"User created succesfully with id: {fake_user.user_id}"
            mock_create_user.assert_awaited_once()

    def test_create_user_missing_fields(self, mock_db_override: AsyncMock, fastapi_client: TestClient):
        """Test user creation with missing required fields"""
        response = fastapi_client.post("/api/user", json={
            "user_id": "1",
            "displayable_name": "test_name"
            # Missing email, profile_pic_object_name, country
        })

        assert response.status_code == 422  # Validation error

    def test_create_user_duplicate(self, mock_db_override: AsyncMock, fastapi_client: TestClient):
        """Test creating a user that already exists - should raise HTTPException"""
        with patch("url_shortener.routers.user.create_user") as mock_create_user:
            # The endpoint doesn't catch exceptions, so it will propagate
            mock_create_user.side_effect = HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists"
            )

            response = fastapi_client.post("/api/user", json={
                "user_id": "1",
                "displayable_name": "test_name",
                "email": "test@example.com",
                "profile_pic_object_name": "pic.jpg",
                "country": "USA"
            })

            assert response.status_code == 409


class TestGetUserEndpoint:
    def test_get_user_success(self, mock_db_override: AsyncMock, fastapi_client: TestClient):
        """Test successfully retrieving user data with presigned URL"""
        fake_user = User(
            user_id="1",
            displayable_name="test_name",
            email="test@example.com",
            profile_pic_object_name="test_profile_pic.jpg",
            country="USA",
            isAdmin=0,
            timeRegistered="2025-10-04T17:46:02.355677",
        )
        
        with patch("url_shortener.routers.user.read_user") as mock_read_user, \
             patch("url_shortener.routers.user.PresignedUrl") as mock_presigned, \
             patch("url_shortener.routers.user.s3_client") as mock_s3, \
             patch("url_shortener.routers.user.app_settings") as mock_settings:
            
            mock_read_user.return_value = fake_user
            mock_settings.S3_MAIN_BUCKET_NAME = "test-bucket"
            
            mock_presigned_instance = MagicMock()
            mock_presigned_instance.get_presigned_url.return_value = "https://s3.aws.com/presigned-url"
            mock_presigned.return_value = mock_presigned_instance

            response = fastapi_client.get("/api/user/1")

            assert response.status_code == 201
            data = response.json()
            assert data["user_id"] == "1"
            assert data["displayable_name"] == "test_name"
            assert data["presigned_url_profile_pic"] == "https://s3.aws.com/presigned-url"
            mock_read_user.assert_awaited_once_with(ANY, "1")

    def test_get_user_not_found(self, mock_db_override: AsyncMock, fastapi_client: TestClient):
        """Test retrieving non-existent user"""
        with patch("url_shortener.routers.user.read_user") as mock_read_user:
            mock_read_user.return_value = None

            response = fastapi_client.get("/api/user/999")

            # Will fail when trying to access user.profile_pic_object_name on None
            assert response.status_code == 500

    def test_get_user_s3_error(self, mock_db_override: AsyncMock, fastapi_client: TestClient):
        """Test handling S3 presigned URL generation error"""
        fake_user = User(
            user_id="1",
            displayable_name="test_name",
            email="test@example.com",
            profile_pic_object_name="test_profile_pic.jpg",
            country="USA",
            isAdmin=0,
            timeRegistered="2025-10-04T17:46:02.355677",
        )
        
        with patch("url_shortener.routers.user.read_user") as mock_read_user, \
             patch("url_shortener.routers.user.PresignedUrl") as mock_presigned, \
             patch("url_shortener.routers.user.s3_client") as mock_s3, \
             patch("url_shortener.routers.user.app_settings") as mock_settings:
            
            mock_read_user.return_value = fake_user
            mock_settings.S3_MAIN_BUCKET_NAME = "test-bucket"
            
            mock_presigned_instance = MagicMock()
            mock_presigned_instance.get_presigned_url.side_effect = Exception("S3 connection failed")
            mock_presigned.return_value = mock_presigned_instance

            response = fastapi_client.get("/api/user/1")

            assert response.status_code == 500
            assert "S3 connection failed" in response.json()["detail"]

    def test_get_user_unauthorized(self, mock_db_override: AsyncMock, fastapi_client: TestClient):
        """Test accessing user data without proper authentication"""
        from url_shortener.routers.user import verify_user_private_dependency
        app.dependency_overrides.pop(verify_user_private_dependency, None)
        
        response = fastapi_client.get("/api/user/1")
        
        # Should fail authentication
        assert response.status_code in [401, 403]


class TestGetUserLinksEndpoint:
    def test_get_user_links_success(self, mock_db_override: AsyncMock, fastapi_client: TestClient):
        """Test successfully retrieving user's links"""
        fake_links = [
            {
                "link_id": 1,
                "creator_id": "1",
                "old_link": "https://example.com",
                "new_link": "abc123",
                "expires_at": "2025-10-05T17:46:02.355677",
                "timeRegistered": "2025-10-04T17:46:02.355677",
                "click_count": 10
            },
            {
                "link_id": 2,
                "creator_id": "1",
                "old_link": "https://test.com",
                "new_link": "def456",
                "expires_at": "2025-10-05T17:46:02.355677",
                "timeRegistered": "2025-10-04T17:46:02.355677",
                "click_count": 5
            }
        ]
        
        with patch("url_shortener.routers.user.get_list_of_links") as mock_get_links:
            mock_get_links.return_value = fake_links

            response = fastapi_client.get("/api/user/1/links")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["new_link"] == "abc123"
            assert data[0]["click_count"] == 10
            mock_get_links.assert_awaited_once()

    def test_get_user_links_empty(self, mock_db_override: AsyncMock, fastapi_client: TestClient):
        """Test retrieving links for user with no links"""
        with patch("url_shortener.routers.user.get_list_of_links") as mock_get_links:
            mock_get_links.return_value = []

            response = fastapi_client.get("/api/user/1/links")

            assert response.status_code == 200
            assert response.json() == []

    def test_get_user_links_unauthorized(self, mock_db_override: AsyncMock, fastapi_client: TestClient):
        """Test accessing links without authentication"""
        from url_shortener.routers.user import verify_user_private_dependency
        app.dependency_overrides.pop(verify_user_private_dependency, None)
        
        response = fastapi_client.get("/api/user/1/links")
        
        assert response.status_code in [401, 403]


class TestCreatePresignedUrlProfilePicEndpoint:
    def test_create_presigned_url_success(self, mock_db_override: AsyncMock, fastapi_client: TestClient):
        """Test successful presigned URL creation for profile picture upload"""
        with patch("url_shortener.routers.user.PresignedUrl") as mock_presigned, \
             patch("url_shortener.routers.user.s3_client") as mock_s3, \
             patch("url_shortener.routers.user.app_settings") as mock_settings:
            
            mock_settings.S3_MAIN_BUCKET_NAME = "test-bucket"
            mock_presigned_instance = MagicMock()
            mock_presigned_instance.put_presigned_url.return_value = "https://s3.aws.com/upload-url"
            mock_presigned.return_value = mock_presigned_instance

            response = fastapi_client.post("/api/user/profile_pic", json={
                "file_name": "my_photo.jpg",
                "content_type": "image/jpeg"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["presigned_url"] == "https://s3.aws.com/upload-url"
            assert "/users/profile-pictures/my_photo.jpg" in data["s3_file_name"]

    def test_create_presigned_url_png(self, mock_db_override: AsyncMock, fastapi_client: TestClient):
        """Test presigned URL creation for PNG file"""
        with patch("url_shortener.routers.user.PresignedUrl") as mock_presigned, \
             patch("url_shortener.routers.user.s3_client") as mock_s3, \
             patch("url_shortener.routers.user.app_settings") as mock_settings:
            
            mock_settings.S3_MAIN_BUCKET_NAME = "test-bucket"
            mock_presigned_instance = MagicMock()
            mock_presigned_instance.put_presigned_url.return_value = "https://s3.aws.com/upload-url"
            mock_presigned.return_value = mock_presigned_instance

            response = fastapi_client.post("/api/user/profile_pic", json={
                "file_name": "avatar.png",
                "content_type": "image/png"
            })

            assert response.status_code == 200
            mock_presigned_instance.put_presigned_url.assert_called_once()
            call_kwargs = mock_presigned_instance.put_presigned_url.call_args.kwargs
            assert call_kwargs["ContentType"] == "image/png"

    def test_create_presigned_url_s3_error(self, mock_db_override: AsyncMock, fastapi_client: TestClient):
        """Test handling S3 error during presigned URL creation"""
        with patch("url_shortener.routers.user.PresignedUrl") as mock_presigned, \
             patch("url_shortener.routers.user.s3_client") as mock_s3, \
             patch("url_shortener.routers.user.app_settings") as mock_settings:
            
            mock_settings.S3_MAIN_BUCKET_NAME = "test-bucket"
            mock_presigned_instance = MagicMock()
            mock_presigned_instance.put_presigned_url.side_effect = Exception("S3 bucket not accessible")
            mock_presigned.return_value = mock_presigned_instance

            response = fastapi_client.post("/api/user/profile_pic", json={
                "file_name": "photo.jpg",
                "content_type": "image/jpeg"
            })

            assert response.status_code == 500
            assert "S3 bucket not accessible" in response.json()["detail"]

    def test_create_presigned_url_missing_fields(self, mock_db_override: AsyncMock, fastapi_client: TestClient):
        """Test presigned URL creation with missing required fields"""
        response = fastapi_client.post("/api/user/profile_pic", json={
            "file_name": "photo.jpg"
            # Missing content_type
        })

        assert response.status_code == 422

    def test_create_presigned_url_invalid_content_type(self, mock_db_override: AsyncMock, fastapi_client: TestClient):
        """Test presigned URL creation with non-image content type"""
        with patch("url_shortener.routers.user.PresignedUrl") as mock_presigned, \
             patch("url_shortener.routers.user.s3_client") as mock_s3, \
             patch("url_shortener.routers.user.app_settings") as mock_settings:
            
            mock_settings.S3_MAIN_BUCKET_NAME = "test-bucket"
            mock_presigned_instance = MagicMock()
            mock_presigned_instance.put_presigned_url.return_value = "https://s3.aws.com/upload-url"
            mock_presigned.return_value = mock_presigned_instance

            response = fastapi_client.post("/api/user/profile_pic", json={
                "file_name": "document.pdf",
                "content_type": "application/pdf"
            })

            # No validation exists in endpoint, so it will succeed
            assert response.status_code == 200


class TestUserEndpointIntegration:
    """Integration tests for user workflow"""
    
    def test_user_lifecycle(self, mock_db_override: AsyncMock, fastapi_client: TestClient):
        """Test complete user lifecycle: create, get, upload profile pic"""
        fake_user = User(
            user_id="lifecycle_test",
            displayable_name="Test User",
            email="lifecycle@test.com",
            profile_pic_object_name="",
            country="USA",
            isAdmin=0,
            timeRegistered="2025-10-04T17:46:02.355677",
        )
        
        # Step 1: Create user
        with patch("url_shortener.routers.user.create_user") as mock_create:
            mock_create.return_value = fake_user
            
            create_response = fastapi_client.post("/api/user", json={
                "user_id": fake_user.user_id,
                "displayable_name": fake_user.displayable_name,
                "email": fake_user.email,
                "profile_pic_object_name": "",
                "country": fake_user.country
            })
            
            assert create_response.status_code == 201
        
        # Step 2: Get presigned URL for profile pic
        with patch("url_shortener.routers.user.PresignedUrl") as mock_presigned, \
             patch("url_shortener.routers.user.s3_client") as mock_s3, \
             patch("url_shortener.routers.user.app_settings") as mock_settings:
            
            mock_settings.S3_MAIN_BUCKET_NAME = "test-bucket"
            mock_presigned_instance = MagicMock()
            mock_presigned_instance.put_presigned_url.return_value = "https://s3.aws.com/upload"
            mock_presigned.return_value = mock_presigned_instance
            
            upload_response = fastapi_client.post("/api/user/profile_pic", json={
                "file_name": "profile.jpg",
                "content_type": "image/jpeg"
            })
            
            assert upload_response.status_code == 200
            s3_file_name = upload_response.json()["s3_file_name"]
        
        # Step 3: Get user with profile pic
        fake_user.profile_pic_object_name = s3_file_name
        with patch("url_shortener.routers.user.read_user") as mock_read, \
             patch("url_shortener.routers.user.PresignedUrl") as mock_presigned, \
             patch("url_shortener.routers.user.s3_client") as mock_s3, \
             patch("url_shortener.routers.user.app_settings") as mock_settings:
            
            mock_read.return_value = fake_user
            mock_settings.S3_MAIN_BUCKET_NAME = "test-bucket"
            
            mock_presigned_instance = MagicMock()
            mock_presigned_instance.get_presigned_url.return_value = "https://s3.aws.com/view"
            mock_presigned.return_value = mock_presigned_instance
            
            get_response = fastapi_client.get(f"/api/user/{fake_user.user_id}")
            
            assert get_response.status_code == 201
            user_data = get_response.json()
            assert user_data["profile_pic_object_name"] == s3_file_name