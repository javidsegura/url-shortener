import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import FastAPI

from url_shortener.main import app, lifespan


class TestMainApp:
    """Test the main FastAPI application."""

    def test_app_initialization(self):
        """Test that the app is properly initialized."""
        assert app is not None
        assert isinstance(app, FastAPI)
        assert app.title == "URL shortener"

    def test_app_has_cors_middleware(self):
        """Test that CORS middleware is configured."""
        middleware_classes = [middleware.cls.__name__ for middleware in app.user_middleware]
        assert "CORSMiddleware" in middleware_classes

    def test_app_has_routers(self):
        """Test that routers are included."""
        route_paths = [route.path for route in app.routes]

        # Check for health router
        assert any("/health" in path for path in route_paths)
        # Check for link router
        assert any("/link" in path for path in route_paths)
        # Check for user router
        assert any("/user" in path for path in route_paths)
        # Check for redirect router
        assert any("/short" in path for path in route_paths)


class TestLifespan:
    """Test the lifespan context manager."""

    @pytest.mark.asyncio
    async def test_lifespan_startup(self):
        """Test lifespan startup initialization."""
        mock_app = MagicMock()

        with patch("url_shortener.main.initialize_firebase") as mock_firebase:
            with patch("url_shortener.main.initialize_logger") as mock_logger:
                with patch("url_shortener.main.settings") as mock_settings_module:
                    mock_settings_module.app_settings = MagicMock()
                    mock_settings_module.initialize_settings.return_value = MagicMock()
                    with patch("url_shortener.main.clients") as mock_clients_module:
                        mock_clients_module.redis = None
                        mock_clients_module.initialize_redis_client.return_value = MagicMock()
                        async with lifespan(mock_app):
                            mock_firebase.assert_called_once()
                            mock_logger.assert_called_once()
                            mock_settings_module.initialize_settings.assert_called_once()
                            mock_clients_module.initialize_redis_client.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_shutdown(self):
        """Test lifespan shutdown cleanup."""
        mock_app = MagicMock()

        with patch("url_shortener.main.initialize_firebase"):
            with patch("url_shortener.main.initialize_logger"):
                with patch("url_shortener.main.settings") as mock_settings_module:
                    mock_settings_module.app_settings = MagicMock()
                    mock_settings_module.initialize_settings.return_value = MagicMock()
                    with patch("url_shortener.main.clients") as mock_clients_module:
                        mock_clients_module.redis = None
                        mock_clients_module.initialize_redis_client.return_value = MagicMock()
                        with patch("url_shortener.main.logger") as mock_logger_module:
                            async with lifespan(mock_app):
                                pass

                            # The lifespan context manager should complete without errors
                            # Shutdown logging is done via logger.debug
