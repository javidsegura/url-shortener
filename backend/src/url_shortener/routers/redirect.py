import traceback
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import RedirectResponse


from url_shortener.core.clients.redis import initialize_redis_client
from url_shortener.database import AsyncSession, increment_link_count
from url_shortener.dependencies import get_db

router = APIRouter(prefix="/short")


@router.get(path="/{shortened_url}", status_code=status.HTTP_308_PERMANENT_REDIRECT)
async def redirect_endpoint(
	shortened_url: str, db: Annotated[AsyncSession, Depends(get_db)]
) -> RedirectResponse:
	# 1) Extraxct key of url
	try:
		redis_connector = initialize_redis_client()
		redis = await redis_connector.get_client()
		og_url = await redis.get(shortened_url)
		if not og_url:
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			)
		# 2) Autoincrment
		await increment_link_count(db, shortened_url)

		# 2) Redirect
		return RedirectResponse(url=og_url, status_code=308)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"An exception occurred: {e}"
		)
