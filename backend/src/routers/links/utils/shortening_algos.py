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

from core import redis_client


class Counter:
	def __init__(self) -> None:
		self._value = 0
		self._lock = threading.Lock()

	def increment(self) -> int:
		with self._lock:
			self._value += 1
			return self._value


GLOBAL_COUNTER = Counter()


class Shortener(ABC):
	def __init__(self, org_url: str, length: int, min_expires_in: int) -> None:
		self.org_url = org_url
		self.length = length
		self.min_expires_in = min_expires_in

	@abstractmethod
	def shorten_url(self) -> str:
		pass

	async def create_url(self) -> str:
		shortened_url = self.shorten_url()
		redis = await redis_client.get_client()
		await redis.set(
			name=shortened_url, value=self.org_url, ex=self.min_expires_in * 60
		)
		print(
			f"SUCCESFULLY SET URL: {await redis.get(shortened_url)} with \
                ttl: {await redis.ttl(shortened_url)}"
		)
		return shortened_url


class RandomString(Shortener):
	def __init__(self, org_url: str, length: int, min_expires_in: int) -> None:
		super().__init__(org_url, length, min_expires_in)

	def shorten_url(self) -> str:
		shortened_url = "".join(
			secrets.choice(string.ascii_letters + string.digits)
			for _ in range(self.length)
		)
		return shortened_url


class EncryptedString(Shortener):
	def __init__(self, org_url: str, length: int, min_expires_in: int) -> None:
		super().__init__(org_url, length, min_expires_in)

	def shorten_url(self) -> str:
		shortened_url = sha256(self.org_url.encode("utf-8")).hexdigest()
		shortened_url = shortened_url[: self.length]
		return shortened_url


class CounterEncodedSstring(Shortener):
	def __init__(self, org_url: str, length: int, min_expires_in: int) -> None:
		super().__init__(org_url, length, min_expires_in)

	def shorten_url(self) -> str:
		value = GLOBAL_COUNTER.increment()
		return self._encode_counter(value)

	def _encode_counter(self, counter: int) -> str:
		chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
		if counter == 0:
			return chars[0]

		result = ""
		while counter > 0:
			result = chars[counter % 62] + result
			counter //= 62

		# Pad or truncate to desired length
		return result.zfill(self.length)[: self.length]


class ShorteningFactory:
	_ALGORITHMS = {
		"counter": CounterEncodedSstring,
		"encrypted": EncryptedString,
		"random": RandomString,
	}

	@staticmethod
	def create_shortener(
		algorithm_choice: str, org_url: str, length: int, min_expires_in: int
	) -> Shortener:
		algorithm_choice = algorithm_choice.lower()
		shortener_class = ShorteningFactory._ALGORITHMS.get(algorithm_choice)

		return shortener_class(org_url, length, min_expires_in)
