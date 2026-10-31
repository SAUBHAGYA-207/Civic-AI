import json
import re
import time
import asyncio
from typing import Any, Optional
import httpx
from ollama import Client as OllamaSdkClient
from backend.app.config import settings

# Global semaphore to enforce sequential model execution (protect 8GB RAM / CPU)
_model_execution_lock = asyncio.Lock()

class OllamaClientWrapper:
    def __init__(self):
        self.host = settings.OLLAMA_HOST
        self.client = OllamaSdkClient(host=self.host)
        self.vision_model = settings.VISION_MODEL
        self.text_model = settings.TEXT_MODEL
        self.timeout = settings.MODEL_TIMEOUT_SECONDS
        self.max_retries = settings.MODEL_MAX_RETRIES

    def check_health(self) -> dict[str, Any]:
        """Verify Ollama host connectivity and installed models."""
        try:
            models_info = self.client.list()
            available = [m.model for m in models_info.models]
            has_vision = any(self.vision_model in m for m in available)
            has_text = any(self.text_model in m for m in available)
            return {
                "status": "healthy" if (has_vision and has_text) else "warning",
                "host": self.host,
                "available_models": available,
                "vision_model_configured": self.vision_model,
                "vision_model_ready": has_vision,
                "text_model_configured": self.text_model,
                "text_model_ready": has_text,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "host": self.host,
                "error": str(e),
                "vision_model_configured": self.vision_model,
                "text_model_configured": self.text_model,
            }

    @staticmethod
    def clean_json_response(raw_text: str) -> dict[str, Any]:
        """Extract and parse valid JSON from text, handling potential codeblocks or preamble."""
        text = raw_text.strip()
        # Strip markdown fences if present
        if "```" in text:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
            if match:
                text = match.group(1).strip()
        # Find start of JSON object or array
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            text = text[start_idx:end_idx + 1]

        return json.loads(text)

    async def chat_with_model(
        self,
        model: str,
        messages: list[dict[str, Any]],
        format_schema: Optional[dict[str, Any]] = None,
        temperature: float = 0.0,
    ) -> tuple[dict[str, Any], float]:
        """
        Executes a chat completion with strict sequential concurrency locking,
        bounded retries, and timing tracking.
        Returns: (parsed_json_dict, duration_seconds)
        """
        async with _model_execution_lock:
            start_time = time.perf_counter()
            last_err = None

            for attempt in range(1, self.max_retries + 1):
                try:
                    # Run synchronous Ollama SDK call inside thread pool with timeout
                    options = {
                        "temperature": temperature,
                    }
                    kwargs: dict[str, Any] = {
                        "model": model,
                        "messages": messages,
                        "options": options,
                    }
                    if format_schema:
                        kwargs["format"] = format_schema
                    else:
                        kwargs["format"] = "json"

                    def _run_chat():
                        return self.client.chat(**kwargs)

                    response = await asyncio.wait_for(
                        asyncio.to_thread(_run_chat),
                        timeout=self.timeout
                    )
                    content = response["message"]["content"]
                    parsed = self.clean_json_response(content)
                    duration = round(time.perf_counter() - start_time, 2)
                    return parsed, duration

                except asyncio.TimeoutError:
                    last_err = TimeoutError(f"Model {model} timed out after {self.timeout}s on attempt {attempt}")
                except Exception as e:
                    last_err = e

                # Small delay before retry
                await asyncio.sleep(1.0)

            duration = round(time.perf_counter() - start_time, 2)
            raise RuntimeError(f"Ollama execution failed for model {model} after {self.max_retries} attempts: {last_err}")

ollama_client = OllamaClientWrapper()
