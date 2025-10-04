import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from url_shortener.database.main import initialize_db_engine, AsyncSessionLocal

@pytest.fixture(autouse=True)
def reset_db_state():
    """Reset the AsyncSessionLocal global variable before each test."""
    global AsyncSessionLocal
    AsyncSessionLocal = None

def test_initialize_db_engine_creates_engine_and_session():
    """
    Test that initialize_db_engine correctly creates and configures
    the async database engine and session maker.
    """
    with patch("url_shortener.database.main.create_async_engine") as mock_create_engine, \
         patch("url_shortener.database.main.async_sessionmaker") as mock_sessionmaker:

        # Mock the engine and session maker objects
        mock_engine = MagicMock()
        mock_session_local = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_sessionmaker.return_value = mock_session_local

        # Call the function to be tested
        initialize_db_engine()

        # Assertions to verify correct behavior
        mock_create_engine.assert_called_once()
        args, kwargs = mock_create_engine.call_args
        
        # Verify the database URL is constructed correctly from mocked env vars
        expected_db_url = "aiomysql://test_user:test_password@localhost:3306/test_db"
        assert args[0] == expected_db_url
        
        # Verify production-ready configuration parameters
        assert kwargs['echo'] is False
        assert kwargs['pool_size'] == 10
        assert kwargs['max_overflow'] == 20
        assert kwargs['pool_pre_ping'] is True
        assert kwargs['pool_recycle'] == 3600

        # Verify that async_sessionmaker is called with the mocked engine
        mock_sessionmaker.assert_called_once_with(
            mock_engine, class_=AsyncSession, expire_on_commit=False
        )

