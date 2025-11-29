"""
Slack Notification Client
-------------------------
Handles posting formatted payment messages to Slack channels.
"""

import requests
from postpay.utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class SlackClient:
    """
    Sends formatted messages to Slack via the Web API.
    """

    def __init__(self, webhook_url: str, api_token: str, channel_id: str):
        self.webhook_url = webhook_url
        self.api_token = api_token
        self.channel_id = channel_id

    def post_message(self, text: str) -> None:
        """
        Sends a message to Slack using chat.postMessage.
        """
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {"channel": self.channel_id, "text": text}

        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers=headers,
            json=payload,
            timeout=10,
        )

        if not response.ok or not response.json().get("ok"):
            logger.error("Slack error: %s", response.text)
        else:
            logger.info("Slack message posted successfully.")
