"""
Very small in-process rate limiter (per client IP).

This is an MVP-level building block, not a distributed rate limiter.
For production/multi-instance deployments, swap this for a Redis-backed
limiter (e.g. token bucket in Redis) — the FastAPI dependency below is
the only place that would need to change.
"""
import time
from collections import defaultdict, deque
from threading import Lock
from typing import Deque, Dict

from fastapi import HTTPException, Request, status

from app.core.config import get_settings

_hits: Dict[str, Deque[float]] = defaultdict(deque)
_lock = Lock()


def _client_key(request: Request) -> str:
    if request.client:
        return request.client.host
    return "unknown"


async def rate_limit_dependency(request: Request) -> None:
    settings = get_settings()
    window = settings.RATE_LIMIT_WINDOW_SECONDS
    limit = settings.RATE_LIMIT_REQUESTS

    key = _client_key(request)
    now = time.time()

    with _lock:
        bucket = _hits[key]
        while bucket and now - bucket[0] > window:
            bucket.popleft()

        if len(bucket) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please slow down and try again shortly.",
            )

        bucket.append(now)
