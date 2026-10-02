import base64
import json
import logging
from typing import Any
from app.config import settings

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

logger = logging.getLogger(__name__)
FALLBACK_MODEL = "gemini-flash-lite-latest"
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

def _client():
    if not settings.ai_enabled or genai is None:
        return None
    return genai.Client(api_key=settings.gemini_api_key)

def generate_plan(prompt: str, image_data_url: str | None = None) -> dict[str, Any] | None:
    """Generate structured JSON. Returns None on missing key, SDK failure, or invalid output."""
    client = _client()
    if client is None:
        return None

    contents: list[Any] = [prompt]
    if image_data_url and "," in image_data_url:
        header, encoded = image_data_url.split(",", 1)
        mime = header.split(";")[0].split(":", 1)[-1]
        try:
            contents.append(types.Part.from_bytes(data=base64.b64decode(encoded), mime_type=mime))
        except Exception:
            pass

    schema = {
        "type": "OBJECT",
        "properties": {
            "summary": {"type": "STRING"},
            "recommendations": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "title": {"type": "STRING"},
                        "category": {"type": "STRING"},
                        "platform": {"type": "STRING"},
                        "estimated_price": {"type": "NUMBER"},
                        "reason": {"type": "STRING"},
                        "url": {"type": "STRING"},
                        "tags": {"type": "ARRAY", "items": {"type": "STRING"}},
                    },
                    "required": ["title", "category", "platform", "estimated_price", "reason", "url", "tags"],
                },
            },
            "tips": {"type": "ARRAY", "items": {"type": "STRING"}},
        },
        "required": ["summary", "recommendations", "tips"],
    }

    models = [settings.gemini_model]
    if FALLBACK_MODEL.casefold() != settings.gemini_model.casefold():
        models.append(FALLBACK_MODEL)

    for index, model in enumerate(models):
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )
            result = json.loads(response.text)
            result["_model_used"] = model
            return result
        except Exception as exc:
            status_code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
            if index == 0 and status_code in RETRYABLE_STATUS_CODES and len(models) > 1:
                logger.warning(
                    "Gemini model %s returned a temporary error (%s); retrying with %s",
                    model,
                    status_code,
                    FALLBACK_MODEL,
                )
                continue
            logger.warning("Gemini request failed for model %s (%s)", model, type(exc).__name__)
            return None
    return None
