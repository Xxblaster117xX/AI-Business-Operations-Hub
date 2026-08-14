import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

# Provide safe defaults so Settings() can be instantiated without a real
# .env / real Gemini key. Individual tests mock any actual Gemini calls.
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg2://hub:hub@localhost:5432/business_ops_hub_test"
)
