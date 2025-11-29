import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from fastapi import HTTPException

from url_shortener.routers.user import (
    create_user_endpoint,
    get_user_endpoint,
    patch_user_endpoint,
    delete_user_endpoint,
    get_user_links_endpoints,
    create_presigned_url_profile_pic_endpoint,
)
from url_shortener.schemas.endpoints import CreateUserRequest, ModifyUserNameRequest, UploadProfilePicRequest
from url_shortener.database.generated_models import User, Link


class TestCreateUserEndpoint:
    """Test the create user endpoint."""

    @pytest.mark.asyncio
    async def test_create_user_endpoint_success(self):
        """Test creating a user successfully."""
        mock_db = AsyncMock()
        user_data = CreateUserRequest(
            user_id="user123",
            displayable_name="Test User",
            email="test@example.com",
            profile_pic_object_name="pic.jpg",
            country="US"
        )

        result = await create_user_endpoint(user_data, mock_db)

        assert "User created succesfully" in result
        assert "user123" in result
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


class TestGetUserEndpoint:
    """Test the get user endpoint."""

    @pytest.mark.asyncio
    async def test_get_user_endpoint_success(self):
        """Test getting a user successfully."""
        mock_db = AsyncMock()
        mock_storage_service = MagicMock()
        mock_storage_service.get_presigned_url.return_value = "https://presigned-url.com/pic.jpg"

        mock_user = User(
            user_id="user123",
            displayable_name="Test User",
            email="test@example.com",
            timeRegistered=datetime.now(),
            profile_pic_object_name="pic.jpg",
            country="US",
            isAdmin=0
        )

        with patch("url_shortener.routers.user.read_user", return_value=mock_user):
            result = await get_user_endpoint("user123", mock_db, mock_storage_service)

            assert result.user_id == "user123"
            assert result.presigned_url_profile_pic == "https://presigned-url.com/pic.jpg"
            mock_storage_service.get_presigned_url.assert_called_once_with(file_path="pic.jpg")

    @pytest.mark.asyncio
    async def test_get_user_endpoint_value_error(self):
        """Test getting a user with ValueError."""
        mock_db = AsyncMock()
        mock_storage_service = MagicMock()
        mock_storage_service.get_presigned_url.side_effect = ValueError("Object not found")

        mock_user = User(
            user_id="user123",
            displayable_name="Test User",
            email="test@example.com",
            timeRegistered=datetime.now(),
            profile_pic_object_name="pic.jpg",
            country="US",
            isAdmin=0
        )

        with patch("url_shortener.routers.user.read_user", return_value=mock_user):
            with pytest.raises(HTTPException) as exc_info:
                await get_user_endpoint("user123", mock_db, mock_storage_service)

            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_user_endpoint_generic_error(self):
        """Test getting a user with generic error."""
        mock_db = AsyncMock()
        mock_storage_service = MagicMock()
        mock_storage_service.get_presigned_url.side_effect = Exception("Storage error")

        mock_user = User(
            user_id="user123",
            displayable_name="Test User",
            email="test@example.com",
            timeRegistered=datetime.now(),
            profile_pic_object_name="pic.jpg",
            country="US",
            isAdmin=0
        )

        with patch("url_shortener.routers.user.read_user", return_value=mock_user):
            with pytest.raises(HTTPException) as exc_info:
                await get_user_endpoint("user123", mock_db, mock_storage_service)

            assert exc_info.value.status_code == 500


class TestPatchUserEndpoint:
    """Test the patch user endpoint."""

    @pytest.mark.asyncio
    async def test_patch_user_endpoint_success(self):
        """Test patching a user successfully."""
        mock_db = AsyncMock()
        mock_current_user = {"uid": "user123"}
        request = ModifyUserNameRequest(new_name="New Name")

        with patch("url_shortener.routers.user.edit_user_name", return_value=MagicMock()):
            result = await patch_user_endpoint("user123", request, mock_db, mock_current_user)

            assert "edited successfully" in result

    @pytest.mark.asyncio
    async def test_patch_user_endpoint_not_found(self):
        """Test patching a user that doesn't exist."""
        mock_db = AsyncMock()
        mock_current_user = {"uid": "user123"}
        request = ModifyUserNameRequest(new_name="New Name")

        with patch("url_shortener.routers.user.edit_user_name", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await patch_user_endpoint("user123", request, mock_db, mock_current_user)

            assert exc_info.value.status_code == 404


class TestDeleteUserEndpoint:
    """Test the delete user endpoint."""

    @pytest.mark.asyncio
    async def test_delete_user_endpoint_success(self):
        """Test deleting a user successfully."""
        mock_db = AsyncMock()
        mock_current_user = {"uid": "user123"}

        with patch("url_shortener.routers.user.delete_user", return_value=True):
            result = await delete_user_endpoint("user123", mock_db, mock_current_user)

            assert "deleted successfully" in result

    @pytest.mark.asyncio
    async def test_delete_user_endpoint_not_found(self):
        """Test deleting a user that doesn't exist."""
        mock_db = AsyncMock()
        mock_current_user = {"uid": "user123"}

        with patch("url_shortener.routers.user.delete_user", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await delete_user_endpoint("user123", mock_db, mock_current_user)

            assert exc_info.value.status_code == 404


class TestGetUserLinksEndpoint:
    """Test the get user links endpoint."""

    @pytest.mark.asyncio
    async def test_get_user_links_endpoint_success(self):
        """Test getting user links successfully."""
        mock_db = AsyncMock()
        mock_current_user = {"uid": "user123"}

        mock_links = [
            Link(
                link_id=1,
                creator_id="user123",
                old_link="https://example.com",
                new_link="abc123",
                expires_at=datetime.now(),
                timeRegistered=datetime.now(),
                click_count=0
            )
        ]

        with patch("url_shortener.routers.user.get_list_of_links", return_value=mock_links):
            result = await get_user_links_endpoints("user123", mock_db, mock_current_user)

            assert len(result) == 1
            assert result[0].creator_id == "user123"


class TestCreatePresignedUrlProfilePicEndpoint:
    """Test the create presigned URL for profile pic endpoint."""

    @pytest.mark.asyncio
    async def test_create_presigned_url_success(self):
        """Test creating presigned URL successfully."""
        mock_storage_service = MagicMock()
        mock_storage_service.put_presigned_url.return_value = "https://presigned-url.com/upload"

        request = UploadProfilePicRequest(
            file_name="profile.jpg",
            content_type="image/jpeg"
        )

        result = await create_presigned_url_profile_pic_endpoint(request, mock_storage_service)

        assert "presigned_url" in result
        assert result["presigned_url"] == "https://presigned-url.com/upload"
        assert "file_path" in result
        assert "users/profile-pictures/profile.jpg" in result["file_path"]

    @pytest.mark.asyncio
    async def test_create_presigned_url_error(self):
        """Test creating presigned URL with error."""
        mock_storage_service = MagicMock()
        mock_storage_service.put_presigned_url.side_effect = Exception("Storage error")

        request = UploadProfilePicRequest(
            file_name="profile.jpg",
            content_type="image/jpeg"
        )

        with pytest.raises(HTTPException) as exc_info:
            await create_presigned_url_profile_pic_endpoint(request, mock_storage_service)

        assert exc_info.value.status_code == 500
