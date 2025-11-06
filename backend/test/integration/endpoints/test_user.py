from fastapi.testclient import TestClient

import logging

import pytest
import requests

logger = logging.getLogger(__name__)

class TestUserEndpoint():
      def test_user_getting_presinged_profile_pic(self, 
            fastapi_client: TestClient, 
            start_docker_compose_services):
            response = fastapi_client.get(
                  url="/api/user/12345"
            )
            print(f"RESPONSE FROM PRESEINGED IS: {response.json()['detail']}")
            assert response.status_code == 404
            assert "Object not found in S3" in response.json()["detail"]