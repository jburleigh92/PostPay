"""
PostPay Public API
------------------

This module provides a unified, stable import interface for the PostPay
automation engine. External code should import from here rather than accessing
internal modules directly.

Example usage:

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

from .version import __version__

# Service Layer
from .services.payment_importer import PaymentImporter
from .services.message_formatter import MessageFormatter
from .services.scheduler import Scheduler

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
    "__version__",

    # Services
    "PaymentImporter",
    "MessageFormatter",
    "Scheduler",

    # Parsers
    "ApplePayParser",
    "CashAppParser",
    "OtherPaymentParser",
    "VenmoParser",
    "ZelleParser",

    # Utilities
    "setup_logger",
    "is_sleep_window",
]
