"""
config.py: This file contains the instructions to handle various I/O operations safely
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, ConfigDict
import yaml
from pathlib import Path
from decimal import Decimal
from typing import Optional


class Secrets(BaseSettings):
    """
    Reads API keys from environment variables (or a .env file).
    Never commit real values.
    """

    model_config = SettingsConfigDict(extra="forbid", env_file=".env")

    openai_api_key: str
    nebius_api_key: str


class ModelConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    provider: str
    endpoint: str
    temperature: Optional[float] = None


class ModelPricing(BaseModel):
    """
    Pricing info for one AI model, loaded from configs/pricing.yaml
    """

    model_config = ConfigDict(extra="forbid")

    input_per_million: Decimal
    output_per_million: Decimal


def load_model_config(path: Path) -> ModelConfig:
    """
    Reads a YAML file and returns a validated ModelConfig.
    Raises yaml.YAMLError if the file isn't valid YAML,
    or pydantic.ValidationError if the fields don't match ModelConfig.
    """
    with open(path) as file:
        data = yaml.safe_load(file)
    return ModelConfig(**data)


def load_all_model_configs(configs_dir: Path) -> dict[str, ModelConfig]:
    """
    Loads every model YAML file in configs_dir into a dict, keyed by model name.
    """
    configs = {}
    for yaml_file in configs_dir.glob("*.yaml"):
        model_config = load_model_config(yaml_file)
        configs[model_config.name] = model_config
    return configs


def openai_model_names(model_configs: dict) -> list[str]:
    """
    Returns the names of all models whose provider is "openai" —
    used to scope real runs to OpenAI only, given Nebius/Anthropic
    are currently excluded.
    """
    return [
        name for name, config in model_configs.items() if config.provider == "openai"
    ]


def load_pricing(path: Path) -> dict[str, ModelPricing]:
    """
    Reads pricing.yaml and eturns a dict mapping model name -> ModelPricing.
    """
    with open(path) as file:
        data = yaml.safe_load(file)
        return {key: ModelPricing(**value) for key, value in data.items()}
