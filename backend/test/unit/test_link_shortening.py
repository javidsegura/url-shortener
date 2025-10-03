import pytest

from url_shortener.services.shortening import RandomStringCreator
from unittest.mock import AsyncMock, patch

REDIS_CLIENT_PATH = "url_shortener.core.clients.redis_client"

@pytest.mark.asyncio
async def check_random_string(get_redis_client):
    max_length = 8
    fake_url = "http://www.faker.com"
    minutes_until_expiration = 10
    creator = RandomStringCreator(max_length=max_length)
    shortened_url = await creator.shorten_url(
                                    original_url=fake_url,
                                    minutes_until_expiration=minutes_until_expiration
    )

    assert len(shortened_url) < max_length



