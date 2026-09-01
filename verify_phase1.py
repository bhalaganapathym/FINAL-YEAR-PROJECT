"""
Direct verification script for Phase 1.
Spins up FastAPI test client and checks all basic routes and imports.
"""

import sys
from importlib.metadata import version
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from fastapi.testclient import TestClient
from app.main import app
from app.config import get_settings

print("--> 1. Testing Configuration Loading...")
settings = get_settings()
print(f"    Backend Host: {settings.BACKEND_HOST}:{settings.BACKEND_PORT}")
print(f"    Gemini Model: {settings.GEMINI_MODEL}")
print(f"    Database URL Format: {settings.database_url}")
assert settings.BACKEND_PORT == 8000
print("    [PASS] Config Loaded Successfully.")

print("--> 2. Testing FastAPI TestClient & Health Endpoint...")
client = TestClient(app)
response = client.get("/health")
print(f"    Status Code: {response.status_code}")
print(f"    Response JSON: {response.json()}")
assert response.status_code == 200
assert response.json()["status"] == "ok"
print("    [PASS] /health Endpoint Working Correctly.")

print("--> 3. Testing Core AI/Analytics Library Imports...")
import langchain
import langgraph
import langchain_google_genai
import sqlalchemy
import pymysql
import statsforecast
import plotly
import pandas as pd
import numpy as np

print(f"    LangChain Version: {version('langchain')}")
print(f"    LangGraph Version: {version('langgraph')}")
print(f"    LangChain Google GenAI Version: {version('langchain-google-genai')}")
print(f"    SQLAlchemy Version: {sqlalchemy.__version__}")
print(f"    PyMySQL Version: {pymysql.__version__}")
print(f"    StatsForecast Version: {version('statsforecast')}")
print(f"    Plotly Version: {plotly.__version__}")
print(f"    Pandas Version: {pd.__version__}")
print(f"    NumPy Version: {np.__version__}")
print("    [PASS] All Core Dependencies Verified.")

print("\n=== PHASE 1 VERIFICATION COMPLETE: ALL CHECKS PASSED ===")
