import re
from datetime import datetime


class VenmoParser:
    """
    Parser for Venmo payment notifications.

    Logic is adapted directly from your PostPay4.py:
    - Match Venmo-related keywords
    - Extract sender and amount via regex
    - Attempt to extract timestamp (optional in some Venmo emails)
    """

    KEYWORDS = [
        "venmo",
        "paid you",
        "sent you",
        "you received a payment",
        "money from",
    ]

    # Examples captured:
    # "John Doe paid you $15.00"
    # "You received $40.00 from Jane Roe"
    AMOUNT_REGEX = re.compile(r"\$([\d,]+\.\d{2})")
    SENDER_REGEX = re.compile(
        r"(?:from|paid you|sent you|money from)\s+([A-Za-z .'-]+)",
        re.IGNORECASE,
    )

    # Optional timestamp extraction
    DATE_REGEX = re.compile(
        r"(\w+\s+\d{1,2},\s+\d{4}\s+\d{1,2}:\d{2}\s*(?:AM|PM)?)",
        re.IGNORECASE,
    )

    def matches(self, email_body: str) -> bool:
        """
        Determine whether the email body likely corresponds to a Venmo payment.
        """
        lower = email_body.lower()
        return any(keyword in lower for keyword in self.KEYWORDS)

    def parse(self, email_body: str):
        """
        Parse Venmo payment content and return dict with:
        - provider
        - amount
        - sender
        - timestamp (raw text or datetime)
        """
        if not self.matches(email_body):
            return None

        # Extract amount
        amount_match = self.AMOUNT_REGEX.search(email_body)
        amount = f"${amount_match.group(1)}" if amount_match else None

        # Extract sender
        sender_match = self.SENDER_REGEX.search(email_body)
        sender = sender_match.group(1).strip() if sender_match else "Unknown Sender"

        # Timestamp extraction (fallback only)
        timestamp_text = None
        match = self.DATE_REGEX.search(email_body)
        if match:
            timestamp_text = match.group(1)

        # Try to normalize timestamp
        timestamp = None
        if timestamp_text:
            try:
                timestamp = datetime.strptime(timestamp_text, "%B %d, %Y %I:%M %p")
            except Exception:
                timestamp = timestamp_text  # leave raw

        return {
            "provider": "Venmo",
            "amount": amount,
            "sender": sender,
            "timestamp": timestamp,
        }
