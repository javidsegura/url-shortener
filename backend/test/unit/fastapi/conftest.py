import os
from unittest.mock import AsyncMock
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from url_shortener.dependencies.database import get_db
from url_shortener.main import app
from url_shortener.core.settings import initialize_settings

       
# conftest.py
import os
from unittest.mock import AsyncMock
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from url_shortener.dependencies.database import get_db
from url_shortener.main import app
from url_shortener.core.settings import initialize_settings
from url_shortener.routers.links import verify_user_dependency
from url_shortener.routers.user import verify_user_private_dependency


       
@pytest.fixture
def mock_db_override():
    """Overrides the database dependency with a mock session."""
    mock_session = AsyncMock(spec=AsyncSession)
    
    def get_mock_db():
        return mock_session

    app.dependency_overrides[get_db] = get_mock_db
    yield mock_session
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def mock_user_auth_override():
    """Overrides the user authentication dependency with a mock user."""
    mock_user = {"uid": "1", "email": "test@example.com"}
    
    def get_mock_user():
        return mock_user

    app.dependency_overrides[verify_user_dependency] = get_mock_user
    app.dependency_overrides[verify_user_private_dependency] = get_mock_user
    yield mock_user
    app.dependency_overrides.pop(verify_user_dependency, None)
    app.dependency_overrides.pop(verify_user_private_dependency, None)


@pytest.fixture
def fastapi_client(mock_db_override, mock_user_auth_override):
    """Create TestClient AFTER overrides are applied."""
    # Overrides are already set by the time we get here
    with TestClient(app) as client:
        yield client
    # Context manager ensures proper cleanup