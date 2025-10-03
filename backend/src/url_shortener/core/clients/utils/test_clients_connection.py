from fastapi import Depends
from sqlalchemy.future import select  # Important for async queries

from core import redis_client
from database import AsyncSession, User, get_db


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
