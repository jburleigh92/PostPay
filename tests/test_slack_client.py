import unittest
from unittest.mock import patch, MagicMock

from postpay.services.notifications.slack import SlackClient


class TestSlackClient(unittest.TestCase):

    @patch("postpay.services.notifications.slack.requests.post")
    def test_post_message_success(self, mock_post):
        # Mock Slack API successful response
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"ok": True}
        mock_post.return_value = mock_response

        client = SlackClient(
            webhook_url="https://hooks.slack.com/services/placeholder",
            api_token="xoxb-testtoken",
            channel_id="C1234567890"
        )

        ok = client.post_message("Test message")

        # Validate return value
        self.assertTrue(ok)

        # Validate URL called
        mock_post.assert_called_once()

        call_args = mock_post.call_args
        url = call_args[0][0]
        payload = call_args[1]["json"]
        headers = call_args[1]["headers"]

        # Validate Slack API URL
        self.assertEqual(url, "https://slack.com/api/chat.postMessage")

        # Validate payload structure
        self.assertEqual(payload["channel"], "C1234567890")
        self.assertEqual(payload["text"], "Test message")

        # Validate Authorization header
        self.assertIn("Authorization", headers)
        self.assertEqual(headers["Authorization"], "Bearer xoxb-testtoken")

    @patch("postpay.services.notifications.slack.requests.post")
    def test_post_message_failure(self, mock_post):
        # Mock Slack API error response
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"ok": False, "error": "invalid_auth"}
        mock_post.return_value = mock_response

        client = SlackClient(
            webhook_url="https://hooks.slack.com/services/placeholder",
            api_token="badtoken",
            channel_id="C1234567890"
        )

        ok = client.post_message("Test")

        # Should return False on Slack failure
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
