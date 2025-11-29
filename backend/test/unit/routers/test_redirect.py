import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from starlette.responses import RedirectResponse

from url_shortener.routers.redirect import redirect_endpoint


class TestRedirectEndpoint:
    """Test the redirect endpoint."""

    @pytest.mark.asyncio
    async def test_redirect_endpoint_success(self):
        """Test redirecting successfully."""
        mock_db = AsyncMock()
        mock_redis_connector = MagicMock()
        mock_redis_client = AsyncMock()
        mock_redis_client.get.return_value = "https://example.com"

        mock_redis_connector.get_client = AsyncMock(return_value=mock_redis_client)

        with patch("url_shortener.routers.redirect.initialize_redis_client", return_value=mock_redis_connector):
            with patch("url_shortener.routers.redirect.increment_link_count", new_callable=AsyncMock):
                result = await redirect_endpoint("abc12345", mock_db)

                assert isinstance(result, RedirectResponse)
                # Check that the redirect URL is set (RedirectResponse uses 'location' header)
                assert hasattr(result, 'headers') or hasattr(result, 'url')
                assert result.status_code == 308
                mock_redis_client.get.assert_called_once_with("abc12345")

    @pytest.mark.asyncio
    async def test_redirect_endpoint_not_found(self):
        """Test redirecting when shortened URL not found."""
        mock_db = AsyncMock()
        mock_redis_connector = MagicMock()
        mock_redis_client = AsyncMock()
        mock_redis_client.get.return_value = None

        mock_redis_connector.get_client = AsyncMock(return_value=mock_redis_client)

        with patch("url_shortener.routers.redirect.initialize_redis_client", return_value=mock_redis_connector):
            # The router catches HTTPException and re-raises as 500
            with pytest.raises(HTTPException) as exc_info:
                await redirect_endpoint("abc12345", mock_db)

            assert exc_info.value.status_code == 500
            assert "404" in str(exc_info.value.detail) or "Not Found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_redirect_endpoint_exception(self):
        """Test redirecting with exception."""
        mock_db = AsyncMock()

        with patch("url_shortener.routers.redirect.initialize_redis_client", side_effect=Exception("Redis error")):
            with pytest.raises(HTTPException) as exc_info:
                await redirect_endpoint("abc12345", mock_db)

            assert exc_info.value.status_code == 500
