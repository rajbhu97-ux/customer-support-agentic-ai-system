from backend.llm.providers.google import GoogleProvider
from backend.llm.providers.mock import MockProvider
from backend.llm.providers.base import BaseLLMProvider
from backend.llm.providers.bedrock import BedRockProvider
from langchain_core.language_models import BaseChatModel
from config.settings import settings
from typing import Any, Type


PROVIDER_REGISTRY = {
    "google": GoogleProvider,
    "mock": MockProvider,
    "bedrock": BedRockProvider,
}

_provider_instances: dict[str, BaseLLMProvider] = {}


def get_provider(provider_name: str) -> BaseLLMProvider:
    if provider_name in _provider_instances:
        return _provider_instances[provider_name]
    provider_class = PROVIDER_REGISTRY.get(provider_name)
    if not provider_class:
        raise ValueError(
            f"Unknown provider '{provider_name}'. Valid options: {list(PROVIDER_REGISTRY.keys())}"
        )
    provider_class_object = provider_class()
    _provider_instances[provider_name] = provider_class_object
    return provider_class_object


def get_llm(temperature: float = 0.0) -> BaseChatModel:

    provider = settings.LLM_PROVIDER.lower()
    if settings.MOCK_LLM:
        provider = "mock"
    return get_provider(provider).get_llm(temperature)


def get_structured_llm(structure: Type[Any], temperature: float = 0.0) -> BaseChatModel:
    provider = settings.LLM_PROVIDER.lower()
    return get_provider(provider).get_structured_llm(structure, temperature)
