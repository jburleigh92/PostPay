from datetime import datetime, time as dtime


SLEEP_START = dtime(0, 0)   # midnight
SLEEP_END = dtime(9, 0)     # 9 AM


def is_within_sleep_window(current_time=None) -> bool:
    """
    Pure time-window check, identical in logic to your original PostPay4.py
    sleep mode boundaries.

    Args:
        current_time: Optional datetime.time for testing.
                      If None, uses the current local system time.

    Returns:
        True if the time falls between 00:00 and 09:00.
    """
    if current_time is None:
        current_time = datetime.now().time()

    return SLEEP_START <= current_time < SLEEP_END


def next_window_end(today=None) -> datetime:
    """
    Returns a datetime object for the *next* 9 AM boundary.

    While your original script did not explicitly compute this directly,
    this helper is provided for potential clean scheduling use and keeps
    this utility future-proof.

    Args:
        today: Optional datetime (for testing). Defaults to now.

    Returns:
        A datetime representing today's (or tomorrow's) 09:00 AM.
    """
    if today is None:
        today = datetime.now()

    target = today.replace(hour=9, minute=0, second=0, microsecond=0)

    if today >= target:
        # If we've already passed 9 AM today, schedule for tomorrow
        return target.replace(day=target.day + 1)

    return target
