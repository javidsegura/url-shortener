from url_shortener.database import AsyncSession, AsyncSessionLocal

async def get_db() -> AsyncSession:
	async with AsyncSessionLocal() as session:
		try:
			yield session
		finally:
			await session.close()
