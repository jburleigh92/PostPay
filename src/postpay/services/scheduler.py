import time
from datetime import datetime, time as dtime


SLEEP_START = dtime(0, 0)   # 12:00 AM
SLEEP_END = dtime(9, 0)     # 9:00 AM


def maybe_sleep_until_window_ends(enable_sleep_mode: bool) -> None:
    """
    Implements the same sleep window logic used in your original PostPay4.py:
    - If ENABLE_SLEEP_MODE is true
    - And the current time is between 12:00 AM and 9:00 AM
    - Then the program should pause until outside the window

    In your original script, the pause interval was printed as a status message
    and slept for 5 minutes at a time.
    """

    if not enable_sleep_mode:
        return

    now = datetime.now().time()

    if _is_within_sleep_window(now):
        print("Status: Sleep mode active (00:00–09:00). Pausing checks...", end="\r")

        # Your original script slept in intervals (e.g., sleep(300))
        # to avoid excessive waiting while allowing graceful shutdown.
        time.sleep(300)


def _is_within_sleep_window(current: dtime) -> bool:
    """
    Returns True if the current time is within the configured sleep window.
    """
    return SLEEP_START <= current < SLEEP_END
