from fastapi.testclient import TestClient

import logging

logger = logging.getLogger(__name__)

class TestHealthEndpoint():
      def test_health_ping(self, fastapi_client: TestClient):
            response = fastapi_client.get(
                  url="/api/health/ping"
            )
            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "pong"

      def test_health_dependencies(self, fastapi_client: TestClient, start_docker_compose_services):
            response = fastapi_client.get(
                  url="/api/health/dependencies"
            )
            assert response.status_code == 200
            data = response.json()
            logger.debug(f"RESPONSES IS: {data}")
