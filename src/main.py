import os
import time

from db.connection import get_connection
from db.migrate import initialize_schema
from services.payment_importer import fetch_and_persist_new_payments
from services.scheduler import maybe_sleep_until_window_ends
from slack_client import SlackClient


def load_config() -> dict:
    """
    Load runtime configuration from environment variables.

    In your original script these values were hard-coded. For a portfolio-
    quality repository, they are pulled from the environment instead.
    """
    return {
        "ENABLE_SLEEP_MODE": os.getenv("ENABLE_SLEEP_MODE", "true").lower() == "true",
        "SLACK_WEBHOOK_URL": os.getenv("SLACK_WEBHOOK_URL", ""),
        "SLACK_API_TOKEN": os.getenv("SLACK_API_TOKEN", ""),
        "SLACK_CHANNEL_ID": os.getenv("SLACK_CHANNEL_ID", ""),
        "DB_PATH": os.getenv("DB_PATH", "data/logged_payments.db"),
        "POLL_INTERVAL_SECONDS": int(os.getenv("POLL_INTERVAL_SECONDS", "30")),
    }


def main() -> None:
    """
    Main event loop.

    Mirrors the behavior of your original PostPay4.py:
    - Connects to SQLite for logged payments
    - Ensures the database schema exists
    - Polls for new payment emails
    - Parses provider-specific payments (Zelle, Venmo, Cash App, Apple, other)
    - Deduplicates against both DB and in-memory set of posted messages
    - Posts formatted messages to Slack
    - Respects a sleep window when ENABLE_SLEEP_MODE is true
    - Waits 30 seconds (configurable) between polling cycles
    """
    config = load_config()

    # Set up database connection (replaces hard-coded LOGGED_DB_PATH)
    conn = get_connection(config["DB_PATH"])

    # Ensure schema exists (equivalent to your initial CREATE TABLE logic)
    initialize_schema(conn)

    # Set up Slack client (replaces hard-coded SLACK_* constants)
    slack = SlackClient(
        webhook_url=config["SLACK_WEBHOOK_URL"],
        api_token=config["SLACK_API_TOKEN"],
        channel_id=config["SLACK_CHANNEL_ID"],
    )

    # Runtime memory of messages posted during this process execution.
    # This mirrors the original posted_messages list used to avoid double-posting
    # within a single run, in addition to the DB-based duplicate protection.
    posted_messages = set()

    poll_interval = config["POLL_INTERVAL_SECONDS"]

    while True:
        # Respect the configured sleep window (00:00–09:00 in your original script)
        maybe_sleep_until_window_ends(config["ENABLE_SLEEP_MODE"])

        # Core logic:
        # - fetch emails
        # - parse provider-specific payments (Zelle, Venmo, Cash App, Apple, etc.)
        # - dedupe and insert into DB
        # - return only newly-logged payments that should be sent to Slack
        new_payments = fetch_and_persist_new_payments(conn, posted_messages)

        new_payments_found = False

        for payment in new_payments:
            # Each `payment` is expected to include at least:
            #   provider, amount, sender, timestamp, formatted_message
            formatted_message = payment["formatted_message"]

            # In-memory duplicate check (same as original posted_messages control)
            if formatted_message in posted_messages:
                print(f"Duplicate or already logged: {formatted_message}", end="\r")
                continue

            slack.post_message(formatted_message)
            posted_messages.add(formatted_message)
            new_payments_found = True

            print(
                f"Status: New {payment['provider']} payment logged and posted to Slack.",
                end="\r",
            )

        if not new_payments_found:
            print("Status: Waiting for new payments...", end="\r")

        time.sleep(poll_interval)


if __name__ == "__main__":
    main()
