from __future__ import annotations

import json
import urllib.error
import urllib.request

from backend.config import load_backend_settings

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"


class LLMClientError(Exception):
    pass


def run_groq_chat(messages: list[dict[str, str]], max_tokens: int = 500) -> str:
    settings = load_backend_settings()
    if not settings.groq_api_key:
        raise LLMClientError("GROQ_API_KEY is missing.")

    payload = {
        "model": settings.groq_model,
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }
    body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        GROQ_CHAT_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ZomatoAI/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            response_json = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise LLMClientError(f"Groq HTTP error: {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise LLMClientError("Unable to reach Groq endpoint.") from exc

    content = (
        response_json.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )
    if not content:
        raise LLMClientError("Empty content from Groq response.")
    return content
