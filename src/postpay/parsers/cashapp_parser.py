import re
from datetime import datetime


class CashAppParser:
    """
    Parser for Cash App payment notifications.

    Reproduces your original PostPay4 logic:
    - Detect Cash App keywords
    - Extract dollar amounts via regex
    - Extract sender using flexible pattern
    - Parse timestamp when present
    """

    KEYWORDS = [
        "cash app",
        "cashapp",
        "sent you money",
        "you received",
        "received payment",
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
        Determine if this email represents a Cash App transaction.
        """
        body = email_body.lower()
        return any(keyword in body for keyword in self.KEYWORDS)

    def parse(self, email_body: str):
        """
        Parse Cash App payment email into a structured dict.

        Returns dict or None.
        """
        if not self.matches(email_body):
            return None

        # Amount
        amount_match = self.AMOUNT_REGEX.search(email_body)
        amount = f"${amount_match.group(1)}" if amount_match else None

        # Sender
        sender_match = self.SENDER_REGEX.search(email_body)
        sender = sender_match.group(1).strip() if sender_match else "Unknown Sender"

        # Timestamp (optional)
        timestamp = None
        ts_match = self.DATE_REGEX.search(email_body)

        if ts_match:
            timestamp_str = ts_match.group(1)
            try:
                timestamp = datetime.strptime(timestamp_str, "%B %d, %Y %I:%M %p")
            except Exception:
                timestamp = timestamp_str  # fallback

        return {
            "provider": "Cash App",
            "amount": amount,
            "sender": sender,
            "timestamp": timestamp,
        }
