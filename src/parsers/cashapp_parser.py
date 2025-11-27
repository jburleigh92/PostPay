import re
from datetime import datetime


class CashAppParser:
    """
    Parser for Cash App payment notifications.

    This reproduces the Cash App logic from your PostPay4.py:
    - Match Cash App or cash-related keywords
    - Extract amount via standard $XX.xx regex
    - Extract sender via flexible regex patterns
    - Optionally detect timestamp if included in the email
    """

    KEYWORDS = [
        "cash app",
        "cashapp",
        "sent you money",
        "you received",
        "received payment",
    ]

    # Standard amount format: $45.00
    AMOUNT_REGEX = re.compile(r"\$([\d,]+\.\d{2})")

    # Sender logic from your script:
    # Examples:
    # "John Doe sent you $25.00 on Cash App"
    # "You received $10.00 from Jane Roe"
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
        Return True if the email appears to be a Cash App payment notification.
        """
        lower = email_body.lower()
        return any(k in lower for k in self.KEYWORDS)

    def parse(self, email_body: str):
        """
        Parse the email body into structured payment fields.

        Returns:
            dict with keys:
                provider
                amount
                sender
                timestamp
        Or None if not a Cash App message.
        """
        if not self.matches(email_body):
            return None

        # Extract amount
        amount_match = self.AMOUNT_REGEX.search(email_body)
        amount = f"${amount_match.group(1)}" if amount_match else None

        # Extract sender
        sender_match = self.SENDER_REGEX.search(email_body)
        sender = sender_match.group(1).strip() if sender_match else "Unknown Sender"

        # Timestamp? Optional.
        timestamp_text = None
        ts_match = self.DATE_REGEX.search(email_body)
        if ts_match:
            timestamp_text = ts_match.group(1)

        # Normalize timestamp, if possible
        timestamp = None
        if timestamp_text:
            try:
                timestamp = datetime.strptime(timestamp_text, "%B %d, %Y %I:%M %p")
            except Exception:
                timestamp = timestamp_text  # fallback to raw

        return {
            "provider": "Cash App",
            "amount": amount,
            "sender": sender,
            "timestamp": timestamp,
        }
