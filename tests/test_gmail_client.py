import unittest
from unittest.mock import patch, MagicMock
import base64

from postpay.services.gmail_client import GmailClient


class TestGmailClient(unittest.TestCase):

    @patch("postpay.services.gmail_client.build")
    @patch("postpay.services.gmail_client.Credentials")
    def test_list_messages(self, MockCreds, MockBuild):
        """
        Ensures GmailClient.list_messages() calls the Gmail API
        with the correct parameters and returns message IDs.
        """

        # --- Mock credentials ---
        mock_creds = MagicMock()
        MockCreds.from_authorized_user_file.return_value = mock_creds

        # --- Mock Gmail service chain ---
        mock_service = MagicMock()
        MockBuild.return_value = mock_service

        mock_users = MagicMock()
        mock_messages = MagicMock()
        mock_list = MagicMock()

        mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.list.return_value = mock_list

        mock_list.execute.return_value = {
            "messages": [
                {"id": "111"},
                {"id": "222"},
            ]
        }

        client = GmailClient("fake-token.json")
        result = client.list_messages(query="from:payments")

        self.assertEqual(result, [{"id": "111"}, {"id": "222"}])

        # Validate Gmail API call chain
        mock_messages.list.assert_called_once_with(
            userId="me",
            q="from:payments",
            maxResults=10,
        )

    @patch("postpay.services.gmail_client.build")
    @patch("postpay.services.gmail_client.Credentials")
    def test_get_message(self, MockCreds, MockBuild):
        """
        Ensures GmailClient.get_message() returns the raw Gmail message JSON.
        """

        mock_creds = MagicMock()
        MockCreds.from_authorized_user_file.return_value = mock_creds

        # Mock Gmail service
        mock_service = MagicMock()
        MockBuild.return_value = mock_service

        mock_users = MagicMock()
        mock_messages = MagicMock()
        mock_get = MagicMock()

        mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.get.return_value = mock_get

        gmail_message = {"id": "abc123", "payload": {}}
        mock_get.execute.return_value = gmail_message

        client = GmailClient("fake-token.json")
        result = client.get_message("abc123")

        self.assertEqual(result, gmail_message)

        mock_messages.get.assert_called_once_with(
            userId="me",
            id="abc123",
            format="full",
        )

    def test_decode_email_body(self):
        """
        Ensures GmailClient.decode_body() correctly decodes base64 strings.
        """
        raw_text = "You received $45.00 from John Doe"
        encoded = base64.urlsafe_b64encode(raw_text.encode()).decode()

        decoded = GmailClient.decode_body(encoded)
        self.assertEqual(decoded, raw_text)

    def test_decode_email_body_empty(self):
        """
        Ensures empty or missing bodies don't cause crashes.
        """
        decoded = GmailClient.decode_body(None)
        self.assertEqual(decoded, "")

    @patch("postpay.services.gmail_client.build")
    @patch("postpay.services.gmail_client.Credentials")
    def test_list_messages_handles_no_results(self, MockCreds, MockBuild):
        """
        Gmail sometimes returns no 'messages' key—ensure function handles this.
        """

        mock_creds = MagicMock()
        MockCreds.from_authorized_user_file.return_value = mock_creds

        mock_service = MagicMock()
        MockBuild.return_value = mock_service

        mock_users = MagicMock()
        mock_messages = MagicMock()
        mock_list = MagicMock()

        mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.list.return_value = mock_list

        mock_list.execute.return_value = {}  # no messages key

        client = GmailClient("fake-token.json")
        result = client.list_messages()

        self.assertEqual(result, [])  # should not crash

    @patch("postpay.services.gmail_client.build")
    @patch("postpay.services.gmail_client.Credentials")
    def test_get_message_error_handling(self, MockCreds, MockBuild):
        """
        Ensures get_message() returns None instead of crashing on API error.
        """

        mock_creds = MagicMock()
        MockCreds.from_authorized_user_file.return_value = mock_creds

        mock_service = MagicMock()
        MockBuild.return_value = mock_service

        mock_users = MagicMock()
        mock_messages = MagicMock()
        mock_get = MagicMock()

        mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.get.return_value = mock_get

        mock_get.execute.side_effect = Exception("Gmail API failure")

        client = GmailClient("fake-token.json")
        result = client.get_message("bad-id")

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
