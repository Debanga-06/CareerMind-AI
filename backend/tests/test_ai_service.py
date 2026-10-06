import pytest

from app.services.ai_service import (
    AnthropicAIProvider,
    AIProviderUnavailable,
    NullAIProvider,
    get_ai_provider,
)


@pytest.mark.asyncio
async def test_null_provider_always_raises():
    provider = NullAIProvider()
    with pytest.raises(AIProviderUnavailable):
        await provider.generate_text("hello")


@pytest.mark.asyncio
async def test_anthropic_provider_raises_without_api_key():
    provider = AnthropicAIProvider(api_key="", model="claude-3-5-haiku-20241022")
    with pytest.raises(AIProviderUnavailable):
        await provider.generate_text("hello")


def test_get_ai_provider_defaults_to_null(monkeypatch):
    from app.core import config

    config.get_settings.cache_clear()
    monkeypatch.setenv("AI_PROVIDER", "none")
    provider = get_ai_provider()
    assert isinstance(provider, NullAIProvider)
    config.get_settings.cache_clear()


def test_get_ai_provider_unknown_falls_back_to_null(monkeypatch):
    from app.core import config

    config.get_settings.cache_clear()
    monkeypatch.setenv("AI_PROVIDER", "totally-not-a-real-provider")
    provider = get_ai_provider()
    assert isinstance(provider, NullAIProvider)
    config.get_settings.cache_clear()
