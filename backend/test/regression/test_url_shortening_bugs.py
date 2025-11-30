"""
Regression tests for fixed bugs in URL shortening functionality.

These tests ensure that previously fixed bugs do not regress.
"""

import pytest
from unittest.mock import AsyncMock
from url_shortener.services.shortening import RandomStringCreator
from url_shortener.core.settings import initialize_settings


@pytest.mark.asyncio
async def test_regression_expiration_time_validation_in_endpoint(get_mock_redis_client: AsyncMock):
    """
    Regression test for bug: Endpoint was missing validation for expiration time.

    Bug: Previously, the endpoint didn't validate expires_in_min against
    MAX_MINUTES_STORAGE before calling the service, allowing invalid values.
    Fix: Added validation check in links.py endpoint (line 44).
    """
    app_settings = initialize_settings()
    creator = RandomStringCreator(max_length=app_settings.SHORTENED_URL_LENGTH)

    # This should fail at the service level (not endpoint level in this test)
    # but the regression ensures the service validation still works
    with pytest.raises(ValueError, match="Minutes until experiation must be"):
        await creator.shorten_url(
            original_url="http://www.example.com",
            minutes_until_expiration=app_settings.MAX_MINUTES_STORAGE + 1
        )


@pytest.mark.asyncio
async def test_regression_shortened_url_never_empty(get_mock_redis_client: AsyncMock):
    """
    Regression test for bug: Shortened URL could be empty string.

    Bug: Under certain conditions, shortened URLs could be empty strings.
    Fix: Validation ensures shortened URLs are always non-empty and valid.
    """
    creator = RandomStringCreator(max_length=8)
    shortened_url = await creator.shorten_url(
        original_url="http://www.example.com",
        minutes_until_expiration=10
    )

    assert shortened_url is not None
    assert len(shortened_url) > 0
    assert len(shortened_url) <= 8


@pytest.mark.asyncio
async def test_regression_url_validation_prevents_none(get_mock_redis_client: AsyncMock):
    """
    Regression test for bug: None URLs were not properly validated.

    Bug: Passing None as original_url could cause unexpected behavior.
    Fix: Added type validation in BaseCreator.shorten_url().
    """
    creator = RandomStringCreator(max_length=8)

    with pytest.raises(ValueError, match="Original url must be an str objeect"):
        await creator.shorten_url(
            original_url=None,
            minutes_until_expiration=10
        )
