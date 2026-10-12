"""
test_nebius_provider.py: tests for NebiusProvider's parsing logic.
"""

import json
from providers.nebius_provider import NebiusProvider
from providers.base import PromptRequest


def test_parse_batch_line():
    fake_line = json.dumps(
        {
            "custom_id": "test_id_1",
            "response": {
                "body": {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": '{"verdicts": []}',
                            }
                        }
                    ],
                    "usage": {"prompt_tokens": 100, "completion_tokens": 20},
                }
            },
        }
    )

    provider = NebiusProvider(api_key="fake-key-not-used")
    result = provider._parse_batch_line(fake_line)

    assert result.content == '{"verdicts": []}'
    assert result.input_tokens == 100
    assert result.output_tokens == 20


def test_build_batch_line_with_image():
    provider = NebiusProvider(api_key="fake-key-not-used")
    provider._encoded_images["fake_image.png"] = "fakebase64content"

    request = PromptRequest(
        custom_id="q1",
        prompt="test prompt",
        image_path="fake_image.png",
        endpoint="test-endpoint",
    )
    line = provider._build_batch_line(request)

    assert line["custom_id"] == "q1"
    assert line["url"] == "/v1/chat/completions"
    content = line["body"]["messages"][0]["content"]
    assert content[0]["type"] == "text"
    assert content[1]["type"] == "image_url"
