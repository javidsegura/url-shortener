import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from url_shortener.core.clients import redis_client
from url_shortener.core.settings import app_settings
from url_shortener.database import AsyncSession, create_link
from url_shortener.dependencies import get_current_user, get_db

from url_shortener.schemas.db import URLShorteningDBStore
from url_shortener.schemas.endpoints import DataURL, URLShorteningRequest, URLShorteningResponse

from url_shortener.services.shortening import RandomStringCreator


router = APIRouter(prefix="/link")


@router.post(path="")
async def shortern_link(
	request: URLShorteningRequest,
	current_user: Annotated[dict, Depends(get_current_user())],
	db: Annotated[AsyncSession, Depends(get_db)],
) -> (
	str
):  # EXPIRES_AT is some app config that frontend fetches to the backend at start_up
	"""
	1) Fetch user config
	2) Create shortened version
	3) If collision go back to 2, else move on to step 4
	4) Add to redis
	5) Exit

	Add a register approach that avoids OCP violation
	"""
	
	# if request.expires_in > app_settings.MAX_MINUTES_STORAGE:
	# 	raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expiration time exceeds maximum allowed")

	# shortener = ShorteningFactory.create_shortener(
	# 	algorithm_choice="random",
	# 	original_url=request.original_url,
	# 	shortened_url_length=app_settings.SHORTENED_URL_LENGTH,
	# 	min_expires_in=request.expires_in,
	# )
	# shortened_url = await shortener.create_url()

	# # Register to db:
	# print(f"CURRENT USER: {current_user}")
	# url_info = URLShorteningDBStore(
	# 	creator_id=current_user["uid"],
	# 	old_link=request.original_url,
	# 	new_link=shortened_url,
	# 	expires_at=request.expires_in * 60 + time.time(),
	# 	click_count=0,
	# )
	# await create_link(db, url_info)

	# return shortened_url
