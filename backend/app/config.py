"""Application configuration loaded from environment variables."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/time_management.db")
SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-to-a-random-string")
REMINDER_SCAN_INTERVAL: int = int(os.getenv("REMINDER_SCAN_INTERVAL", "60"))

# Ensure data directory exists for SQLite
(BASE_DIR / "data").mkdir(exist_ok=True)
