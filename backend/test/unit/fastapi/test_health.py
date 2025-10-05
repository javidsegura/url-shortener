from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from url_shortener.main import app
from url_shortener.dependencies import get_db

class TestHealthEndpoint:
      def test_basic(self, 
                        fastapi_client: TestClient,
                        mock_db_override: AsyncMock, 
                        get_mock_redis_client: AsyncMock): # FIX: could we recycle from this as much as possible for integraito ntests? 
            response = fastapi_client.get("/api/health")

            assert response.status_code == 200
            assert str(mock_db_override.execute.call_args.args[0]) == "SELECT 1"
            data = response.json()
            assert data["services"] == {"fastapi": True,
                                        "redis": True,
                                        "db": True}
            get_mock_redis_client.ping.assert_awaited_once()
