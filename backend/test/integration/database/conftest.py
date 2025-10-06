# backend/test/integration/conftest.py
import os
import pytest
import pytest_asyncio

from sqlalchemy import make_url
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.mysql import MySqlContainer

from url_shortener.core.settings import initialize_settings
from url_shortener.database.generated_models import Base


def _build_async_url(raw_url: str) -> str:
    """
    Convert testcontainers 'mysql://user:pass@host:port/db' to
    'mysql+aiomysql://user:pass@host:port/db', normalizing host.
    """
    u = make_url(raw_url)
    host = (u.host or "127.0.0.1").replace("localhost", "127.0.0.1")
    async_url = URL.create(
        drivername="mysql+aiomysql",
        username=u.username,
        password=u.password,
        host=host,
        port=u.port,
        database=u.database,
        query=u.query,
    )
    return async_url.render_as_string(hide_password=False)


@pytest.fixture(scope="session")
def mysql_container():
    with MySqlContainer("mysql:8.0") as mysql:
        yield mysql


@pytest_asyncio.fixture(scope="function")
async def db_session(mysql_container: MySqlContainer) -> AsyncSession:
    async_url = _build_async_url(mysql_container.get_connection_url())
    engine = create_async_engine(async_url, echo=False, pool_pre_ping=True)

    # Create schema for this test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    # Provide a usable session to the test
    async with SessionLocal() as session:
        yield session

    # Clean up: close all connections, drop schema, dispose engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()