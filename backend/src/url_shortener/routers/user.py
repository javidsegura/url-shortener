import traceback
from typing import Annotated, Dict, List

from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from url_shortener.core.settings.app_settings import Settings
from url_shortener.dependencies import verify_user, get_db, get_app_settings
from url_shortener.core.clients import redis_client, s3_client
from url_shortener.database.CRUD.user import create_user, edit_user_name, read_user, delete_user
from url_shortener.database import Link, User, get_list_of_links
from url_shortener.schemas.endpoints.user import ModifyUserNameRequest
from url_shortener.services.infra.s3 import PresignedUrl

from url_shortener.schemas.endpoints import CreateUserRequest, UploadProfilePicRequest, ListOfLinksResponse, GetUserDataResponse

import logging 
logger = logging.getLogger(__name__)


# GLOBAL VARIABLES
router = APIRouter(prefix="/user")
verify_user_private_dependency = verify_user(user_private_route=True)


@router.post(path="", status_code=status.HTTP_201_CREATED) # This should be a / depednent endpoint 
async def create_user_endpoint(
	user_data: CreateUserRequest, db: Annotated[AsyncSession, Depends(get_db)]
) -> str:
	await create_user(user_data=user_data, db=db)
	return f"User created succesfully with id: {user_data.user_id}"


@router.get(path="/{user_id}", status_code=status.HTTP_201_CREATED)
async def get_user_endpoint(
	user_id: str,
	db: Annotated[AsyncSession, Depends(get_db)],
	app_settings: Annotated[Settings, Depends(get_app_settings)],
	#current_user: Annotated[dict, Depends(verify_user_private_dependency)],
) -> GetUserDataResponse:
	user = await read_user(db, user_id)

	try:
		presigned_url_creator = PresignedUrl()
		presigned_url = presigned_url_creator.get_presigned_url(
						s3_bucket_name=app_settings.S3_MAIN_BUCKET_NAME,
						key=user.profile_pic_object_name
		)
		return GetUserDataResponse(**user.__dict__, presigned_url_profile_pic=presigned_url)
	except ValueError as e:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=str(e)
		)
	except ClientError as e:
		error_code = e.response['Error']['Code']
		error_message = e.response['Error']['Message']
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"S3 error ({error_code}): {error_message}"
		)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Failed to generate presigned URL: {str(e)}"
		)


@router.patch(path="/{user_id}", status_code=status.HTTP_200_OK)
async def patch_user_endpoint(
	user_id: str,
	change_name_request: ModifyUserNameRequest,
	db: Annotated[AsyncSession, Depends(get_db)],
	current_user: Annotated[dict, Depends(verify_user_private_dependency)],
) -> str:
	user_edited = await edit_user_name(db=db, user_id=user_id, new_name=change_name_request.new_name)
	if user_edited:
		return f"User with id: {user_id} edited successfully."
	else:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"User with id: {user_id} not found."
		)

@router.delete(path="/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user_endpoint(
	user_id: str,
	db: Annotated[AsyncSession, Depends(get_db)],
	current_user: Annotated[dict, Depends(verify_user_private_dependency)],
) -> str:
	user_deleted = await delete_user(db=db, user_id=user_id)
	if user_deleted:
		return f"User with id: {user_id} deleted successfully."
	else:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"User with id: {user_id} not found."
		)


@router.get(path="/{user_id}/links")
async def get_user_links_endpoints(
	user_id: str,
	db: Annotated[AsyncSession, Depends(get_db)],
	current_user: Annotated[dict, Depends(verify_user_private_dependency)],
) -> List[ListOfLinksResponse]:
	links = await get_list_of_links(db, current_user["uid"])
	return links


@router.post(path="/profile_pic")
async def create_presigned_url_profile_pic_endpoint(
	request: UploadProfilePicRequest,
	app_settings: Annotated[Settings, Depends(get_app_settings)],
) -> Dict:
	s3_file_name = f"/users/profile-pictures/{request.file_name}"
	try:
		presigned_url_creator = PresignedUrl()
		presigned_url = presigned_url_creator.put_presigned_url(
						s3_bucket_name=app_settings.S3_MAIN_BUCKET_NAME,
						key=s3_file_name,
						ContentType=request.content_type
						
		)
		logger.debug(f"Sucesfully created presigned url {presigned_url}")
		return {"presigned_url": presigned_url, "s3_file_name": s3_file_name}
	except Exception as e:
		logger.debug(f"Exception in: {e}")
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
		)
