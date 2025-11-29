"""
Scheduler
---------
Controls sleep windows / polling intervals.
"""

import time
from postpay.services.scheduling.sleep_window import is_sleep_window
from postpay.utils.logging_utils import setup_logger

logger = setup_logger(__name__)


def maybe_sleep_until_window_ends(enable_sleep: bool):
    if not enable_sleep:
        return

    while is_sleep_window():
        logger.info("Sleep window active — pausing processing.")
        time.sleep(60)
