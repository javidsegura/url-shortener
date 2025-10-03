import asyncio
import os
import random
import secrets
import string
import threading
from abc import ABC, abstractmethod
from hashlib import sha256

from core import redis_client

class Shortener(ABC): # Abstract product
	def __init__(self, 
				max_length: int) -> None:
		self.max_length = max_length

	@abstractmethod
	def shorten_url(self, original_url: str) -> str: 
		pass

class RandomString(Shortener): # Concrete product 1
	def __init__(self, max_length: int) -> None:
		super().__init__(max_length)

	def shorten_url(self, original_url: str) -> str:
		shortened_url = "".join(
			secrets.choice(string.ascii_letters + string.digits)
			for _ in range(self.max_length)
		)
		return shortened_url


class EncryptedString(Shortener): # Concrete product 2
	def __init__(self, original_url: str, max_length: int, min_expires_in: int) -> None:
		super().__init__(original_url, max_length, min_expires_in)

	def shorten_url(self) -> str:
		shortened_url = sha256(self.original_url.encode("utf-8")).hexdigest()
		shortened_url = shortened_url[: self.max_length]
		return shortened_url

class Counter: 
	def __init__(self) -> None:
		self._value = 0
		self._lock = threading.Lock()

	def increment(self) -> int:
		with self._lock:
			self._value += 1
			return self._value


GLOBAL_COUNTER = Counter()


class CounterEncodedSstring(Shortener): # Concrete product 3
	def __init__(self, original_url: str, max_length: int, min_expires_in: int) -> None:
		super().__init__(original_url, max_length, min_expires_in)

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

		# Pad or truncate to desired max_length
		return result.zfill(self.max_length)[: self.max_length]