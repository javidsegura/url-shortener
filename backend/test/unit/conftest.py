
import pytest 
from unittest.mock import AsyncMock, patch

@pytest.fixture(scope="function")
def get_redis_client():
    REDIS_CLIENT_PATH = "url_shortener.services.shortening.factory.redis_client.get_client"
    
    mock_redis_instance = AsyncMock()
    mock_redis_instance.set = AsyncMock()
    mock_redis_instance.get = AsyncMock(return_value="http://www.faker.com")
    mock_redis_instance.ttl = AsyncMock(return_value=600)
    
    # Patch the get_client method to return our mock
    with patch(REDIS_CLIENT_PATH, new_callable=AsyncMock) as mock_get_client:
        mock_get_client.return_value = mock_redis_instance
        yield mock_redis_instance