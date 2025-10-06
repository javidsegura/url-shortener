import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from url_shortener.database.CRUD.user import create_user, delete_user, read_user
from url_shortener.database.generated_models import User

class TestUserHealthyInput:
      """
      1) Test two endpoints for correct data
      2) Test one endpoint for proper exception rasing on missing data or incorrect datatype
      """
      @pytest.mark.asyncio
      async def test_user_creation(self, db_session: AsyncSession):
            fake_user = User(
                  user_id = "111",
                  displayable_name = "testUser",
                  email = "test@gmail.com",
                  profile_pic_object_name="pics/myObj",
                  country="US",
            )

            created_user = await create_user(db_session, fake_user)

            assert created_user is not None
            assert created_user.user_id == fake_user.user_id
            assert created_user.displayable_name == fake_user.displayable_name
            assert created_user.email == fake_user.email
            assert created_user.profile_pic_object_name == fake_user.profile_pic_object_name
            assert created_user.country == fake_user.country
            assert created_user.timeRegistered is not None
            assert created_user.isAdmin == 0

            looked_up_user = await read_user(db_session, fake_user.user_id)
            assert looked_up_user.user_id == fake_user.user_id
      
      @pytest.mark.asyncio
      async def test_user_deletion(self, db_session: AsyncSession):
            fake_user = User(
                  user_id = "111",
                  displayable_name = "testUser",
                  email = "test@gmail.com",
                  profile_pic_object_name="pics/myObj",
                  country="US",
            )

            created_user = await create_user(db_session, fake_user)
            user_was_deleted = await delete_user(db_session, fake_user.user_id)
            assert user_was_deleted
            looked_up_user = await read_user(db_session, fake_user.user_id)
            assert looked_up_user is None

