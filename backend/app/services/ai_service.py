"""
AI provider abstraction.

Design goals
------------
* Calling code (roadmap_service.py, etc.) never talks to a specific AI
  vendor directly — only to this abstraction — so swapping or adding a
  provider later means changing this file, not every caller.
* When no provider is configured (the hackathon-safe default), every
  method raises `AIProviderUnavailable` rather than returning fabricated
  text. Callers are expected to catch this and fall back to the
  deterministic, rule-based generation already implemented in
  roadmap_service.py / project_service.py — so the product works even
  with zero AI spend, and gets richer automatically once a real key is
  configured.

Configured via env vars (see .env.example):
  AI_PROVIDER = "none" | "anthropic"
  AI_API_KEY  = provider API key (never logged, never returned to clients)
  AI_MODEL    = model name/id for the chosen provider
"""
from __future__ import annotations

from abc import ABC, abstractmethod

import httpx

from app.core.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

DEFAULT_ANTHROPIC_MODEL = "claude-3-5-haiku-20241022"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


class AIProviderUnavailable(Exception):
    """Raised when no usable AI provider is configured, or the call fails."""


class AIProvider(ABC):
    name: str = "unset"

    @abstractmethod
    async def generate_text(self, prompt: str, max_tokens: int = 600) -> str:
        """Return generated text for the given prompt, or raise AIProviderUnavailable."""
        raise NotImplementedError


class NullAIProvider(AIProvider):
    """Default provider: always unavailable. Keeps the app fully functional
    (via rule-based fallbacks) with zero AI configuration and zero cost."""

    name = "none"

    async def generate_text(self, prompt: str, max_tokens: int = 600) -> str:
        raise AIProviderUnavailable(
            "No AI provider is configured (AI_PROVIDER=none). "
            "Falling back to rule-based generation."
        )


class AnthropicAIProvider(AIProvider):
    """Minimal Anthropic Messages API client, used only to enrich/narrate
    output that already has a deterministic rule-based fallback."""

    name = "anthropic"

    def __init__(self, api_key: str, model: str):
        self._api_key = api_key
        self._model = model or DEFAULT_ANTHROPIC_MODEL

    async def generate_text(self, prompt: str, max_tokens: int = 600) -> str:
        if not self._api_key:
            raise AIProviderUnavailable(
                "AI_PROVIDER=anthropic but AI_API_KEY is not set in the environment."
            )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    ANTHROPIC_API_URL,
                    headers={
                        "x-api-key": self._api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": self._model,
                        "max_tokens": max_tokens,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            raise AIProviderUnavailable(f"Could not reach Anthropic API: {exc}") from exc

        if response.status_code != 200:
            raise AIProviderUnavailable(
                f"Anthropic API returned {response.status_code}: {response.text[:300]}"
            )

        data = response.json()
        text_blocks = [
            block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
        ]
        result = "\n".join(text_blocks).strip()
        if not result:
            raise AIProviderUnavailable("Anthropic API returned no text content.")
        return result


def get_ai_provider() -> AIProvider:
    """Factory: returns the configured AI provider, defaulting safely to NullAIProvider."""
    settings = get_settings()
    provider_name = (settings.AI_PROVIDER or "none").strip().lower()

    if provider_name == "anthropic":
        return AnthropicAIProvider(settings.AI_API_KEY, settings.AI_MODEL)

    if provider_name != "none":
        logger.warning("Unknown AI_PROVIDER=%s; falling back to no-op provider.", provider_name)

    return NullAIProvider()
