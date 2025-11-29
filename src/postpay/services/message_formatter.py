from datetime import datetime, timezone, timedelta


def format_payment_message(parsed: dict) -> str:
    """
    Formats the Slack message exactly as your original PostPay4.py did.

    Input dict contains:
        provider
        amount
        sender
        timestamp (may be datetime or string)

    Output is a multi-line Slack message exactly matching your format.
    """

    provider = parsed.get("provider", "Unknown")
    amount = parsed.get("amount", "Unknown Amount")
    sender = parsed.get("sender", "Unknown Sender")
    ts = parsed.get("timestamp")

    timestamp_str = _format_timestamp(ts)

    formatted = (
        f"*{provider} Payment Received*\n"
        f"Amount: {amount}\n"
        f"From: {sender}\n"
        f"Time: {timestamp_str}"
    )

    return formatted


def _format_timestamp(ts):
    """
    Reproduces your timestamp logic:

    - If value is a datetime, convert to PST/PDT (UTC-8 standard)
    - If not a datetime, return raw string or default
    """
    if isinstance(ts, datetime):
        # Convert timestamp to America/Los_Angeles manually
        # because you did it using timedelta in your original script.
        pacific_offset = timedelta(hours=-8)  # matches your original usage
        local_ts = ts.astimezone(timezone(pacific_offset))
        return local_ts.strftime("%Y-%m-%d %I:%M %p")

    # If timestamp exists but is raw text, return as-is
    if ts:
        return str(ts)

    # Default fallback
    return "Unknown"
