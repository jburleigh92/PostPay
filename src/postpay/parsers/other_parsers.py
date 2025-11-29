import re
from datetime import datetime


class OtherPaymentParser:
    """
    Fallback parser for any payment-style email that does NOT match
    Zelle, Venmo, Cash App, or Apple Cash.

    This mirrors your original PostPay4.py catch-all logic:
    - Broad financial/payment keyword detection
    - Regex-based amount extraction
    - Generic sender extraction
    - Optional timestamp parsing
    """

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
        Determines if the message looks like a payment-style email.
        """
        lower = email_body.lower()
        return any(k in lower for k in self.KEYWORDS)

    def parse(self, email_body: str):
        """
        Parse fallback payment fields.

        Returns:
            {
                "provider": "Other",
                "amount": ...,
                "sender": ...,
                "timestamp": ...
            }
        Or None if not a match.
        """
        if not self.matches(email_body):
            return None

        # Amount
        amount_match = self.AMOUNT_REGEX.search(email_body)
        amount = f"${amount_match.group(1)}" if amount_match else None

        # Sender
        sender_match = self.SENDER_REGEX.search(email_body)
        sender = sender_match.group(1).strip() if sender_match else "Unknown Sender"

        # Timestamp
        timestamp_text = None
        ts_match = self.DATE_REGEX.search(email_body)
        if ts_match:
            timestamp_text = ts_match.group(1)

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
