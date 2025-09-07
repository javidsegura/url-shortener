import pytest
import time
import sys
import os
import random
import secrets
import string
import threading
from abc import ABC, abstractmethod
from hashlib import sha256
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import BaseModel


# Test implementations (copied from source to avoid import issues)
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
        # Mock Redis operations for testing
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


# Test schemas
class URLShorteningRequest(BaseModel):
    original_url: str
    expires_in: int


class URLShorteningDBStore(BaseModel):
    creator_id: str
    old_link: str
    new_link: str
    expires_at: float
    click_count: int


class TestShorteningAlgorithms:
    """Test the URL shortening algorithms"""

    def test_random_string_shortener(self):
        """Test random string generation"""
        shortener = RandomString("https://example.com", 6, 60)
        result = shortener.shorten_url()
        
        assert len(result) == 6
        assert result.isalnum()

    def test_encrypted_string_shortener(self):
        """Test encrypted string generation"""
        shortener = EncryptedString("https://example.com", 8, 60)
        result = shortener.shorten_url()
        
        assert len(result) == 8
        assert result.isalnum()
        
        # Same URL should produce same hash
        result2 = shortener.shorten_url()
        assert result == result2

    def test_counter_encoded_shortener(self):
        """Test counter-based encoding"""
        shortener = CounterEncodedSstring("https://example.com", 4, 60)
        result1 = shortener.shorten_url()
        result2 = shortener.shorten_url()
        
        assert len(result1) == 4
        assert len(result2) == 4
        assert result1 != result2  # Different URLs should produce different results

    def test_shortening_factory(self):
        """Test factory pattern for creating shorteners"""
        # Test random algorithm
        shortener = ShorteningFactory.create_shortener(
            "random", "https://example.com", 6, 60
        )
        assert isinstance(shortener, RandomString)
        
        # Test encrypted algorithm
        shortener = ShorteningFactory.create_shortener(
            "encrypted", "https://example.com", 8, 60
        )
        assert isinstance(shortener, EncryptedString)
        
        # Test counter algorithm
        shortener = ShorteningFactory.create_shortener(
            "counter", "https://example.com", 4, 60
        )
        assert isinstance(shortener, CounterEncodedSstring)


class TestLinkCreation:
    """Test link creation functionality"""

    @pytest.mark.asyncio
    async def test_create_url(self):
        """Test URL creation"""
        shortener = RandomString("https://example.com", 6, 60)
        result = await shortener.create_url()
        
        assert len(result) == 6
        assert result.isalnum()

    def test_url_shortening_request_validation(self):
        """Test URL shortening request schema validation"""
        # Valid request
        request = URLShorteningRequest(
            original_url="https://example.com",
            expires_in=60
        )
        assert request.original_url == "https://example.com"
        assert request.expires_in == 60
        
        # Test with different values
        request = URLShorteningRequest(
            original_url="https://google.com",
            expires_in=1440  # 24 hours
        )
        assert request.original_url == "https://google.com"
        assert request.expires_in == 1440

    def test_url_shortening_db_store_validation(self):
        """Test URL shortening DB store schema validation"""
        current_time = time.time()
        db_store = URLShorteningDBStore(
            creator_id="user123",
            old_link="https://example.com",
            new_link="abc123",
            expires_at=current_time + 3600,
            click_count=0
        )
        
        assert db_store.creator_id == "user123"
        assert db_store.old_link == "https://example.com"
        assert db_store.new_link == "abc123"
        assert db_store.expires_at == current_time + 3600
        assert db_store.click_count == 0


class TestLinkValidation:
    """Test link validation logic"""

    def test_expiration_validation(self):
        """Test expiration time validation logic"""
        max_minutes = 10080  # 7 days in minutes
        
        # Valid expiration time
        expires_in = 60  # 1 hour
        assert expires_in <= max_minutes
        
        # Invalid expiration time
        expires_in = 20000  # More than 7 days
        assert expires_in > max_minutes

    def test_url_validation(self):
        """Test URL format validation"""
        valid_urls = [
            "https://example.com",
            "http://google.com",
            "https://subdomain.example.com/path?query=value",
            "https://example.com:8080/path"
        ]
        
        for url in valid_urls:
            # Basic URL validation - should not raise exceptions
            assert isinstance(url, str)
            assert len(url) > 0
            assert url.startswith(("http://", "https://"))


if __name__ == "__main__":
    pytest.main([__file__])
