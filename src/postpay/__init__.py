"""
PostPay Public API
------------------

This module provides the official public interface for the PostPay
automation engine. External consumers should import from here rather
than from internal module paths.

Example:

    from postpay import (
        PaymentImporter,
        MessageFormatter,
        Scheduler,
        ZelleParser,
        VenmoParser,
        CashAppParser,
        ApplePayParser,
        OtherPaymentParser,
        setup_logger,
        is_sleep_window,
        __version__,
    )
"""

from .VERSION import __version__

# Service Layer
from .services.payments.importer import fetch_and_persist_new_payments as PaymentImporter
from .services.notifications.formatter import MessageFormatter
from .services.scheduling.scheduler import Scheduler

# Parsers
from .parsers.apple_parser import ApplePayParser
from .parsers.cashapp_parser import CashAppParser
from .parsers.other_parsers import OtherPaymentParser
from .parsers.venmo_parser import VenmoParser
from .parsers.zelle_parser import ZelleParser

# Utilities
from .utils.logging_utils import setup_logger
from .utils.sleep_window import is_sleep_window

__all__ = [
    "PaymentImporter",
    "MessageFormatter",
    "Scheduler",
    "ApplePayParser",
    "CashAppParser",
    "OtherPaymentParser",
    "VenmoParser",
    "ZelleParser",
    "setup_logger",
    "is_sleep_window",
    "__version__",
]
