"""Simple caching layer for improved performance."""

from __future__ import annotations

import hashlib
import json
import os
import pickle
import time
from typing import Any, Optional


class SearchCache:
    """LRU-like cache with disk persistence for search results."""
    
    def __init__(self, max_size: int = 100, ttl: int = 300, cache_dir: str = ".cache"):
        self.max_size = max_size
        self.ttl = ttl
        self.cache_dir = cache_dir
        self._memory_cache: dict = {}
        self._access_times: dict = {}
        
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
    
    def _make_key(self, query: str, model: str, k: int) -> str:
        """Generate cache key from query parameters."""
        raw = f"{query}:{model}:{k}"
        return hashlib.md5(raw.encode()).hexdigest()
    
    def _cache_path(self, key: str) -> str:
        return os.path.join(self.cache_dir, f"{key}.cache")
    
    def get(self, query: str, model: str, k: int) -> Optional[Any]:
        """Retrieve cached result if exists and not expired."""
        key = self._make_key(query, model, k)
        
        # Check memory cache first
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            if time.time() - entry["time"] < self.ttl:
                self._access_times[key] = time.time()
                return entry["data"]
            else:
                del self._memory_cache[key]
        
        # Check disk cache
        path = self._cache_path(key)
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    entry = pickle.load(f)
                if time.time() - entry["time"] < self.ttl:
                    self._memory_cache[key] = entry
                    self._access_times[key] = time.time()
                    return entry["data"]
            except Exception:
                os.remove(path)
        
        return None
    
    def set(self, query: str, model: str, k: int, data: Any):
        """Cache search result."""
        key = self._make_key(query, model, k)
        entry = {"data": data, "time": time.time()}
        
        # Manage memory cache size
        if len(self._memory_cache) >= self.max_size:
            # Remove least recently used
            oldest = min(self._access_times, key=self._access_times.get)
            del self._memory_cache[oldest]
            del self._access_times[oldest]
        
        self._memory_cache[key] = entry
        self._access_times[key] = time.time()
        
        # Persist to disk
        try:
            path = self._cache_path(key)
            with open(path, "wb") as f:
                pickle.dump(entry, f)
        except Exception:
            pass
    
    def clear(self):
        """Clear all cached results."""
        self._memory_cache.clear()
        self._access_times.clear()
        if os.path.exists(self.cache_dir):
            for f in os.listdir(self.cache_dir):
                try:
                    os.remove(os.path.join(self.cache_dir, f))
                except Exception:
                    pass


# Global cache instance
search_cache = SearchCache()
