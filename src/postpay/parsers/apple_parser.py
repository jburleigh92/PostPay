import re
from datetime import datetime


class AppleParser:
    """
    Parser for Apple Cash / Apple Pay payment notifications.

    Mirrors the logic used in your original PostPay4.py:
    - Detects Apple Cash related keywords
    - Extracts dollar amounts via $XX.xx regex
    - Extracts sender using flexible 'from/sent you' patterns
    - Attempts to parse timestamp (optional in many Apple Cash emails)
    """

    KEYWORDS = [
        "apple cash",
        "apple pay",
        "apple payment",
        "sent you",
        "you received",
        "received payment",
    ]

    AMOUNT_REGEX = re.compile(r"\$([\d,]+\.\d{2})")

    # Examples:
    # "You received $25.00 from John Doe via Apple Cash"
    # "John Doe sent you $50.00 using Apple Pay"
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
        Determines if the email body likely refers to an Apple Cash transaction.
        """
        body = email_body.lower()
        return any(keyword in body for keyword in self.KEYWORDS)

    def parse(self, email_body: str):
        """
        Parse the Apple Cash related email. Returns:
        {
            "provider": "Apple Cash",
            "amount": ...,
            "sender": ...,
            "timestamp": ...,
        }
        or None if not matched.
        """

        if not self.matches(email_body):
            return None

        # Extract amount
        amount_match = self.AMOUNT_REGEX.search(email_body)
        amount = f"${amount_match.group(1)}" if amount_match else None

        # Extract sender
        sender_match = self.SENDER_REGEX.search(email_body)
        sender = sender_match.group(1).strip() if sender_match else "Unknown Sender"

        # Optional timestamp
        timestamp_text = None
        ts_match = self.DATE_REGEX.search(email_body)
        if ts_match:
            timestamp_text = ts_match.group(1)

        # Normalize timestamp
        timestamp = None
        if timestamp_text:
            try:
                timestamp = datetime.strptime(timestamp_text, "%B %d, %Y %I:%M %p")
            except Exception:
                timestamp = timestamp_text

        return {
            "provider": "Apple Cash",
            "amount": amount,
            "sender": sender,
            "timestamp": timestamp,
        }
