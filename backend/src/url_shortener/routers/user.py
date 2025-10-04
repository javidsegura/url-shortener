from typing import Annotated, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from url_shortener.dependencies import verify_user, get_db
from url_shortener.core.settings import app_settings
from url_shortener.core.clients import redis_client, s3_client
from url_shortener.database.CRUD.user import create_user, read_user
from url_shortener.database import Link, User, get_list_of_links
from url_shortener.services.infra.s3 import PresignedUrl

from url_shortener.schemas.endpoints import CreateUserRequest, UploadProfilePicRequest, ListOfLinksResponse, GetUserDataResponse

router = APIRouter(prefix="/user")


@router.post(path="", status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
	user_data: CreateUserRequest, db: Annotated[AsyncSession, Depends(get_db)]
) -> GetUserDataResponse:
	user = await create_user(user_data=user_data, db=db)
	return user


@router.get(path="/{user_id}", status_code=status.HTTP_201_CREATED)
async def get_user_endpoint(
	user_id: str,
	db: Annotated[AsyncSession, Depends(get_db)],
	current_user: Annotated[dict, Depends(verify_user(user_specific_route=True))],
) -> GetUserDataResponse:
	user = await read_user(db, user_id)

	try:
		presigned_url_creator = PresignedUrl(s3_client=s3_client)
		presigned_url = presigned_url_creator.get_presigned_url(
						s3_bucket_name=app_settings.S3_MAIN_BUCKET_NAME,
						key=user.profile_pic_object_name
		)
		return GetUserDataResponse(**user.__dict__, presigned_url_profile_pic=presigned_url)
	except Exception as e:
		print("=> ERROR WITH AWS PRESIGNED URL")
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{str(e)} -- couldnt get aws presigned url"
		)


@router.get(path="/{user_id}/links")
async def get_user_links_endpoints(
	user_id: str,
	db: Annotated[AsyncSession, Depends(get_db)],
	current_user: Annotated[dict, Depends(verify_user(user_specific_route=True))],
) -> List[ListOfLinksResponse]:
	links = await get_list_of_links(db, current_user["uid"])
	return links


@router.post(path="/profile_pic")
async def create_presigned_url_profile_pic_endpoint(
	request: UploadProfilePicRequest,
) -> Dict:
	"""
	Potential bug: overwriting an existing image uploaded by someone else.
	Solution: check name doesnt exist before + add random postfix
	"""
	s3_file_name = f"/users/profile-pictures/{request.file_name}"
	try:
		presigned_url_creator = PresignedUrl(s3_client=s3_client)
		presigned_url = presigned_url_creator.get_presigned_url(
						s3_bucket_name=app_settings.S3_MAIN_BUCKET_NAME,
						key=s3_file_name,
						ContentType=request.content_type
						
		)
		print(f"Sucesfully created presigned url {presigned_url}")
		return {"presigned_url": presigned_url, "s3_file_name": s3_file_name}
	except Exception as e:
		print(f"Exception in: {e}")
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
		)
