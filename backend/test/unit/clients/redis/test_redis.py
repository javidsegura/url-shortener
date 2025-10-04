import pytest
from unittest.mock import AsyncMock, patch
from url_shortener.core.clients.redis import RedisClientConnector

@pytest.fixture(scope="function")
def get_mock_redis_client():
    """
    Provides a mocked RedisClientConnector instance for testing.

    This fixture creates a mock for the internal _client attribute
    of the RedisClientConnector, allowing us to test the connector's
    logic without a real Redis connection.
    """
    mock_redis_instance = AsyncMock()
    mock_redis_instance.aclose = AsyncMock()
    
    # Patch the redis.asyncio.from_url to return our mock instance
    with patch("redis.asyncio.from_url", return_value=mock_redis_instance):
        connector = RedisClientConnector()
        yield connector

@pytest.mark.asyncio
async def test_connect(get_mock_redis_client):
    """
    Tests that the connect method correctly creates and returns a client.
    """
    connector = get_mock_redis_client
    # Initially, the client should be None
    assert connector._client is None
    
    client = await connector.connect()
    
    # After calling connect, the internal client should not be None
    assert connector._client is not None
    assert connector._client is client
    
    # Calling connect again should return the same instance
    second_client = await connector.connect()
    assert second_client is client

@pytest.mark.asyncio
async def test_get_client(get_mock_redis_client):
    """
    Tests that the get_client method returns the same client instance
    and calls connect if the client doesn't exist.
    """
    connector = get_mock_redis_client
    # The client should not exist initially
    assert connector._client is None
    
    # The first call to get_client should call connect()
    client = await connector.get_client()
    assert connector._client is client
    assert connector._client is not None
    
    # A subsequent call should return the same instance without calling connect() again
    second_client = await connector.get_client()
    assert second_client is client

@pytest.mark.asyncio
async def test_close(get_mock_redis_client):
    """
    Tests that the close method correctly closes the client and resets the instance.
    """
    connector = get_mock_redis_client
    client = await connector.connect()
    
    # Verify the client is active before closing
    assert connector._client is not None
    
    await connector.close()
    
    # After closing, the internal client should be None and aclose should have been called on the mock
    assert connector._client is None
    client.aclose.assert_called_once()
