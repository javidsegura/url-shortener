import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from core import get_current_user, redis_client, settings
from database import AsyncSession, create_link, get_db
from schemas import (
	DataURL,
	URLShorteningDBStore,
	URLShorteningRequest,
	URLShorteningResponse,
)

from .utils import ShorteningFactory

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
	"""
	if request.expires_in > settings.MAX_MINUTES_STORAGE:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expiration time exceeds maximum allowed")

	shortener = ShorteningFactory.create_shortener(
		algorithm_choice="random",
		org_url=request.original_url,
		length=settings.SHORTENED_URL_LENGTH,
		min_expires_in=request.expires_in,
	)
	shortened_url = await shortener.create_url()

	# Register to db:
	print(f"CURRENT USER: {current_user}")
	url_info = URLShorteningDBStore(
		creator_id=current_user["uid"],
		old_link=request.original_url,
		new_link=shortened_url,
		expires_at=request.expires_in * 60 + time.time(),
		click_count=0,
	)
	await create_link(db, url_info)

	return shortened_url
