# database.py - Production-ready database configuration
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from core import settings

DATABASE_URL = (
	f"{settings.MYSQL_ASYNC_DRIVER}"
	f"://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}"
	f":{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
)


# Production engine configuration
engine = create_async_engine(
	DATABASE_URL,
	echo=False,  # Never True in production (performance impact)
	pool_size=10,  # Connection pool size
	max_overflow=20,  # Additional connections when pool is full
	pool_pre_ping=True,  # Validate connections before use
	pool_recycle=3600,  # Recycle connections every hour
)

AsyncSessionLocal = async_sessionmaker(
	engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncSession:
	async with AsyncSessionLocal() as session:
		try:
			yield session
		finally:
			await session.close()
