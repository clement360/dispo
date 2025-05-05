"""
Centralised configuration loader.
Reads .env (if present) and provides typed accessors.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

AMAZON_CLIENT_ID     = os.getenv("AMAZON_CLIENT_ID", "")
AMAZON_CLIENT_SECRET = os.getenv("AMAZON_CLIENT_SECRET", "")
AMAZON_REFRESH_TOKEN = os.getenv("AMAZON_REFRESH_TOKEN", "")

# Refresh rate for sales polling (seconds)
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", 300))

# Display back-end selection.
# auto  – detect platform
# real  – force real matrix
# emu   – force emulator
DISPLAY_BACKEND = os.getenv("DISPLAY_BACKEND", "auto")