import os
import time
import logging

from postpay.config import load_config
from postpay.db.connection import get_connection
from postpay.db.migrate import initialize_schema

# Updated imports based on new folder layout
from postpay.services.payments.importer import fetch_and_persist_new_payments
from postpay.services.scheduling.scheduler import maybe_sleep_until_window_ends
from postpay.services.notifications.slack import SlackClient

logger = logging.getLogger("postpay")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)


def main() -> None:
    """
    Orchestrates the PostPay service:
      - Loads configuration
      - Initializes the database
      - Starts polling loop (email → parse → dedupe → Slack)
      - Respects sleep windows
      - Handles unexpected runtime errors gracefully
    """
    config = load_config()
    conn = get_connection(config["DB_PATH"])
    initialize_schema(conn)

    slack = SlackClient(
        webhook_url=config["SLACK_WEBHOOK_URL"],
        api_token=config["SLACK_API_TOKEN"],
        channel_id=config["SLACK_CHANNEL_ID"],
    )

    poll_interval = config["POLL_INTERVAL_SECONDS"]

    while True:
        try:
            # Sleep window enforcement (00:00–09:00)
            maybe_sleep_until_window_ends(config["ENABLE_SLEEP_MODE"])

            # Core workflow: fetch → parse → dedupe → persist
            new_payments = fetch_and_persist_new_payments(conn)

            if not new_payments:
                logger.info("No new payments found.")
                time.sleep(poll_interval)
                continue

            # Push each formatted message to Slack
            for payment in new_payments:
                formatted = payment["formatted_message"]
                slack.post_message(formatted)
                logger.info("Posted new %s payment: %s",
                            payment["provider"], formatted)

        except Exception as exc:
            logger.exception("Unhandled exception in main loop: %s", exc)
            time.sleep(5)

        time.sleep(poll_interval)


if __name__ == "__main__":
    main()
