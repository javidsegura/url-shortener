
import pytest 
from unittest.mock import AsyncMock, patch

@pytest.fixture(scope="session")
def get_redis_client():
      REDIS_CLIENT_PATH = "url_shortener.core.clients.redis_client.redis_client"
      with patch(REDIS_CLIENT_PATH, new_callable=AsyncMock) as mock_redis_client:
            mock_redis = AsyncMock()
            mock_redis.get_client.return_value = mock_redis
            yield mock_redis
