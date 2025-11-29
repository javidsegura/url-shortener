from fastapi.testclient import TestClient

import logging
import uuid

import pytest
import requests

logger = logging.getLogger(__name__)

class TestUserEndpoint():
      def test_create_user_integration(self,
            fastapi_client: TestClient,
            start_docker_compose_services):
            """Integration test for POST /api/user - CREATE operation"""
            # Generate unique user data
            user_id = f"test_user_{uuid.uuid4().hex[:8]}"
            user_data = {
                  "user_id": user_id,
                  "displayable_name": "Test User",
                  "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
                  "profile_pic_object_name": "images/test_user",
                  "country": "USA"
            }

            # Create user via API
            response = fastapi_client.post(
                  url="/api/user",
                  json=user_data
            )

            # Assert successful creation
            assert response.status_code == 201
            assert f"User created succesfully with id: {user_id}" in response.text

            logger.info(f"Successfully created user with id: {user_id}")
