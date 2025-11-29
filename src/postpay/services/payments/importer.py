"""
Payment Importer
----------------
Fetches new payment messages from connected providers, parses them,
deduplicates entries, and persists them to the database.
"""

from postpay.parsers.apple_parser import ApplePayParser
from postpay.parsers.cashapp_parser import CashAppParser
from postpay.parsers.zelle_parser import ZelleParser
from postpay.parsers.venmo_parser import VenmoParser
from postpay.parsers.other_parsers import OtherPaymentParser
from postpay.db.connection import get_cursor
from postpay.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

PARSERS = [
    ApplePayParser(),
    CashAppParser(),
    ZelleParser(),
    VenmoParser(),
    OtherPaymentParser(),
]


def fetch_and_persist_new_payments(conn):
    cursor = get_cursor(conn)

    new_payments = []

    for parser in PARSERS:
        results = parser.fetch()

        for payment in results:
            cursor.execute(
                "SELECT COUNT(*) FROM payments WHERE transaction_id = ?",
                (payment["transaction_id"],),
            )
            if cursor.fetchone()[0] > 0:
                continue

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
                    payment["transaction_id"],
                    payment["provider"],
                    payment["sender"],
                    payment["amount"],
                    payment["timestamp"],
                    payment["formatted_message"],
                ),
            )
            conn.commit()

            new_payments.append(payment)

    logger.info("Imported %d new payments.", len(new_payments))
    return new_payments
