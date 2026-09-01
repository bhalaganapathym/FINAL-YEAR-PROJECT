"""
Phase 3 Verification Script: Google Gemini API Integration.
Tests:
1. LLM Client initialization
2. Basic prompt round-trip
3. Structured output parsing via Pydantic model
"""

import sys
import time
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from app.config import get_settings
from app.services.llm_service import get_llm, test_llm_connection, generate_structured_output
from app.prompts.test_prompts import SimpleIntentTest

print("==================================================")
print("  PHASE 3 VERIFICATION: GOOGLE GEMINI API         ")
print("==================================================")

settings = get_settings()
print(f"--> 1. Checking Configuration...")
print(f"    Configured Model: {settings.GEMINI_MODEL}")
print(f"    API Key Configured: {'Yes (length ' + str(len(settings.GOOGLE_API_KEY)) + ')' if settings.GOOGLE_API_KEY else 'NO'}")

print(f"\n--> 2. Testing Basic Gemini API Connectivity...")
success, msg, latency = test_llm_connection()
print(f"    Status: {'SUCCESS' if success else 'FAILED'}")
print(f"    Latency: {latency:.2f}ms")
print(f"    Message: {msg}")
assert success, f"Gemini connection failed: {msg}"

print(f"\n--> 3. Testing Natural Language Prompt Invocation...")
llm = get_llm()
start_t = time.time()
response = llm.invoke("You are an AI Data Analyst. In one short sentence, introduce your capability.")
duration = (time.time() - start_t) * 1000

content = response.content
if isinstance(content, list):
    content = " ".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
content = str(content).strip()

print(f"    Response [{duration:.2f}ms]:\n    \"{content}\"")

print(f"\n--> 4. Testing Structured Pydantic Output Generation...")
test_query = "Show total monthly revenue by region for 2024."
print(f"    Test Query: \"{test_query}\"")
prompt = f"Analyze the analytical intent and entities in this user query:\n\n\"{test_query}\""

start_t = time.time()
structured_result: SimpleIntentTest = generate_structured_output(prompt, SimpleIntentTest)
duration = (time.time() - start_t) * 1000

print(f"    Structured Output [{duration:.2f}ms]:")
print(f"      - Intent: {structured_result.intent}")
print(f"      - Metric: {structured_result.metric}")
print(f"      - Dimensions: {structured_result.dimensions}")
print(f"      - Time Filter: {structured_result.time_filter}")
print(f"      - Requires Visualization: {structured_result.requires_visualization}")

assert structured_result.intent, "Intent should not be empty"
assert "revenue" in structured_result.metric.lower() or "sales" in structured_result.metric.lower()
print("\n[PASS] Structured Output Parsed Successfully.")

print("\n=== PHASE 3 VERIFICATION COMPLETE: ALL CHECKS PASSED ===")
