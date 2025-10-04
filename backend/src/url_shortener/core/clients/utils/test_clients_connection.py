from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select  # Important for async queries

from url_shortener.core.clients.redis import redis_client
from url_shortener.dependencies import get_db
from url_shortener.database import User

# FIX: these tests need to be redesigned 

# Redis
async def test_redis_connection() -> bool:
	client = await redis_client.get_client()
	response = await client.ping()
	return response


# Database
async def test_db_connection(db: AsyncSession = Depends(get_db)) -> bool:
	result = await db.execute(select(User))
	if result:
		instance = result.scalars().first()
		print(f"FIRST INSTANCE {instance}")
		return True
	return False
