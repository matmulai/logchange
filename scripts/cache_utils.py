"""Caching utilities for API calls to reduce costs and improve performance."""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional


class APICache:
    """Simple file-based cache for API responses."""

    def __init__(self, cache_dir: str = ".logchange_cache", ttl_seconds: int = 86400):
        """
        Initialize the cache.

        Args:
            cache_dir: Directory to store cache files
            ttl_seconds: Time-to-live for cache entries (default: 24 hours)
        """
        self.cache_dir = Path(cache_dir)
        self.ttl_seconds = ttl_seconds
        self.cache_dir.mkdir(exist_ok=True)

        # Add to .gitignore if it doesn't exist
        gitignore = Path(".gitignore")
        if gitignore.exists():
            content = gitignore.read_text()
            if cache_dir not in content:
                with gitignore.open("a") as f:
                    f.write(f"\n{cache_dir}/\n")
        else:
            gitignore.write_text(f"{cache_dir}/\n")

    def _get_cache_key(self, content: str, model: str, style: str = "") -> str:
        """Generate a cache key from content and parameters."""
        key_str = f"{content}:{model}:{style}"
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{cache_key}.json"

    def get(self, content: str, model: str, style: str = "") -> Optional[str]:
        """
        Retrieve a cached response.

        Returns:
            Cached response or None if not found/expired
        """
        cache_key = self._get_cache_key(content, model, style)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        try:
            with cache_path.open("r") as f:
                data = json.load(f)

            # Check if cache has expired
            if time.time() - data["timestamp"] > self.ttl_seconds:
                cache_path.unlink()  # Delete expired cache
                return None

            return data["response"]
        except (json.JSONDecodeError, KeyError, OSError):
            # If cache file is corrupted, delete it
            if cache_path.exists():
                cache_path.unlink()
            return None

    def set(self, content: str, model: str, response: str, style: str = "") -> None:
        """
        Store a response in the cache.
        """
        cache_key = self._get_cache_key(content, model, style)
        cache_path = self._get_cache_path(cache_key)

        data = {"timestamp": time.time(), "response": response, "model": model}

        try:
            with cache_path.open("w") as f:
                json.dump(data, f)
        except OSError:
            # Silently fail if we can't write to cache
            pass

    def clear(self) -> int:
        """
        Clear all cached entries.

        Returns:
            Number of entries cleared
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except OSError:
                pass
        return count

    def clear_expired(self) -> int:
        """
        Clear only expired cache entries.

        Returns:
            Number of expired entries cleared
        """
        count = 0
        current_time = time.time()

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with cache_file.open("r") as f:
                    data = json.load(f)

                if current_time - data["timestamp"] > self.ttl_seconds:
                    cache_file.unlink()
                    count += 1
            except (json.JSONDecodeError, KeyError, OSError):
                # Delete corrupted cache files
                cache_file.unlink()
                count += 1

        return count


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, max_calls_per_minute: int = 50):
        """
        Initialize the rate limiter.

        Args:
            max_calls_per_minute: Maximum API calls allowed per minute
        """
        self.max_calls = max_calls_per_minute
        self.calls = []

    def wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded."""
        current_time = time.time()

        # Remove calls older than 1 minute
        self.calls = [t for t in self.calls if current_time - t < 60]

        if len(self.calls) >= self.max_calls:
            # Calculate how long to wait
            oldest_call = min(self.calls)
            wait_time = 60 - (current_time - oldest_call)
            if wait_time > 0:
                print(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                self.calls = []

        # Record this call
        self.calls.append(current_time)
