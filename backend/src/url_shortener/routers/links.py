import time
import traceback
from typing import Annotated, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from url_shortener.core.clients import redis_client
from url_shortener.core.settings.app_settings import Settings, app_settings
from url_shortener.database import AsyncSession, create_link
from url_shortener.dependencies import verify_user, get_db, get_app_settings

from url_shortener.schemas.db_CRUD import URLShorteningDBStore
from url_shortener.schemas.endpoints import DataURL, URLShorteningRequest, URLShorteningResponse

from url_shortener.services.shortening import RandomStringCreator

import logging
logger = logging.getLogger(__name__)


router = APIRouter(prefix="/link")
verify_user_dependency = verify_user()

@router.post(path="", status_code=status.HTTP_200_OK)
async def shortern_link(
	current_user: Annotated[dict, Depends(verify_user_dependency)],
	db: Annotated[AsyncSession, Depends(get_db)],
	app_settings: Annotated[Settings, Depends(get_app_settings)],
	shortening_request: URLShorteningRequest,
) -> (
	Dict[str, str]
):  
	"""
	1) Fetch user config
	2) Create shortened version
	3) If collision go back to 2, else move on to step 4
	4) Add to redis
	5) Exit

	Add a register approach that avoids OCP violation
	"""
	try: 
		if shortening_request.expires_in_min > app_settings.MAX_MINUTES_STORAGE:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expiration time exceeds maximum allowed")
		creator = RandomStringCreator(max_length=app_settings.SHORTENED_URL_LENGTH) # Devs can change this algorithm if they find it conventient

		shortened_url = await creator.shorten_url(
							original_url=shortening_request.original_url,
							minutes_until_expiration=shortening_request.expires_in_min
		)
	except Exception as e:
		full_traceback = traceback.format_exc()

		# Print the exception details and the full traceback
		logger.debug(f"An exception of type {type(e).__name__} occurred.")
		logger.debug(f"Details: {e}")
		logger.debug("Full Traceback:")
		logger.debug(full_traceback)

		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"An exception occurred: {e}"
		)

	# Register to db:
	logger.debug(f"CURRENT USER: {current_user}")
	url_info = URLShorteningDBStore(
		creator_id=current_user["uid"],
		old_link=shortening_request.original_url,
		new_link=shortened_url,
		expires_at=shortening_request.expires_in_min * 60 + time.time(),
		click_count=0,
	)
	await create_link(db, url_info)

	return {"shortened_url": shortened_url}
