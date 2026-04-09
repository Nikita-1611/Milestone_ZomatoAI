from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request

from dotenv import load_dotenv

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"


def _call_groq(messages: list[dict[str, str]], max_tokens: int = 80) -> dict:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing in environment.")

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        GROQ_URL,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ZomatoAI/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _extract_text(response_json: dict) -> str:
    return (
        response_json.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )


def test_1_api_key_present() -> tuple[bool, str]:
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        return False, "GROQ_API_KEY is not set."
    if len(key) < 20:
        return False, "GROQ_API_KEY looks too short."
    return True, "API key is present in environment."


def test_2_basic_chat_completion() -> tuple[bool, str]:
    started = time.time()
    try:
        out = _call_groq(
            [
                {"role": "system", "content": "Reply in one short sentence."},
                {"role": "user", "content": "Say ping acknowledged."},
            ],
            max_tokens=20,
        )
        text = _extract_text(out)
        latency_ms = int((time.time() - started) * 1000)
        if not text:
            return False, "Connected, but empty model response."
        return True, f"Received non-empty response in {latency_ms}ms."
    except urllib.error.HTTPError as e:
        return False, f"HTTP error from Groq API: {e.code}."
    except Exception as e:  # noqa: BLE001
        return False, f"Connection failed: {type(e).__name__}."


def test_3_recommendation_json_style() -> tuple[bool, str]:
    prompt = (
        "You are a restaurant ranking assistant. Return ONLY valid JSON with key "
        "'recommendations' containing one item with fields "
        "restaurant_name,cuisine,rating,estimated_cost_for_two,ai_explanation. "
        "Candidates: 1) Pasta Hub, Italian, rating 4.4, cost 1400. "
        "2) Noodle Spot, Chinese, rating 4.1, cost 900. "
        "User wants Italian, medium budget, min rating 4.0."
    )
    try:
        out = _call_groq([{"role": "user", "content": prompt}], max_tokens=200)
        text = _extract_text(out)
        text = re.sub(r"^```json|```$", "", text, flags=re.MULTILINE).strip()
        parsed = json.loads(text)
        recs = parsed.get("recommendations")
        if not isinstance(recs, list) or not recs:
            return False, "Model responded but JSON shape was not as expected."
        first = recs[0]
        required = {
            "restaurant_name",
            "cuisine",
            "rating",
            "estimated_cost_for_two",
            "ai_explanation",
        }
        if not required.issubset(first.keys()):
            return False, "JSON response missing one or more required fields."
        return True, "Model produced parseable recommendation JSON."
    except json.JSONDecodeError:
        return False, "Model responded but not strict JSON."
    except Exception as e:  # noqa: BLE001
        return False, f"Recommendation-style test failed: {type(e).__name__}."


def main() -> None:
    load_dotenv()
    tests = [
        ("Test 1: API key presence", test_1_api_key_present),
        ("Test 2: Basic chat completion", test_2_basic_chat_completion),
        ("Test 3: Recommendation JSON output", test_3_recommendation_json_style),
    ]

    passed = 0
    print("Running 3 Groq smoke tests...\n")
    for name, fn in tests:
        ok, msg = fn()
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name} - {msg}")
        passed += int(ok)

    print(f"\nResult: {passed}/{len(tests)} tests passed.")
    if passed != len(tests):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
