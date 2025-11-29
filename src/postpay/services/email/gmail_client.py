"""
Gmail Client
------------
Handles Gmail API authentication, message listing, and raw email body extraction.
This preserves the exact behavior of the original PostPay4 logic, rewritten
cleanly for the new modular architecture.
"""

import base64
from typing import List, Dict, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from postpay.utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class GmailClient:
    def __init__(self, token_path: str, credentials_path: str, query: str):
        """
        token_path: Path to token.json (contains user's OAuth tokens)
        credentials_path: Path to credentials.json (OAuth client secrets)
        query: Gmail search filter (e.g., 'from:messaging@cash.app newer_than:1d')
        """
        self.token_path = token_path
        self.credentials_path = credentials_path
        self.query = query

        self.service = self._authenticate()

    def _authenticate(self):
        """
        Loads saved OAuth credentials and constructs the Gmail API client.
        Assumes token.json already exists (same as original script).
        """
        try:
            creds = Credentials.from_authorized_user_file(self.token_path)
            service = build("gmail", "v1", credentials=creds)
            logger.info("Gmail authentication successful.")
            return service
        except Exception as exc:
            logger.error("Failed to authenticate Gmail client: %s", exc)
            raise

    def list_messages(self) -> List[Dict]:
        """
        Returns a list of Gmail messages matching the query filter.
        """
        try:
            response = (
                self.service.users()
                .messages()
                .list(userId="me", q=self.query, maxResults=10)
                .execute()
            )
            return response.get("messages", [])
        except HttpError as err:
            logger.error("Gmail API list_messages error: %s", err)
            return []

    def get_message(self, msg_id: str) -> Dict:
        """
        Returns the full Gmail message object, including payload parts.
        """
        try:
            message = (
                self.service.users()
                .messages()
                .get(userId="me", id=msg_id, format="full")
                .execute()
            )
            return message
        except HttpError as err:
            logger.error("Gmail API get_message error: %s", err)
            return {}

    @staticmethod
    def extract_text(message: Dict) -> Optional[str]:
        """
        Extracts the plain-text body from a Gmail message payload.

        The original PostPay4 logic depended on:
        - payload.parts[0].body.data
        - Base64 URL-safe decoding
        """
        try:
            parts = message.get("payload", {}).get("parts", [])
            if not parts:
                return None

            data = parts[0]["body"].get("data")
            if not data:
                return None

            decoded_bytes = base64.urlsafe_b64decode(data)
            return decoded_bytes.decode("utf-8", errors="ignore")

        except Exception as exc:
            logger.error("Failed to decode Gmail message body: %s", exc)
            return None
