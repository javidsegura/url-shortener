from typing import Annotated, Dict

from fastapi import APIRouter, Depends

from url_shortener.dependencies import get_current_user
from url_shortener.database.CRUD.user import read_user
from url_shortener.database import AsyncSession
from url_shortener.dependencies import get_db
from url_shortener.schemas.endpoints import GetUserDataResponse


router = APIRouter(prefix="/test")


@router.get(path="")
async def get_test_endpoint(
	current_user: Annotated[
		dict, Depends(get_current_user(email_needs_verification=False))
	],
	db: Annotated[AsyncSession, Depends(get_db)],
) -> GetUserDataResponse:
	print(f"Current user!!!: {current_user}")
	user_id = current_user["uid"]
	user = await read_user(db, user_id)
	print(user.__dict__)
	return GetUserDataResponse(**user.__dict__, are_you_cool=False)
 