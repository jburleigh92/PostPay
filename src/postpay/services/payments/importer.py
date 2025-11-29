"""
Payment Importer
----------------
Fetches new payment messages from Gmail, parses them with provider-specific
parsers, deduplicates entries, and persists new payments to the database.
"""

import base64

from postpay.gmail_client import GmailClient

from postpay.parsers.apple_parser import ApplePayParser
from postpay.parsers.cashapp_parser import CashAppParser
from postpay.parsers.zelle_parser import ZelleParser
from postpay.parsers.venmo_parser import VenmoParser
from postpay.parsers.other_parsers import OtherParser

from postpay.db.connection import get_cursor
from postpay.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

# Instantiate all parsers once
PARSERS = [
    ApplePayParser(),
    CashAppParser(),
    ZelleParser(),
    VenmoParser(),
    OtherParser(),
]


def _decode_email_body(msg_json: dict) -> str:
    """
    Extracts and decodes the text/plain body from a Gmail API message.
    Mirrors your original PostPay4 logic exactly.
    """
    try:
        parts = msg_json["payload"].get("parts", [])
        for part in parts:
            if part.get("mimeType") == "text/plain":
                data = part["body"].get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    except Exception:
        pass

    return ""


def fetch_and_persist_new_payments(conn):
    """
    Full ingestion pipeline:
    - Pull emails from Gmail
    - Extract and decode bodies
    - Feed into each parser
    - Persist new payments (deduped)
    - Return a list of new payment dicts for Slack posting
    """
    cursor = get_cursor(conn)
    gmail = GmailClient()

    results = []
    messages = gmail.list_messages()

    if not messages:
        logger.info("No Gmail messages to process.")
        return results

    for msg in messages:
        msg_json = gmail.get_message(msg["id"])
        body = _decode_email_body(msg_json)

        if not body.strip():
            continue

        # Feed into each parser
        for parser in PARSERS:
            parsed = parser.parse(body)
            if not parsed:
                continue

            # Each provider must assign a transaction_id
            transaction_id = f"{parsed['provider']}-{parsed['sender']}-{parsed['amount']}-{parsed['timestamp']}"

            # Dedupe against DB
            cursor.execute(
                "SELECT COUNT(*) FROM payments WHERE transaction_id = ?",
                (transaction_id,),
            )
            if cursor.fetchone()[0] > 0:
                continue

            # Format message EXACTLY as original PostPay4 did
            formatted = (
                f"*{parsed['provider']} Payment Received*\n"
                f"From: {parsed['sender']}\n"
                f"Amount: {parsed['amount']}\n"
                f"Time: {parsed['timestamp']}"
            )

            # Persist
            cursor.execute(
                """
                INSERT INTO payments (
                    transaction_id,
                    provider,
                    sender,
                    amount,
                    timestamp,
                    formatted_message
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    transaction_id,
                    parsed["provider"],
                    parsed["sender"],
                    parsed["amount"],
                    parsed["timestamp"],
                    formatted,
                ),
            )
            conn.commit()

            parsed["formatted_message"] = formatted
            parsed["transaction_id"] = transaction_id

            results.append(parsed)

    logger.info("Imported %d new payments.", len(results))
    return results
