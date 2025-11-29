import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from url_shortener.database.CRUD.links import (
    create_link,
    increment_link_count,
    get_list_of_links,
)
from url_shortener.schemas.db_CRUD.link import URLShorteningDBStore
from url_shortener.database.generated_models import Link


class TestCreateLink:
    """Test the create_link function."""

    @pytest.mark.asyncio
    async def test_create_link_success(self):
        """Test creating a link successfully."""
        mock_db = AsyncMock()
        expires_at = datetime.now() + timedelta(hours=1)

        url_info = URLShorteningDBStore(
            creator_id="user123",
            old_link="https://example.com",
            new_link="abc12345",
            expires_at=expires_at.timestamp(),
            click_count=0
        )

        mock_link = Link(
            creator_id="user123",
            old_link="https://example.com",
            new_link="abc12345",
            expires_at=expires_at,
            click_count=0
        )

        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock(side_effect=lambda x: setattr(x, 'link_id', 1) or None)

        # Call the function - it will create a Link instance internally
        result = await create_link(mock_db, url_info)

        # Verify database operations were called
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert result is not None
        assert hasattr(result, 'creator_id')


class TestIncrementLinkCount:
    """Test the increment_link_count function."""

    @pytest.mark.asyncio
    async def test_increment_link_count_success(self):
        """Test incrementing link count successfully."""
        mock_db = AsyncMock()
        mock_execute = AsyncMock()
        mock_db.execute = mock_execute
        mock_db.commit = AsyncMock()

        await increment_link_count(mock_db, "abc12345")

        mock_execute.assert_called_once()
        mock_db.commit.assert_called_once()


class TestGetListOfLinks:
    """Test the get_list_of_links function."""

    @pytest.mark.asyncio
    async def test_get_list_of_links_success(self):
        """Test getting list of links successfully."""
        mock_db = AsyncMock()

        mock_link1 = Link(
            link_id=1,
            creator_id="user123",
            old_link="https://example.com",
            new_link="abc12345",
            expires_at=datetime.now(),
            timeRegistered=datetime.now(),
            click_count=0
        )

        mock_link2 = Link(
            link_id=2,
            creator_id="user123",
            old_link="https://example2.com",
            new_link="def67890",
            expires_at=datetime.now(),
            timeRegistered=datetime.now(),
            click_count=5
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_link1, mock_link2]
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await get_list_of_links(mock_db, "user123")

        assert len(result) == 2
        assert result[0].creator_id == "user123"
        assert result[1].creator_id == "user123"
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_list_of_links_empty(self):
        """Test getting empty list of links."""
        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await get_list_of_links(mock_db, "user123")

        assert len(result) == 0
        assert result == []
