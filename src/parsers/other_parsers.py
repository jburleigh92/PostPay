import re
from datetime import datetime


class OtherParser:
    """
    Fallback parser for any payment-style email that does NOT match the
    Zelle, Venmo, Cash App, or Apple parsers.

    This logic reflects the catch-all parsing behavior in your original PostPay4.py:
    - Detect financial/payout/payment keywords
    - Extract dollar amounts
    - Extract sender using flexible "from/sent you" patterns
    - Attempt timestamp parsing
    """

    # Broad payment-related keywords for fallback classification
    KEYWORDS = [
        "payment",
        "paid you",
        "sent you",
        "you received",
        "received money",
        "money from",
        "transaction",
    ]

    AMOUNT_REGEX = re.compile(r"\$([\d,]+\.\d{2})")

    SENDER_REGEX = re.compile(
        r"(?:from|sent you|payment from)\s+([A-Za-z .'-]+)",
        re.IGNORECASE,
    )

    DATE_REGEX = re.compile(
        r"(\w+\s+\d{1,2},\s+\d{4}\s+\d{1,2}:\d{2}\s*(?:AM|PM)?)",
        re.IGNORECASE,
    )

    def matches(self, email_body: str) -> bool:
        """
        Determines if the email likely represents a payment, even if
        the specific provider cannot be matched.
        """
        body = email_body.lower()
        return any(k in body for k in self.KEYWORDS)

    def parse(self, email_body: str):
        """
        Parse a generic / unknown payment email body.

        Returns:
            {
                "provider": "Other",
                "amount": ...,
                "sender": ...,
                "timestamp": ...
            }
        Or None if it does not appear to be a payment email.
        """
        if not self.matches(email_body):
            return None

        # Extract amount
        amount_match = self.AMOUNT_REGEX.search(email_body)
        amount = f"${amount_match.group(1)}" if amount_match else None

        # Extract sender (optional)
        sender_match = self.SENDER_REGEX.search(email_body)
        sender = sender_match.group(1).strip() if sender_match else "Unknown Sender"

        # Attempt timestamp
        timestamp_text = None
        ts_match = self.DATE_REGEX.search(email_body)
        if ts_match:
            timestamp_text = ts_match.group(1)

        # Normalize
        timestamp = None
        if timestamp_text:
            try:
                timestamp = datetime.strptime(timestamp_text, "%B %d, %Y %I:%M %p")
            except Exception:
                timestamp = timestamp_text

        return {
            "provider": "Other",
            "amount": amount,
            "sender": sender,
            "timestamp": timestamp,
        }
