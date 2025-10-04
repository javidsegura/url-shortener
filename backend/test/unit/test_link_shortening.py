import string
import secrets 
from unittest.mock import AsyncMock
import pytest

from url_shortener.services.shortening import BaseCreator, RandomStringCreator, EncryptedStringCreator, CounterEncodedStringCreator

# Sanitized input
@pytest.mark.asyncio
@pytest.mark.parametrize("creator_class", [
    RandomStringCreator,
    EncryptedStringCreator,
    CounterEncodedStringCreator
])
async def test_string_creator_healthy_input(get_redis_client: AsyncMock, creator_class: BaseCreator):

    max_length = 8
    fake_url = "http://www.faker.com"
    minutes_until_expiration = 10
    creator = creator_class(max_length=max_length)
    shortened_url = await creator.shorten_url(
                                    original_url=fake_url,
                                    minutes_until_expiration=minutes_until_expiration
    )

    expected_chars = string.ascii_letters + string.digits
    for char in shortened_url:
        assert char in expected_chars
    assert len(shortened_url) <= max_length
    get_redis_client.set.assert_awaited_once_with(
        name=shortened_url,
        value=fake_url,
        ex=minutes_until_expiration * 60
    )


# Unhealthy input
@pytest.mark.asyncio
@pytest.mark.parametrize("creator_class", [
    RandomStringCreator,
    EncryptedStringCreator,
    CounterEncodedStringCreator
])
async def test_string_creator_wrong_url_length_input(get_redis_client: AsyncMock, creator_class):
    from url_shortener.services.shortening import RandomStringCreator

    max_length = 3
    fake_url = "http://www.faker.com"
    minutes_until_expiration = 10
    creator = creator_class(max_length=max_length)
    with pytest.raises(ValueError, match="Length of shortened url must be larger than 3 chars. Currently is: 3"):
        shortened_url = await creator.shorten_url(
                                        original_url=fake_url,
                                        minutes_until_expiration=minutes_until_expiration
        )
@pytest.mark.asyncio
@pytest.mark.parametrize("creator_class", [
    RandomStringCreator,
    EncryptedStringCreator,
    CounterEncodedStringCreator
])
async def test_string_creator_wrong_url_type_input(get_redis_client: AsyncMock, creator_class):
    from url_shortener.services.shortening import RandomStringCreator

    max_length = 10
    fake_url = None
    minutes_until_expiration = 10
    creator = creator_class(max_length=max_length)
    with pytest.raises(ValueError, match="Original url must be an str objeect. Currently is: <class 'NoneType'>"):
        shortened_url = await creator.shorten_url(
                                        original_url=fake_url,
                                        minutes_until_expiration=minutes_until_expiration
        )
@pytest.mark.asyncio
@pytest.mark.parametrize("creator_class", [
    RandomStringCreator,
    EncryptedStringCreator,
    CounterEncodedStringCreator
])
async def test_string_creator_wrong_minute_until_expiration_input(get_redis_client: AsyncMock, creator_class):
    from url_shortener.services.shortening import RandomStringCreator

    max_length = 10
    fake_url = "http://www.faker.com"
    minutes_until_expiration = 3
    creator = creator_class(max_length=max_length)
    with pytest.raises(ValueError, match="Minutes until experiation must be >= 5 or <= 60. Currently is 3"):
        shortened_url = await creator.shorten_url(
                                        original_url=fake_url,
                                        minutes_until_expiration=minutes_until_expiration
        )






