"""
Message Formatter
-----------------
Builds Slack-friendly formatted messages from raw payment objects.
"""

from datetime import datetime


class MessageFormatter:
    @staticmethod
    def format(payment):
        ts = datetime.fromtimestamp(payment["timestamp"]).strftime("%Y-%m-%d %H:%M")
        return (
            f"*{payment['provider']} Payment Received*\n"
            f"From: {payment['sender']}\n"
            f"Amount: ${payment['amount']}\n"
            f"Time: {ts}"
        )
