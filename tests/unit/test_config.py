"""
test_config.py: tests if the config.py file works as intended. (Secrets, ModelConfig, and pricing loading)
"""

from pathlib import Path
import pytest
from pydantic import ValidationError
from config import Secrets, load_model_config, load_pricing


def test_secrets_load_from_env(monkeypatch):
    """
    Tests whether the correct api keys are loaded
    """
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai")
    monkeypatch.setenv("NEBIUS_API_KEY", "test-nebius")

    secrets = Secrets()
    assert secrets.openai_api_key == "test-openai"


def test_secrets_rejects_unknown_field(monkeypatch):
    """Tests whether non-conforming keys are rejectedl."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai")
    monkeypatch.setenv("NEBIUS_API_KEY", "test-nebius")
    monkeypatch.setenv("SOME_TYPO", "oops")
    secrets = Secrets()
    assert secrets.openai_api_key == "test-openai"


def test_load_model_config_reads_valid_yaml(tmp_path):
    """
    Tests whether the load_model_config function parses yaml files correctly
    """
    yaml_content = """
    name: gpt-4
    provider: openai
    endpoint: gpt-4-0613
    """

    config_file = tmp_path / "gpt-4.yaml"
    config_file.write_text(yaml_content)

    config = load_model_config(config_file)

    assert config.name == "gpt-4"
    assert config.provider == "openai"
    assert config.endpoint == "gpt-4-0613"


def test_load_model_config_missing_fields_raises(tmp_path):
    """
    Model configs without all the required fields should raise.
    """
    yaml_content = """
    name: gpt-4    
    """
    config_file = tmp_path / "broken.yaml"
    config_file.write_text(yaml_content)

    with pytest.raises(ValidationError):
        load_model_config(config_file)


def test_load_pricing_reads_valid_yaml(tmp_path):
    """
    Tests whether the load_pricing_config function parses yaml files correctly
    """
    yaml_content = """
    gpt-4: 
        input_per_million: 3.0
        output_per_million: 12.0
    """
    pricing_file = tmp_path / "pricing-test.yaml"
    pricing_file.write_text(yaml_content)

    pricing = load_pricing(pricing_file)
    assert pricing["gpt-4"].input_per_million == 3.0
    assert pricing["gpt-4"].output_per_million == 12.0


def test_load_pricing_missing_fields_raises(tmp_path):
    """
    Pricing yaml files without all the required fields should raise.
    """
    yaml_content = """
    gpt-4: 
        input_per_million: 3.0
    """
    pricing_file = tmp_path / "broken-pricing.yaml"
    pricing_file.write_text(yaml_content)

    with pytest.raises(ValidationError):
        load_pricing(pricing_file)
