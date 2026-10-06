"""
Minimal in-process TTL cache.

For the MVP this avoids re-hitting SerpApi for identical searches within a
short window (saving quota/cost) without introducing a Redis dependency.
This is intentionally simple; swapping in Redis later only requires
changing this file, since the rest of the app calls `cache_get`/`cache_set`.
"""
import time
from threading import Lock
from typing import Any, Dict, Optional, Tuple

_store: Dict[str, Tuple[float, Any]] = {}
_lock = Lock()


def cache_get(key: str) -> Optional[Any]:
    with _lock:
        entry = _store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.time() > expires_at:
            _store.pop(key, None)
            return None
        return value


def cache_set(key: str, value: Any, ttl_seconds: int) -> None:
    with _lock:
        _store[key] = (time.time() + ttl_seconds, value)


def cache_clear() -> None:
    """Mainly for tests."""
    with _lock:
        _store.clear()
