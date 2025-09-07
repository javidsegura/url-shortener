from typing import Annotated, Dict

from fastapi import APIRouter, Depends

from core import get_current_user
from database.CRUD.user import read_user
from database import get_db, AsyncSession
from schemas import GetUserDataResponse


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
 