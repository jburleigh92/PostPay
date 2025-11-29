"""
Sleep Window Utility
--------------------
Defines the quiet hours when the system should not process payments.
"""

from datetime import datetime


def is_sleep_window():
    now = datetime.now().hour
    return 0 <= now < 9  # Midnight → 9am
