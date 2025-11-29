import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from url_shortener.routers.health import (
    cheeck_backend_health_dependencies_endpoint,
    cheeck_backend_health_endpoint,
)


class TestHealthPingEndpoint:
    """Test the /health/ping endpoint."""

    @pytest.mark.asyncio
    async def test_ping_endpoint_success(self):
        """Test that ping endpoint returns pong."""
        mock_settings = MagicMock()
        result = await cheeck_backend_health_endpoint(mock_settings)

        assert isinstance(result, dict)


class TestHealthDependenciesEndpoint:
    """Test the /health/dependencies endpoint."""

    @pytest.mark.asyncio
    async def test_dependencies_endpoint_healthy(self):
        """Test dependencies endpoint when all services are healthy."""
        mock_db = AsyncMock()

        with patch("url_shortener.routers.health.test_redis_connection", return_value=True):
            result = await cheeck_backend_health_dependencies_endpoint(mock_db)

            assert result["status"] == "healthy"
            assert result["checks"]["redis"] == "ok"

    @pytest.mark.asyncio
    async def test_dependencies_endpoint_unhealthy_redis(self):
        """Test dependencies endpoint when Redis is unhealthy."""
        mock_db = AsyncMock()

        with patch("url_shortener.routers.health.test_redis_connection", side_effect=Exception("Redis connection failed")):
            from fastapi import HTTPException

            with pytest.raises(HTTPException) as exc_info:
                await cheeck_backend_health_dependencies_endpoint(mock_db)

            assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            assert exc_info.value.detail["status"] == "unhealthy"
            assert "failed" in exc_info.value.detail["checks"]["redis"]

    @pytest.mark.asyncio
    async def test_dependencies_endpoint_redis_false(self):
        """Test dependencies endpoint when Redis returns False."""
        mock_db = AsyncMock()

        with patch("url_shortener.routers.health.test_redis_connection", return_value=False):
            from fastapi import HTTPException

            with pytest.raises(HTTPException) as exc_info:
                await cheeck_backend_health_dependencies_endpoint(mock_db)

            assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            assert exc_info.value.detail["status"] == "unhealthy"
