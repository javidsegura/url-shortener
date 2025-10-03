from sqlalchemy.ext.asyncio import AsyncSession
from url_shortener.database import AsyncSessionLocal


async def get_db() -> AsyncSession:
	async with AsyncSessionLocal() as session:
		try:
			yield session
		finally:
			await session.close()
