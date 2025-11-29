"""
Configuration Loader for PostPay
--------------------------------
Provides a centralized, environment-based configuration system for:

- Slack API credentials
- Database location
- Polling interval
- Sleep window activation
- Gmail credentials paths

This replaces hardcoded variables and enables clean deployment.
"""

import os
from pathlib import Path


def load_config() -> dict:
    """
    Loads configuration for PostPay using environment variables with sensible defaults.
    Environment variables override defaults automatically.
    """

    # Base project directory (repo root)
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    return {
        # ---- Slack Configuration ----
        "SLACK_WEBHOOK_URL": os.getenv("SLACK_WEBHOOK_URL", ""),
        "SLACK_API_TOKEN": os.getenv("SLACK_API_TOKEN", ""),
        "SLACK_CHANNEL_ID": os.getenv("SLACK_CHANNEL_ID", ""),

        # ---- Gmail OAuth Credentials ----
        "CREDENTIALS_PATH": os.getenv(
            "CREDENTIALS_PATH",
            str(BASE_DIR / "credentials" / "credentials.json")
        ),
        "TOKEN_PATH": os.getenv(
            "TOKEN_PATH",
            str(BASE_DIR / "credentials" / "token.json")
        ),

        # ---- Database ----
        "DB_PATH": os.getenv(
            "DB_PATH",
            str(BASE_DIR / "data" / "payments.db")
        ),

        # ---- Polling ----
        "POLL_INTERVAL_SECONDS": int(os.getenv("POLL_INTERVAL_SECONDS", "30")),

        # ---- Sleep Window ----
        "ENABLE_SLEEP_MODE": os.getenv("ENABLE_SLEEP_MODE", "true").lower() == "true",
    }
