import time
from typing import Any, Dict, List, Optional, Tuple, Type
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import get_settings
from app.utils.logger import logger

settings = get_settings()

FALLBACK_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.7-flash",
    "gemini-flash-latest",
]


def get_llm(
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_retries: int = 3,
) -> ChatGoogleGenerativeAI:
    """
    Instantiate and configure ChatGoogleGenerativeAI instance.
    Defaults to GEMINI_MODEL from config.
    """
    api_key = settings.GOOGLE_API_KEY
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY is not set in environment or .env file. "
            "Please configure your Google Gemini API key."
        )

    chosen_model = model or settings.GEMINI_MODEL

    return ChatGoogleGenerativeAI(
        model=chosen_model,
        google_api_key=api_key,
        temperature=temperature,
        max_retries=max_retries,
    )


def test_llm_connection(model: Optional[str] = None) -> Tuple[bool, str, float]:
    """
    Test connectivity to Google Gemini API with a minimal probe prompt across fallback candidates.
    Returns (success: bool, message: str, latency_ms: float).
    """
    primary = model or settings.GEMINI_MODEL
    candidate_models = [primary] if model else [primary] + [m for m in FALLBACK_MODELS if m != primary]

    last_error = None
    start_time = time.time()

    for candidate in candidate_models:
        try:
            llm = get_llm(model=candidate, temperature=0.0)
            response = llm.invoke("Respond with the exact word: OK")
            latency_ms = (time.time() - start_time) * 1000

            content = response.content
            if isinstance(content, list):
                content = " ".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
            content = str(content).strip()

            logger.info(f"Gemini API connection successful ({llm.model}) in {latency_ms:.2f}ms: '{content}'")
            return True, f"Gemini ({llm.model}) connected. Response: '{content}'", latency_ms

        except Exception as e:
            last_error = e
            logger.warning(f"Gemini connection probe failed for '{candidate}': {e}. Trying fallback...")

    latency_ms = (time.time() - start_time) * 1000
    sanitized_error = str(last_error)
    if settings.GOOGLE_API_KEY:
        sanitized_error = sanitized_error.replace(settings.GOOGLE_API_KEY, "[REDACTED_API_KEY]")

    logger.error(f"All Gemini candidate connection tests failed in {latency_ms:.2f}ms: {sanitized_error}")
    return False, sanitized_error, latency_ms


def generate_structured_output(
    prompt: str,
    schema: Type[BaseModel],
    model: Optional[str] = None,
    temperature: float = 0.0,
) -> BaseModel:
    """
    Invoke Gemini and parse response directly into a Pydantic schema.
    Includes automated fallback across configured candidate models.
    """
    primary_model = model or settings.GEMINI_MODEL
    candidate_models = [primary_model] + [m for m in FALLBACK_MODELS if m != primary_model]

    last_error = None
    for candidate in candidate_models:
        try:
            llm = get_llm(model=candidate, temperature=temperature)
            structured_llm = llm.with_structured_output(schema)
            result = structured_llm.invoke(prompt)
            return result
        except Exception as e:
            last_error = e
            logger.warning(f"Structured output attempt failed on '{candidate}': {e}. Trying next fallback...")

    logger.error(f"All candidate models exhausted for structured output: {last_error}")
    raise last_error or RuntimeError("Failed to generate structured output from Gemini.")
