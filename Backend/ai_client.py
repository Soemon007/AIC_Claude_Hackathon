# backend/ai_client.py

import os
import time
from uuid import uuid4

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

from output_parser import build_error_response, parse_ai_meal_output


DEFAULT_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
DEFAULT_MAX_TOKENS = int(os.getenv("ANTHROPIC_MAX_TOKENS", "700"))
DEFAULT_TEMPERATURE = float(os.getenv("ANTHROPIC_TEMPERATURE", "0.2"))
DEFAULT_RETRIES = int(os.getenv("ANTHROPIC_RETRIES", "2"))

SYSTEM_PROMPT = """
You are a precise nutrition content generator for a production wellness application.
Follow the user's schema exactly, be concise, and return only the requested JSON.
Do not add markdown, explanation, or any extra wrapper text.
""".strip()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")) if Anthropic else None


def generate_meal_from_ai(prompt: str) -> str:
    result = generate_meal_from_ai_result(prompt)
    return result.get("raw_text", "")


def generate_meal_from_ai_result(prompt: str) -> dict:
    request_id = str(uuid4())
    last_error = None

    if not prompt or not prompt.strip():
        return {
            "success": False,
            "raw_text": "",
            "error": {
                "type": "validation_error",
                "message": "Prompt is empty.",
            },
            "meta": {
                "request_id": request_id,
                "model": DEFAULT_MODEL,
                "attempts": 0,
                "latency_ms": 0,
            },
        }

    for attempt in range(1, DEFAULT_RETRIES + 2):
        started_at = time.time()

        try:
            if client is None:
                raise RuntimeError("anthropic dependency is not installed.")

            response = client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=DEFAULT_MAX_TOKENS,
                temperature=DEFAULT_TEMPERATURE,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )

            raw_text = extract_text_from_response(response)
            latency_ms = int((time.time() - started_at) * 1000)

            if not raw_text.strip():
                raise ValueError("AI response did not contain usable text.")

            return {
                "success": True,
                "raw_text": raw_text,
                "error": None,
                "meta": {
                    "request_id": request_id,
                    "model": DEFAULT_MODEL,
                    "attempts": attempt,
                    "latency_ms": latency_ms,
                    "stop_reason": getattr(response, "stop_reason", None),
                },
            }

        except Exception as exc:
            latency_ms = int((time.time() - started_at) * 1000)
            last_error = {
                "type": "provider_error",
                "message": str(exc),
            }
            print(f"[AI ERROR][attempt={attempt}][request_id={request_id}][latency_ms={latency_ms}]: {exc}")

            if attempt <= DEFAULT_RETRIES:
                time.sleep(0.6 * attempt)

    return {
        "success": False,
        "raw_text": "",
        "error": last_error,
        "meta": {
            "request_id": request_id,
            "model": DEFAULT_MODEL,
            "attempts": DEFAULT_RETRIES + 1,
            "latency_ms": None,
        },
    }


def generate_website_meal_response(prompt: str) -> dict:
    """
    Generate a meal with AI and return a website-deliverable payload.
    """

    ai_result = generate_meal_from_ai_result(prompt)

    if not ai_result.get("success"):
        error = ai_result.get("error") or {}
        response = build_error_response(error.get("message", "AI did not return a response."))
        response["meta"] = ai_result.get("meta", {})
        response["error_type"] = error.get("type", "provider_error")
        return response

    try:
        website_response = parse_ai_meal_output(ai_result["raw_text"])
        website_response["meta"] = ai_result.get("meta", {})
        return website_response
    except Exception as exc:
        print(f"[PARSER ERROR][request_id={ai_result['meta']['request_id']}]: {exc}")
        response = build_error_response(str(exc))
        response["meta"] = ai_result.get("meta", {})
        response["error_type"] = "parser_error"
        response["raw_output"] = ai_result.get("raw_text", "")
        return response


def extract_text_from_response(response) -> str:
    blocks = getattr(response, "content", []) or []
    text_parts = []

    for block in blocks:
        block_type = getattr(block, "type", None)
        if block_type == "text":
            text_value = getattr(block, "text", "")
            if text_value:
                text_parts.append(text_value)

    return "\n".join(text_parts).strip()
