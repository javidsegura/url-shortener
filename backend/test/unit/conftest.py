import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture(scope="function")
def get_mock_redis_client():
    REDIS_CLIENT_PATH = "url_shortener.core.clients.redis.RedisClientConnector.get_client"
    
    
    mock_redis_instance = AsyncMock()
    mock_redis_instance.set = AsyncMock()
    mock_redis_instance.get = AsyncMock(return_value="http://www.faker.com")
    mock_redis_instance.ttl = AsyncMock(return_value=600)
    mock_redis_instance.ping = AsyncMock(return_value="pong")


    # Patch the initialize_redis_client function
    with patch(REDIS_CLIENT_PATH, return_value=mock_redis_instance) as mock_initializer:
        yield mock_redis_instance