"""
Notification Service Domain

Handles outbound messaging, Slack integration, and formatting.
"""

from .formatter import MessageFormatter
from .slack import SlackClient

__all__ = ["MessageFormatter", "SlackClient"]
