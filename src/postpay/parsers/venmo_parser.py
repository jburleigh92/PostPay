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
        text = email_body.lower()
        return any(keyword in text for keyword in self.KEYWORDS)

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
        amt = self.AMOUNT_REGEX.search(email_body)
        amount = f"${amt.group(1)}" if amt else None

        # Extract sender
        snd = self.SENDER_REGEX.search(email_body)
        sender = snd.group(1).strip() if snd else "Unknown Sender"

        # Optional timestamp
        raw_ts = None
        ts_match = self.DATE_REGEX.search(email_body)
        if ts_match:
            raw_ts = ts_match.group(1)

        # Parse timestamp if possible
        timestamp = None
        if raw_ts:
            try:
                timestamp = datetime.strptime(raw_ts, "%B %d, %Y %I:%M %p")
            except Exception:
                timestamp = raw_ts  # fallback to raw

        return {
            "provider": "Venmo",
            "amount": amount,
            "sender": sender,
            "timestamp": timestamp,
        }
