from sqlalchemy.ext.asyncio import AsyncSession

from url_shortener.database.main import initialize_db_engine


async def get_db() -> AsyncSession:
	AsyncSessionLocal = initialize_db_engine()
	async with AsyncSessionLocal() as session:
		try:
			yield session
		finally:
			await session.close()
