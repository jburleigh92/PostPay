import re
from datetime import datetime
from postpay.utils.logging_utils import info, error


class ApplePayParser:
    """
    Parser for Apple Cash / Apple Pay payment notifications.

    This parser mirrors your original PostPay4 logic:
    - Detect Apple Cash related keywords
    - Extract dollar amounts
    - Extract sender with natural-language patterns
    - Normalize timestamps when possible
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

    SENDER_REGEX = re.compile(
        r"(?:from|sent you|payment from)\s+([A-Za-z .'-]+)",
        re.IGNORECASE,
    )

    DATE_REGEX = re.compile(
        r"(\w+\s+\d{1,2},\s+\d{4}\s+\d{1,2}:\d{2}\s*(?:AM|PM)?)",
        re.IGNORECASE,
    )

    def matches(self, text: str) -> bool:
        """Return True if the email/sms content likely belongs to Apple Cash."""
        body = text.lower()
        return any(keyword in body for keyword in self.KEYWORDS)

    def parse(self, text: str):
        """Parse an Apple Cash message into a normalized payment object."""
        if not self.matches(text):
            return None

        # Amount
        amount_match = self.AMOUNT_REGEX.search(text)
        amount = f"${amount_match.group(1)}" if amount_match else None

        # Sender
        sender_match = self.SENDER_REGEX.search(text)
        sender = sender_match.group(1).strip() if sender_match else "Unknown Sender"

        # Timestamp
        timestamp = None
        date_match = self.DATE_REGEX.search(text)
        if date_match:
            raw_ts = date_match.group(1)
            try:
                timestamp = datetime.strptime(raw_ts, "%B %d, %Y %I:%M %p").timestamp()
            except Exception:
                timestamp = datetime.now().timestamp()

        return {
            "provider": "Apple Cash",
            "amount": amount,
            "sender": sender,
            "timestamp": timestamp or datetime.now().timestamp(),
            "formatted_message": None,  # Filled later by MessageFormatter
            "transaction_id": f"apple-{sender}-{timestamp}",
        }

    # NEW: required by the importer
    def fetch(self):
        """
        Apple Pay has no API — this parser cannot fetch by itself.
        Your email ingestion layer calls parser.parse() for each email body.

        So fetch() returns an empty list.
        """
        return []
