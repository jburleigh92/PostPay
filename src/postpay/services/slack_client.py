import requests


class SlackClient:
    """
    A minimal Slack client that reproduces the exact behavior used in PostPay4.py.
    
    Your original program posted messages using Slack's chat.postMessage endpoint
    with a Bearer token and channel ID. This class encapsulates that logic.
    """

    def __init__(self, webhook_url: str, api_token: str, channel_id: str):
        self.webhook_url = webhook_url
        self.api_token = api_token
        self.channel_id = channel_id

    def post_message(self, text: str) -> bool:
        """
        Send a formatted message to Slack using the API method chat.postMessage.

        This is a direct adaptation of your original request logic:
        - Authorization: Bearer <SLACK_API_TOKEN>
        - POST to https://slack.com/api/chat.postMessage
        - Payload: channel + text

        Returns True if Slack confirms success, False otherwise.
        """

        url = "https://slack.com/api/chat.postMessage"

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "channel": self.channel_id,
            "text": text,
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()

            # Slack responses include {"ok": true/false}
            if not data.get("ok", False):
                print(f"Slack API error: {data}")
                return False

            return True

        except Exception as e:
            print(f"Slack communication failed: {e}")
            return False
