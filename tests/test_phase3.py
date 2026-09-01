"""
Phase 3 automated tests: Google Gemini API integration, Structured Pydantic Output,
and Error Handling.
"""

import os
import pytest
from app.config import get_settings
from app.services.llm_service import (
    get_llm,
    test_llm_connection,
    generate_structured_output,
)
from app.prompts.test_prompts import SimpleIntentTest


def test_gemini_client_initialization():
    """Verify that get_llm instantiates ChatGoogleGenerativeAI with configured settings."""
    llm = get_llm()
    assert llm is not None
    assert llm.model == get_settings().GEMINI_MODEL
    assert llm.temperature == 0.0


def test_gemini_connectivity():
    """Verify live communication with Gemini model."""
    success, msg, latency = test_llm_connection()
    assert success is True, f"Gemini connection test failed: {msg}"
    assert latency > 0
    assert "connected" in msg.lower()


def test_gemini_structured_pydantic_output():
    """Verify that Gemini generates valid structured Pydantic objects."""
    prompt = "Extract analytical intent from: 'What were our top 5 selling products in Chennai in 2023?'"
    result: SimpleIntentTest = generate_structured_output(prompt, SimpleIntentTest)

    assert result is not None
    assert isinstance(result, SimpleIntentTest)
    assert result.intent is not None
    assert len(result.intent) > 0
    assert result.metric is not None


def test_gemini_missing_api_key_handling(monkeypatch):
    """Verify that clear ValueError is raised if API key is missing."""
    settings = get_settings()
    original_key = settings.GOOGLE_API_KEY
    try:
        settings.GOOGLE_API_KEY = ""
        with pytest.raises(ValueError) as exc_info:
            get_llm()
        assert "GOOGLE_API_KEY" in str(exc_info.value)
    finally:
        settings.GOOGLE_API_KEY = original_key
