from sqlalchemy import select

from database import AsyncSession, User
from schemas import CreateUserRequest


async def create_user(db: AsyncSession, user_data: CreateUserRequest) -> User:
	db_user = User(
		user_id=user_data.user_id,
		displayable_name=user_data.displayable_name,
		email=user_data.email,
		profile_pic_object_name=user_data.profile_pic_object_name,
		country=user_data.country,
	)

	db.add(db_user)

	await db.commit()
	await db.refresh(db_user)

	return db_user


async def read_user(db: AsyncSession, user_id: str) -> User:
	result = await db.execute(select(User).where(User.user_id == user_id))
	return result.scalar_one_or_none()
