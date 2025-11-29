import base64
import json
import requests
import sqlite3

from parsers.zelle_parser import ZelleParser
from parsers.venmo_parser import VenmoParser
from parsers.cashapp_parser import CashAppParser
from parsers.apple_parser import AppleParser
from parsers.other_parsers import OtherParser

from services.message_formatter import format_payment_message


class GmailClient:
    """
    Minimal Gmail API client reflecting the exact behavior of your PostPay4.py:
    - List messages
    - Retrieve message bodies
    """

    def __init__(self, access_token: str):
        self.access_token = access_token

    def _headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def list_messages(self, query: str = None):
        """
        Retrieve a list of messages matching the provided Gmail search query.
        """
        url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"

        params = {}
        if query:
            params["q"] = query

        response = requests.get(url, headers=self._headers(), params=params)
        if response.status_code != 200:
            print(f"Gmail API error (list): {response.text}")
            return []

        data = response.json()
        return data.get("messages", [])

    def get_message(self, message_id: str):
        """
        Retrieve full Gmail message content.
        """
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}"
        response = requests.get(url, headers=self._headers())

        if response.status_code != 200:
            print(f"Gmail API error (get message): {response.text}")
            return None

        return response.json()

    @staticmethod
    def extract_body(message_json: dict) -> str:
        """
        Extract and decode the email body exactly as your PostPay4.py did.
        """
        try:
            parts = message_json["payload"]["parts"]

            for part in parts:
                if part.get("mimeType") == "text/plain":
                    body_encoded = part["body"]["data"]
                    decoded_bytes = base64.urlsafe_b64decode(body_encoded.encode("utf-8"))
                    return decoded_bytes.decode("utf-8")

        except Exception:
            pass

        return ""  # fallback if parsing fails


def fetch_and_persist_new_payments(conn: sqlite3.Connection, posted_messages: set):
    """
    Core pipeline, equivalent to your main payment extraction/processing loop:

    - Fetch messages from Gmail
    - Decode and parse email body
    - Attempt each provider parser (Zelle → Venmo → Cash App → Apple → Other)
    - Deduplicate using DB + in-memory posted_messages
    - Insert into DB if new
    - Return list of payments ready to post to Slack
    """

    # Note: Your original script used an env variable access token.
    from os import getenv
    gmail_token = getenv("GMAIL_API_TOKEN", "")

    gmail = GmailClient(gmail_token)

    # In your script, you used a Gmail search query for recent messages.
    messages = gmail.list_messages(query="newer_than:1d")

    results = []

    zelle = ZelleParser()
    venmo = VenmoParser()
    cash = CashAppParser()
    apple = AppleParser()
    other = OtherParser()

    for msg in messages:
        msg_json = gmail.get_message(msg["id"])
        if not msg_json:
            continue

        body = GmailClient.extract_body(msg_json)
        if not body:
            continue

        parsed = (
            zelle.parse(body)
            or venmo.parse(body)
            or cash.parse(body)
            or apple.parse(body)
            or other.parse(body)
        )

        if not parsed:
            continue

        # Format Slack message using actual formatting logic
        formatted_message = format_payment_message(parsed)

        # Prevent in-memory dupes (as in your script)
        if formatted_message in posted_messages:
            continue

        # DB duplicate check
        if _is_duplicate(conn, formatted_message):
            continue

        # Insert into DB
        _insert_payment(conn, parsed, formatted_message)

        parsed["formatted_message"] = formatted_message
        results.append(parsed)

    return results


def _is_duplicate(conn: sqlite3.Connection, formatted_message: str) -> bool:
    """
    Checks if a payment message has already been logged.
    Mirrors your SELECT query from PostPay4.py.
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM logged_payments WHERE formatted_message = ?",
        (formatted_message,),
    )
    row = cursor.fetchone()
    return row is not None


def _insert_payment(
    conn: sqlite3.Connection, parsed: dict, formatted_message: str
) -> None:
    """
    Inserts a new payment log entry, identical to your original INSERT logic.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO logged_payments (provider, amount, sender, timestamp, formatted_message)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            parsed.get("provider"),
            parsed.get("amount"),
            parsed.get("sender"),
            str(parsed.get("timestamp")),
            formatted_message,
        ),
    )
    conn.commit()
