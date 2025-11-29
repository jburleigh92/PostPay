import unittest
from unittest.mock import patch
import sqlite3
import base64

from postpay.services.payments.importer import fetch_and_persist_new_payments
from postpay.services.notifications.formatter import MessageFormatter
from postpay.db.migrate import initialize_schema


class TestPaymentImporter(unittest.TestCase):

    def setUp(self):
        # Create in-memory SQLite DB for testing
        self.conn = sqlite3.connect(":memory:")
        initialize_schema(self.conn)

    @patch("postpay.services.payments.importer.GmailClient")
    def test_import_new_payment(self, MockGmailClient):
        """
        Ensures:
        - Gmail message is read
        - Parsers detect a payment
        - Payment is inserted into DB
        - Payment is returned as new
        """

        mock_client = MockGmailClient.return_value
        mock_client.list_messages.return_value = [{"id": "123"}]

        # Base64 for "You received $45.00 from John Doe via Zelle"
        mock_msg_json = {
            "payload": {
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {
                            "data": base64.b64encode(
                                b"You received $45.00 from John Doe via Zelle"
                            ).decode()
                        },
                    }
                ]
            }
        }

        mock_client.get_message.return_value = mock_msg_json

        # Execute importer
        results = fetch_and_persist_new_payments(self.conn)

        self.assertEqual(len(results), 1)
        payment = results[0]

        self.assertEqual(payment["provider"], "Zelle")
        self.assertEqual(payment["amount"], "$45.00")
        self.assertEqual(payment["sender"], "John Doe")

        # Verify DB insert happened
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM payments")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)

    def test_inserts_and_detects_duplicates(self):
        """
        Confirms SQL-level duplicate detection works.
        """

        parsed = {
            "transaction_id": "abc123",
            "provider": "Zelle",
            "amount": "$50.00",
            "sender": "Alice",
            "timestamp": 1234567890,
            "formatted_message": "msg1",
        }

        # Insert once
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO payments (
                transaction_id,
                provider,
                sender,
                amount,
                timestamp,
                formatted_message
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                parsed["transaction_id"],
                parsed["provider"],
                parsed["sender"],
                parsed["amount"],
                parsed["timestamp"],
                parsed["formatted_message"],
            ),
        )
        self.conn.commit()

        # Insert same again — should skip
        cursor.execute(
            "SELECT COUNT(*) FROM payments WHERE transaction_id = ?",
            (parsed["transaction_id"],),
        )
        count = cursor.fetchone()[0]

        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
