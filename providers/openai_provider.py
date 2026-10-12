"""
openai_provider.py: OpenAI implementation of the BatchProvider protocol.
"""

import json
import base64
from pathlib import Path
from openai import OpenAI

from providers.base import BatchProvider, RawResponse, BatchStatus, PromptRequest

BATCH_DIR = Path("runs/batches")
MAX_BATCH_FILE_BYTES = 190 * 1024 * 1024  # safe margin under OpenAI's 200 MB limit


class OpenAIProvider:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self._uploaded_files: dict[str, str] = {}

    def _get_or_encode_image(self, image_path: str) -> str:
        if image_path in self._uploaded_files:
            return self._uploaded_files[image_path]

        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")

        self._uploaded_files[image_path] = encoded
        return encoded

    def _build_batch_line(self, request: PromptRequest) -> dict:
        content = [{"type": "input_text", "text": request.prompt}]

        if request.image_path is not None:
            encoded_image = self._get_or_encode_image(request.image_path)
            content.append(
                {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{encoded_image}",
                }
            )

        return {
            "custom_id": request.custom_id,
            "method": "POST",
            "url": "/v1/responses",
            "body": {
                "model": request.endpoint,
                "input": [{"role": "user", "content": content}],
            },
        }

    def submit_batch(self, requests: list[PromptRequest]) -> str:
        BATCH_DIR.mkdir(parents=True, exist_ok=True)

        lines = []
        total_bytes = 0
        for i, request in enumerate(requests):
            line = self._build_batch_line(request)
            lines.append(line)
            total_bytes += len(json.dumps(line).encode("utf-8"))
            if (i + 1) % 100 == 0 or (i + 1) == len(requests):
                print(
                    f"Built {i + 1}/{len(requests)} requests... ({total_bytes / (1024**2):.1f} MB)"
                )

        if total_bytes > MAX_BATCH_FILE_BYTES:
            raise ValueError(
                f"Batch file would be {total_bytes / (1024**2):.1f} MB, over the "
                f"{MAX_BATCH_FILE_BYTES / (1024**2):.0f} MB safe limit. Lower --max-per-batch."
            )

        batch_file_path = BATCH_DIR / "batch_input.jsonl"
        with open(batch_file_path, "w") as f:
            for line in lines:
                f.write(json.dumps(line) + "\n")

        with open(batch_file_path, "rb") as f:
            uploaded_file = self.client.files.create(file=f, purpose="batch")

        batch = self.client.batches.create(
            input_file_id=uploaded_file.id,
            endpoint="/v1/responses",
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

        if batch.output_file_id is None:
            raise RuntimeError(
                f"Batch {batch_id} status={batch.status} but has no output_file_id."
            )

        result_file = self.client.files.content(batch.output_file_id)
        lines = result_file.text.strip().split("\n")

        return [self._parse_batch_line(line) for line in lines]

    def _parse_batch_line(self, line: str) -> RawResponse:
        data = json.loads(line)
        custom_id = data["custom_id"]
        body = data["response"]["body"]

        message_block = next(
            item for item in body["output"] if item["type"] == "message"
        )
        content = message_block["content"][0]["text"]
        usage = body["usage"]

        return RawResponse(
            custom_id=custom_id,
            content=content,
            input_tokens=usage["input_tokens"],
            output_tokens=usage["output_tokens"],
        )
