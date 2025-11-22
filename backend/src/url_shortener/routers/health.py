import logging
from typing import Annotated, Dict

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from url_shortener.core.clients.utils.test_clients_connection import (
	test_db_connection,
	test_redis_connection,
)
from url_shortener.core.settings import Settings
from url_shortener.database.CRUD.user import read_user
from url_shortener.dependencies import get_app_settings, get_db

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/health")


@router.get(path="/dependencies", status_code=status.HTTP_200_OK)
async def cheeck_backend_health_dependencies_endpoint(
	db: Annotated[AsyncSession, Depends(get_db)],
) -> Dict:
	"""
	You could have here the response schema to be service with variables\
		being 'status' and 'error' (if any)
	"""
	redis_status = await test_redis_connection()
	db_status = await test_db_connection(db=db)
	return {"services": {"redis": redis_status, "db": db_status}}


@router.get(path="/ping", status_code=status.HTTP_200_OK)
async def cheeck_backend_health_endpoint(
	app_settings: Annotated[Settings, Depends(get_app_settings)],
) -> Dict:
	return {"response": "pong"}
