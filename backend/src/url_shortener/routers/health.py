from typing import Annotated, Dict

from fastapi import APIRouter, Depends, Request, status

from url_shortener.core.clients.utils.test_clients_connection import test_db_connection, test_redis_connection
from sqlalchemy.ext.asyncio import AsyncSession
from url_shortener.dependencies.database import get_db

router = APIRouter(prefix="/health")


@router.get(path="", status_code=status.HTTP_200_OK)
async def cheeck_backend_health_endpoint(
	request: Request, db: Annotated[AsyncSession, Depends(get_db)]
) -> Dict:
	"""
	You could have here the response schema to be service with variables\
		being 'status' and 'error' (if any)
	"""

	redis_status = await test_redis_connection()
	db_status = await test_db_connection(db=db)
	return {"services": {"fastapi": True, "redis": redis_status, "db": db_status}}
