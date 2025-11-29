import logging
from typing import Annotated, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, status
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
	Simple readiness probe that only returns 200 when all dependencies are OK.
	"""

	checks = {"status": "healthy", "checks": {}}

	# Redis
	try:
		redis_connected = await test_redis_connection()
		if not redis_connected:
			raise Exception()
		checks["checks"]["redis"] = "ok"
	except Exception as e:
		checks["status"] = "unhealthy"
		checks["checks"]["redis"] = f"failed: {e}"

	if checks["status"] == "unhealthy":
		raise HTTPException(
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
			detail=checks,
		)

	return checks


@router.get(path="/ping", status_code=status.HTTP_200_OK)
async def cheeck_backend_health_endpoint(
	app_settings: Annotated[Settings, Depends(get_app_settings)],
) -> Dict:
	return {"response": "pong"}
