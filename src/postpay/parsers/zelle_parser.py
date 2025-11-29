# src/postpay/parsers/zelle_parser.py

import re
from datetime import datetime


class ZelleParser:
    """
    Parser for Zelle payment email bodies.

    This class reproduces the logic from your original PostPay4.py:
    - Identify Zelle-related keywords
    - Extract amount, sender, timestamp using regex
    """

    # Matches examples like:
    # "You received $45.00 from John Doe via Zelle"
    AMOUNT_REGEX = re.compile(r"\$([\d,]+\.\d{2})")

    SENDER_REGEX = re.compile(
        r"(?:from|sender|sent|received from)\s+([A-Za-z .'-]+)",
        re.IGNORECASE
    )

    # Possible timestamp format:
    DATE_REGEX = re.compile(
        r"(\w+\s+\d{1,2},\s+\d{4}\s+\d{1,2}:\d{2}\s*(?:AM|PM)?)",
        re.IGNORECASE
    )

    KEYWORDS = [
        "zelle",
        "received money",
        "sent you money",
        "you received",
    ]

    def matches(self, email_body: str) -> bool:
        """
        Returns True if the email body likely represents a Zelle payment.
        """
        lower_body = email_body.lower()
        return any(keyword in lower_body for keyword in self.KEYWORDS)

    def parse(self, email_body: str):
        """
        Parse the Zelle email body and extract:
        - provider
        - amount
        - sender
        - timestamp

        Returns a dict or None if parsing fails.
        """
        if not self.matches(email_body):
            return None

        # Extract amount
        amount_match = self.AMOUNT_REGEX.search(email_body)
        amount = f"${amount_match.group(1)}" if amount_match else None

        # Extract sender
        sender_match = self.SENDER_REGEX.search(email_body)
        sender = sender_match.group(1).strip() if sender_match else "Unknown Sender"

        # Extract timestamp
        timestamp_match = self.DATE_REGEX.search(email_body)
        timestamp_text = timestamp_match.group(1) if timestamp_match else None

        # Normalize timestamp
        try:
            timestamp = (
                datetime.strptime(timestamp_text, "%B %d, %Y %I:%M %p")
                if timestamp_text
                else None
            )
        except Exception:
            timestamp = timestamp_text  # leave raw if unparseable

        return {
            "provider": "Zelle",
            "amount": amount,
            "sender": sender,
            "timestamp": timestamp,
        }
