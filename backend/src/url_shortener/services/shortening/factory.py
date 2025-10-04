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

from url_shortener.core.clients.redis import initialize_redis_client
from .concrete_implementations import Shortener, RandomString, EncryptedString, CounterEncodedString
from url_shortener.core.settings import initialize_settings

class BaseCreator(ABC):
	def __init__(self) -> None:
		self.redis_client = initialize_redis_client()
		self.app_settings = initialize_settings()
	@abstractmethod
	def factory_method(self) -> Shortener:
		pass
	async def _store_shortened_url_in_redis(self, 
								    original_url: str,
								    shortened_url: str,
								    minutes_until_expiration: int):
		redis = await self.redis_client.get_client()
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
		if not (self.app_settings.MIN_MINUTES_STORAGE <= minutes_until_expiration <= self.app_settings.MAX_MINUTES_STORAGE):
			raise ValueError(f"Minutes until experiation must be >= {self.app_settings.MIN_MINUTES_STORAGE} or <= {self.app_settings.MAX_MINUTES_STORAGE}. Currently is {minutes_until_expiration}")
		shortener = self.factory_method()
		shortened_url = shortener.shorten_url(original_url)
		await self._store_shortened_url_in_redis(
									original_url,
									shortened_url,
									minutes_until_expiration)
		return shortened_url

class RandomStringCreator(BaseCreator):
	def __init__(self, max_length: int) -> None:
		super().__init__()
		self.max_length = max_length
	def factory_method(self) -> Shortener:
		return RandomString(self.max_length)
class EncryptedStringCreator(BaseCreator):
	def __init__(self, max_length: int) -> None:
		super().__init__()
		self.max_length = max_length
	def factory_method(self) -> Shortener:
		return EncryptedString(self.max_length)
class CounterEncodedStringCreator(BaseCreator):
	def __init__(self, max_length: int) -> None:
		super().__init__()
		self.max_length = max_length
	def factory_method(self) -> Shortener:
		return CounterEncodedString(self.max_length)

"""
USAGE (client):
	RandomStringCreator(max_length=8).shorten_url(original_url="http://www.my_url.com", 
								    minutes_until_expiration=100)
"""