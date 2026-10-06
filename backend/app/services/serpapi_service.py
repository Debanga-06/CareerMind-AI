"""
SerpApi integration service.

This is the ONLY module that is allowed to talk to SerpApi. Everything
else in the codebase must go through the functions defined here so that:

  * the SERPAPI_API_KEY never leaks outside this module / never gets
    included in any response sent back to a client
  * error handling, retries, timeouts and caching are consistent
  * it is easy to unit test the rest of the app by mocking this module

Supported SerpApi engines (Stage 1 focuses on Google Jobs):
  * google_jobs    -> current job listings + requirements
  * google         -> general search for career/skill/resource research
  * google_scholar -> research papers / emerging technology signals
  * google_news    -> industry trend articles

Docs: https://serpapi.com/search-api
"""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.services.cache_service import cache_get, cache_set

logger = get_logger(__name__)


class SerpApiError(Exception):
    """Raised whenever SerpApi cannot be reached or returns an error."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class SerpApiService:
    """Thin, defensive wrapper around the SerpApi HTTP API."""

    def __init__(self) -> None:
        self._settings = get_settings()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_api_key(self) -> str:
        api_key = self._settings.SERPAPI_API_KEY
        if not api_key:
            raise SerpApiError(
                "SERPAPI_API_KEY is not configured on the server. "
                "Set it in your .env file (see .env.example)."
            )
        return api_key

    async def _request(self, params: Dict[str, Any], cache_key: str) -> Dict[str, Any]:
        """
        Perform a GET request against SerpApi with retries, timeout handling
        and a simple TTL cache so repeated identical searches (e.g. a user
        re-analyzing the same career within a few minutes) don't burn quota.
        """
        cached = cache_get(cache_key)
        if cached is not None:
            logger.debug("SerpApi cache hit for key=%s", cache_key)
            return cached

        api_key = self._require_api_key()
        request_params = {**params, "api_key": api_key}

        last_error: Optional[Exception] = None
        for attempt in range(1, self._settings.SERPAPI_MAX_RETRIES + 2):
            try:
                async with httpx.AsyncClient(timeout=self._settings.SERPAPI_TIMEOUT_SECONDS) as client:
                    response = await client.get(self._settings.SERPAPI_BASE_URL, params=request_params)

                if response.status_code == 401:
                    raise SerpApiError(
                        "SerpApi rejected the request: invalid or missing API key.",
                        status_code=401,
                    )
                if response.status_code == 429:
                    raise SerpApiError(
                        "SerpApi rate limit / quota exceeded. Try again shortly.",
                        status_code=429,
                    )
                response.raise_for_status()

                data = response.json()

                # SerpApi returns HTTP 200 even for some soft errors; surface them.
                if isinstance(data, dict) and data.get("error"):
                    raise SerpApiError(f"SerpApi error: {data['error']}", status_code=200)

                cache_set(cache_key, data, ttl_seconds=self._settings.SERPAPI_CACHE_TTL_SECONDS)
                return data

            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_error = exc
                logger.warning(
                    "SerpApi request attempt %s failed (%s). Retrying...",
                    attempt,
                    exc,
                )
                await asyncio.sleep(0.5 * attempt)
            except SerpApiError:
                raise
            except Exception as exc:  # noqa: BLE001 - defensive catch-all for a 3rd party API
                last_error = exc
                logger.exception("Unexpected error calling SerpApi")
                break

        raise SerpApiError(f"SerpApi request failed after retries: {last_error}")

    # ------------------------------------------------------------------
    # Public engines
    # ------------------------------------------------------------------

    async def google_jobs_search(
        self,
        query: str,
        location: Optional[str] = None,
        num_results: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Search Google Jobs via SerpApi and return the raw `jobs_results` list.

        Note: Google Jobs (via SerpApi) does not support a "num" parameter the
        way normal Google Search does; it returns a page of results plus a
        pagination token. For the MVP we take the first page and let the
        caller decide how many to keep/analyze.
        """
        params: Dict[str, Any] = {
            "engine": "google_jobs",
            "q": query,
            "hl": "en",
        }
        if location:
            params["location"] = location

        cache_key = f"google_jobs:{query}:{location}"
        data = await self._request(params, cache_key)

        jobs = data.get("jobs_results", [])
        if not isinstance(jobs, list):
            jobs = []
        return jobs[:num_results] if num_results else jobs

    async def google_search(
        self,
        query: str,
        num_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """General Google Search, used for career/skill/resource research."""
        params: Dict[str, Any] = {
            "engine": "google",
            "q": query,
            "num": num_results,
            "hl": "en",
        }
        cache_key = f"google_search:{query}:{num_results}"
        data = await self._request(params, cache_key)
        results = data.get("organic_results", [])
        return results if isinstance(results, list) else []

    async def google_scholar_search(
        self,
        query: str,
        num_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Google Scholar search for relevant research / emerging tech signals."""
        params: Dict[str, Any] = {
            "engine": "google_scholar",
            "q": query,
            "hl": "en",
        }
        cache_key = f"google_scholar:{query}:{num_results}"
        data = await self._request(params, cache_key)
        results = data.get("organic_results", [])
        return results[:num_results] if isinstance(results, list) else []

    async def google_news_search(
        self,
        query: str,
        num_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Google News search, used for industry trend detection."""
        params: Dict[str, Any] = {
            "engine": "google_news",
            "q": query,
            "hl": "en",
        }
        cache_key = f"google_news:{query}:{num_results}"
        data = await self._request(params, cache_key)
        results = data.get("news_results", [])
        return results[:num_results] if isinstance(results, list) else []


# Module-level singleton — stateless aside from cached settings, safe to share.
serpapi_service = SerpApiService()
