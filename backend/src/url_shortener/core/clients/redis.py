import redis.asyncio as r
from redis.client import Redis

from url_shortener.core.settings import app_settings


class RedisClient:
	def __init__(self) -> None:
		self._client = None


	async def connect(self) -> Redis:
		if not self._client:
			self._client = r.from_url(
				url=app_settings.REDIS_URL,
				encoding="utf-8",
				decode_responses=True,
				max_connections=1,
			)
		print(f"REDIS CLIENT ID: {id(self._client)}")
		return self._client

	async def get_client(self) -> Redis:
		if not self._client:
			print(f"CLIENT DIDNT EXIST BEFORE!")
			return await self.connect()
		print(f"REDIS CLIENT ID: {id(self._client)}")
		return self._client

	async def close(self) -> None:
		if self._client:
			print(f"REDIS CLIENT ID: {id(self._client)}")
			await self._client.aclose()
			self._client = None


redis_client = RedisClient()
