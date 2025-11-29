"""
Scheduler
---------
Enforces the PostPay sleep window and manages timing behavior
for the main polling loop.
"""

import time

from postpay.services.scheduling.sleep_window import is_sleep_window
from postpay.utils.logging_utils import setup_logger

logger = setup_logger(__name__)


def maybe_sleep_until_window_ends(enable_sleep: bool) -> None:
    """
    If sleep mode is enabled, pauses execution until the nightly
    restricted window has ended (00:00–09:00). Uses a 60-second
    polling interval while waiting.

    Parameters
    ----------
    enable_sleep : bool
        Whether sleep-windows are enforced.
    """
    if not enable_sleep:
        return

    while is_sleep_window():
        logger.info("Sleep window active — pausing processing for 60 seconds.")
        time.sleep(60)
