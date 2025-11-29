import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from url_shortener.routers.links import shortern_link
from url_shortener.schemas.endpoints import URLShorteningRequest
from url_shortener.core.settings.app_settings import Settings


class TestShortenLinkEndpoint:
    """Test the shorten link endpoint."""

    @pytest.mark.asyncio
    async def test_shorten_link_success(self):
        """Test shortening a link successfully."""
        mock_current_user = {"uid": "user123"}
        mock_db = AsyncMock()
        mock_settings = MagicMock(spec=Settings)
        mock_settings.MAX_MINUTES_STORAGE = 60
        mock_settings.SHORTENED_URL_LENGTH = 8

        request = URLShorteningRequest(
            original_url="https://example.com",
            expires_in_min=30
        )

        mock_creator = AsyncMock()
        mock_creator.shorten_url.return_value = "abc12345"

        with patch("url_shortener.routers.links.RandomStringCreator", return_value=mock_creator):
            with patch("url_shortener.routers.links.create_link", new_callable=AsyncMock):
                result = await shortern_link(
                    mock_current_user,
                    mock_db,
                    mock_settings,
                    request
                )

                assert "shortened_url" in result
                assert result["shortened_url"] == "abc12345"
                mock_creator.shorten_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_shorten_link_expiration_exceeds_maximum(self):
        """Test shortening a link with expiration exceeding maximum."""
        mock_current_user = {"uid": "user123"}
        mock_db = AsyncMock()
        mock_settings = MagicMock(spec=Settings)
        mock_settings.MAX_MINUTES_STORAGE = 60
        mock_settings.SHORTENED_URL_LENGTH = 8

        request = URLShorteningRequest(
            original_url="https://example.com",
            expires_in_min=120  # Exceeds maximum
        )

        # The router catches HTTPException and re-raises as 500
        with pytest.raises(HTTPException) as exc_info:
            await shortern_link(
                mock_current_user,
                mock_db,
                mock_settings,
                request
            )

        assert exc_info.value.status_code == 500
        assert "exceeds maximum" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_shorten_link_exception(self):
        """Test shortening a link with exception."""
        mock_current_user = {"uid": "user123"}
        mock_db = AsyncMock()
        mock_settings = MagicMock(spec=Settings)
        mock_settings.MAX_MINUTES_STORAGE = 60
        mock_settings.SHORTENED_URL_LENGTH = 8

        request = URLShorteningRequest(
            original_url="https://example.com",
            expires_in_min=30
        )

        mock_creator = AsyncMock()
        mock_creator.shorten_url.side_effect = Exception("Shortening failed")

        with patch("url_shortener.routers.links.RandomStringCreator", return_value=mock_creator):
            with pytest.raises(HTTPException) as exc_info:
                await shortern_link(
                    mock_current_user,
                    mock_db,
                    mock_settings,
                    request
                )

            assert exc_info.value.status_code == 500
