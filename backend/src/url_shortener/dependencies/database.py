from sqlalchemy.ext.asyncio import AsyncSession
from url_shortener.database.main import initialize_db_engine

async def get_db() -> AsyncSession:#pragma: no cover
	AsyncSessionLocal = initialize_db_engine()#pragma: no cover
	async with AsyncSessionLocal() as session:#pragma: no cover
		try:#pragma: no cover
			yield session#pragma: no cover
		finally:#pragma: no cover
			await session.close() #pragma: no cover