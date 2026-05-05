# backend/ai_client.py

import os
import time
from uuid import uuid4

# try:
#     from anthropic import Anthropic
# except ImportError:
#     Anthropic = None

try:
    from google import genai
except ImportError:
    genai = None

from output_parser import build_error_response, parse_ai_meal_output


DEFAULT_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
DEFAULT_MAX_TOKENS = int(os.getenv("ANTHROPIC_MAX_TOKENS", "700"))
DEFAULT_TEMPERATURE = float(os.getenv("ANTHROPIC_TEMPERATURE", "0.2"))
DEFAULT_RETRIES = int(os.getenv("ANTHROPIC_RETRIES", "2"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "3"))
GEMINI_BACKOFF_SECONDS = float(os.getenv("GEMINI_BACKOFF_SECONDS", "0.8"))

SYSTEM_PROMPT = """
You are a precise nutrition content generator for a production wellness application.
Follow the user's schema exactly, be concise, and return only the requested JSON.
Do not add markdown, explanation, or any extra wrapper text.
""".strip()

STRICT_JSON_SUFFIX = """
Return ONLY valid JSON that matches the required schema.
Do not add commentary, markdown, or code fences.
""".strip()

STRICT_JSON_INSTRUCTION = """
You must output strict JSON only. Do not include any other text.
""".strip()

# NOTE: Keep Anthropic client code for later use.
# anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")) if Anthropic else None

gemini_client = None
if genai and GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)


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

    for attempt in range(1, GEMINI_MAX_RETRIES + 1):
        started_at = time.time()

        try:
            if gemini_client is None:
                raise RuntimeError("Gemini dependency is not installed or GEMINI_API_KEY is missing.")

            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[SYSTEM_PROMPT, STRICT_JSON_INSTRUCTION, prompt],
                config={
                    "temperature": DEFAULT_TEMPERATURE,
                    "max_output_tokens": DEFAULT_MAX_TOKENS,
                    "response_mime_type": "application/json",
                },
            )

            raw_text = getattr(response, "text", "") or ""
            latency_ms = int((time.time() - started_at) * 1000)

            if not raw_text.strip():
                raise ValueError("AI response did not contain usable text.")

            return {
                "success": True,
                "raw_text": raw_text,
                "error": None,
                "meta": {
                    "request_id": request_id,
                    "model": GEMINI_MODEL,
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

            if attempt < GEMINI_MAX_RETRIES:
                time.sleep(GEMINI_BACKOFF_SECONDS * (2 ** (attempt - 1)))

    return {
        "success": False,
        "raw_text": "",
        "error": last_error,
        "meta": {
            "request_id": request_id,
            "model": DEFAULT_MODEL,
            "attempts": GEMINI_MAX_RETRIES,
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

        strict_prompt = f"{prompt}\n\n{STRICT_JSON_SUFFIX}"
        retry_result = generate_meal_from_ai_result(strict_prompt)

        if retry_result.get("success"):
            try:
                website_response = parse_ai_meal_output(retry_result["raw_text"])
                website_response["meta"] = retry_result.get("meta", {})
                return website_response
            except Exception as retry_exc:
                print(
                    "[PARSER ERROR][retry][request_id=%s]: %s"
                    % (retry_result["meta"].get("request_id"), retry_exc)
                )

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
