"""

We create simple factory design pattern for concrete product being
a) base64 encoding, b) random-string, c) cryptographic-hash.
We discuss their pros and cons as well.


"""

import asyncio
import os
import random
import secrets
import string
import threading
from abc import ABC, abstractmethod
from hashlib import sha256

from url_shortener.core.clients.redis import redis_client
from .concrete_implementations import Shortener, RandomString, EncryptedString, CounterEncodedString

class BaseCreator(ABC):
	@abstractmethod
	def factory_method(self) -> Shortener:
		pass
	async def _store_shortened_url_in_redis(self, 
								    original_url: str,
								    shortened_url: str,
								    minutes_until_expiration: int):
		redis = await redis_client.get_client()
		await redis.set(
			name=shortened_url, 
			value=original_url, 
			ex=minutes_until_expiration * 60
		)
		print( # FIX => Add logger 
			f"SUCCESFULLY SET URL: {await redis.get(shortened_url)} with \
                ttl: {await redis.ttl(shortened_url)}"
		)
	async def shorten_url(self, original_url:str, minutes_until_expiration: int = 10) -> str:
		if not isinstance(original_url, str):
			raise ValueError(f"Original url must be an str objeect. Currently is: {type(original_url)}")
		if not (5 <= minutes_until_expiration <= 60):
			raise ValueError(f"Minutes until experiation must be >= 5 or <= 60. Currently is {minutes_until_expiration}")
		shortener = self.factory_method()
		shortened_url = shortener.shorten_url(original_url)
		await self._store_shortened_url_in_redis(
									original_url,
									shortened_url,
									minutes_until_expiration)
		return shortened_url

class RandomStringCreator(BaseCreator):
	def __init__(self, max_length: int) -> None:
		self.max_length = max_length
	def factory_method(self) -> Shortener:
		return RandomString(self.max_length)
class EncryptedStringCreator(BaseCreator):
	def __init__(self, max_length: int) -> None:
		self.max_length = max_length
	def factory_method(self) -> Shortener:
		return EncryptedString(self.max_length)
class CounterEncodedStringCreator(BaseCreator):
	def __init__(self, max_length: int) -> None:
		self.max_length = max_length
	def factory_method(self) -> Shortener:
		return CounterEncodedString(self.max_length)

"""
USAGE (client):
	RandomStringCreator(max_length=8).shorten_url(original_url="http://www.my_url.com", 
								    minutes_until_expiration=100)
"""