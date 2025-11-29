"""
Scheduler
---------
Manages PostPay's sleep window to prevent processing during restricted hours.
"""

import time
from postpay.services.scheduling.sleep_window import is_sleep_window
from postpay.utils.logging_utils import setup_logger

logger = setup_logger(__name__)


def maybe_sleep_until_window_ends(enable_sleep: bool) -> None:
    """
    If sleep mode is enabled, pause execution until the current sleep window ends.
    """
    if not enable_sleep:
        return

    while is_sleep_window():
        logger.info("Sleep window active — pausing processing.")
        time.sleep(60)
