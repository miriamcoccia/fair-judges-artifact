"""
nebius_provider.py: Nebius implementation of the BatchProvider protocol.
"""

import json
from pathlib import Path
from openai import OpenAI
import base64

from providers.base import BatchProvider, RawResponse, BatchStatus, PromptRequest

BATCH_DIR = Path("runs/batches")


class NebiusProvider:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            base_url="https://api.tokenfactory.nebius.com/v1/", api_key=api_key
        )
        self._encoded_images: dict[str, str] = {}

    def _get_or_encode_image(self, image_path: str) -> str:
        if image_path in self._encoded_images:
            return self._encoded_images[image_path]

        with open(image_path, "rb") as f:
            result = base64.b64encode(f.read()).decode("utf-8")

        self._encoded_images[image_path] = result
        return result

    def _build_batch_line(self, request: PromptRequest) -> dict:
        content = [{"type": "text", "text": request.prompt}]

        if request.image_path is not None:
            encoded_image = self._get_or_encode_image(request.image_path)
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64, {encoded_image}"},
                }
            )

        return {
            "custom_id": request.custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "Qwen/Qwen2.5-VL-72B-Instruct",  # placeholder for now
                "messages": [{"role": "user", "content": content}],
            },
        }

    def submit_batch(self, requests: list[PromptRequest]) -> str:
        BATCH_DIR.mkdir(parents=True, exist_ok=True)

        lines = [self._build_batch_line(r) for r in requests]

        batch_file_path = BATCH_DIR / "batch_input.jsonl"
        with open(batch_file_path, "w") as f:
            for line in lines:
                f.write(json.dumps(line) + "\n")

        with open(batch_file_path, "rb") as f:
            uploaded_file = self.client.files.create(file=f, purpose="batch")

        batch = self.client.batches.create(
            input_file_id=uploaded_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )

        return batch.id

    def check_batch_status(self, batch_id: str) -> BatchStatus:
        batch = self.client.batches.retrieve(batch_id)

        if batch.status == "completed":
            return BatchStatus.COMPLETED
        elif batch.status in ("failed", "expired", "cancelled"):
            return BatchStatus.FAILED
        else:
            return BatchStatus.PENDING

    def fetch_batch(self, batch_id: str) -> list[RawResponse]:
        batch = self.client.batches.retrieve(batch_id)

        result_file = self.client.files.content(batch.output_file_id)
        lines = result_file.text.strip().split("\n")

        return [self._parse_batch_line(line) for line in lines]

    def _parse_batch_line(self, line: str) -> RawResponse:
        data = json.loads(line)
        custom_id = data["custom_id"]
        body = data["response"]["body"]

        content = body["choices"][0]["message"]["content"]
        usage = body["usage"]

        return RawResponse(
            custom_id=custom_id,
            content=content,
            input_tokens=usage["prompt_tokens"],
            output_tokens=usage["completion_tokens"],
        )
