from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
import pytest
from url_shortener.database.generated_models import Link
from url_shortener.main import app
from url_shortener.dependencies import get_db
from url_shortener.schemas.endpoints.link import DataURL, URLShorteningRequest

class TestLinkgsEndpoint:
      def test_basic(self,  
                        get_mock_redis_client: AsyncMock,
                        mock_db_override: AsyncMock, 
                        mock_user_auth_override: AsyncMock,
                        fastapi_client: TestClient): # FIX: could we recycle from this as much as possible for integraito ntests? 
      

            fake_url_shortening_request = URLShorteningRequest(
                  original_url="test-very-lomg.com",
                  expires_in_min=10
                  
            )
            with patch("url_shortener.routers.links.create_link") as mock_create_link, \
                 patch("url_shortener.routers.links.RandomStringCreator") as MockCreatorClass:
                  mock_create_link.return_value = Link(
                        link_id=1,
                        creator_id=1,
                        old_link="old_link.com",
                        new_link="new_link_abc",
                        expires_at=datetime.now(),
                  )
                  mock_creator_instance = MockCreatorClass.return_value
                  

                  MOCKED_SHORT_URL = "new_link_abc"
                  mock_creator_instance.shorten_url = AsyncMock(return_value=MOCKED_SHORT_URL) 

                  response = fastapi_client.post("/api/link",
                        json=fake_url_shortening_request.model_dump()
                  )

                  assert response.status_code == 200
                  data = response.json()
                  assert data["shortened_url"] == "new_link_abc"
                  #get_mock_redis_client.set

                  mock_create_link.assert_awaited_once()
      def test_min_length(self, 
                        mock_db_override: AsyncMock, 
                        mock_user_auth_override: AsyncMock,
                        fastapi_client: TestClient): # FIX: could we recycle from this as much as possible for integraito ntests? 
      
            fake_url_shortening_request = URLShorteningRequest(
                  original_url="test-very-lomg.com",
                  expires_in_min=100
                  
            )
            response = fastapi_client.post("/api/link",
                  json=fake_url_shortening_request.model_dump()
            )
            assert response.status_code == 500
