"""
registry.py: maps provider names to their classes
"""

from providers.base import BatchProvider
from providers.openai_provider import OpenAIProvider
from providers.nebius_provider import NebiusProvider

# from providers.nebius_provider import NebiusProvider

PROVIDERS: dict[str, type] = {
    "openai": OpenAIProvider,
    "nebius": NebiusProvider,
}


def get_provider(name: str, *args, **kwargs) -> BatchProvider:
    """
    Looks up a provider class by name and constructs it.
    Raises ValueError if the name isn't registered.
    """
    if name not in PROVIDERS:
        raise ValueError(f"Unknown provider: {name}")
    provider_class = PROVIDERS[name]
    return provider_class(*args, **kwargs)
