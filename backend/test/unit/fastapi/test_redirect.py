from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

class TestRedirectEndpoint:
      def test_basic(self, 
                        fastapi_client: TestClient, 
                        mock_db_override: AsyncMock, 
                        get_mock_redis_client: AsyncMock): 

            fake_shortener_url = 123
            response = fastapi_client.get(f"/short/{fake_shortener_url}", follow_redirects=False)

            assert response.status_code == 308
            
            


