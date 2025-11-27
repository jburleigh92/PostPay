import unittest
from unittest.mock import patch, MagicMock
import sqlite3

from services.payment_importer import (
    fetch_and_persist_new_payments,
    _is_duplicate,
    _insert_payment
)
from services.message_formatter import format_payment_message
from db.migrate import initialize_schema


class TestPaymentImporter(unittest.TestCase):

    def setUp(self):
        # Create in-memory SQLite DB for duplicate testing
        self.conn = sqlite3.connect(":memory:")
        initialize_schema(self.conn)

        # posted_messages simulates runtime duplicate memory
        self.posted_messages = set()

    @patch("services.payment_importer.GmailClient")
    def test_import_new_payment(self, MockGmailClient):
        """
        Ensures:
        - Gmail message is read
        - Parsers detect payment
        - Payment is inserted into DB
        - Payment is returned for posting
        """

        # Mock Gmail response
        mock_client = MockGmailClient.return_value
        mock_client.list_messages.return_value = [{"id": "123"}]
        
        # Provide sample body for parsers
        mock_msg_json = {
            "payload": {
                "parts": [
                    {
                        "mimeType": "text/plain",
                        "body": {
                            "data": "WW91IHJlY2VpdmVkICQ0NS4wMCBmcm9tIEpvaG4gRG9lIHZpYSBaZWxsZQ=="  
                            # Base64 for: "You received $45.00 from John Doe via Zelle"
                        }
                    }
                ]
            }
        }

        mock_client.get_message.return_value = mock_msg_json

        # Call the importer
        results = fetch_and_persist_new_payments(self.conn, self.posted_messages)

        self.assertEqual(len(results), 1)
        payment = results[0]

        self.assertEqual(payment["provider"], "Zelle")
        self.assertEqual(payment["amount"], "$45.00")
        self.assertEqual(payment["sender"], "John Doe")

        # Confirm DB insert happened
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM logged_payments")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)

    def test_db_duplicate_detection(self):
        """
        Confirms _is_duplicate matches DB content.
        """

        parsed = {
            "provider": "Zelle",
            "amount": "$50.00",
            "sender": "Alice",
            "timestamp": "2024-02-05 10:00 AM",
        }

        formatted = format_payment_message(parsed)

        # Insert once
        _insert_payment(self.conn, parsed, formatted)

        # Now DB should detect a duplicate
        self.assertTrue(_is_duplicate(self.conn, formatted))

    def test_runtime_duplicate_detection(self):
        """
        Confirms that posted_messages set blocks repeats within the same run.
        """
        parsed = {
            "provider": "Venmo",
            "amount": "$20.00",
            "sender": "Bob",
            "timestamp": "2024-02-05 11:00 AM",
        }

        formatted = format_payment_message(parsed)

        # Simulate that this message was already posted
        self.posted_messages.add(formatted)

        # Insert into DB also
        _insert_payment(self.conn, parsed, formatted)

        # Now importer should not return it as new
        # We will patch GmailClient to return it again but logic should skip
        with patch("services.payment_importer.GmailClient") as MockClient:
            mock_client = MockClient.return_value
            mock_client.list_messages.return_value = [{"id": "456"}]
            mock_msg_json = {
                "payload": {
                    "parts": [
                        {
                            "mimeType": "text/plain",
                            "body": {
                                "data": base64.b64encode(
                                    f"You received {parsed['amount']} from {parsed['sender']} via Venmo".encode()
                                ).decode()
                            }
                        }
                    ]
                }
            }
            mock_client.get_message.return_value = mock_msg_json

            results = fetch_and_persist_new_payments(self.conn, self.posted_messages)

            # Should be skipped, so no new results
            self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()
