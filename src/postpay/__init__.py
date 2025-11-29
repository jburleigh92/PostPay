"""
PostPay Public API
------------------

This module exposes a clean and unified interface for the PostPay automation
engine. External users should import from here rather than accessing internal
modules directly.

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

from pathlib import Path

# -------------------------------------------------------------------
# Version Loader
# -------------------------------------------------------------------
# Load version dynamically from the root-level VERSION file.
_version_file = Path(__file__).resolve().parent.parent.parent / "VERSION"
__version__ = _version_file.read_text().strip()

# -------------------------------------------------------------------
# Service Layer
# -------------------------------------------------------------------
from .services.payment_importer import PaymentImporter
from .services.message_formatter import MessageFormatter
from .services.scheduler import Scheduler

# -------------------------------------------------------------------
# Parsers
# -------------------------------------------------------------------
from .parsers.apple_parser import ApplePayParser
from .parsers.cashapp_parser import CashAppParser
from .parsers.other_parsers import OtherPaymentParser
from .parsers.venmo_parser import VenmoParser
from .parsers.zelle_parser import ZelleParser

# -------------------------------------------------------------------
# Utilities
# -------------------------------------------------------------------
from .utils.logging_utils import setup_logger
from .utils.sleep_window import is_sleep_window

# -------------------------------------------------------------------
# Public API surface
# -------------------------------------------------------------------
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

    # Utils
    "setup_logger",
    "is_sleep_window",
]
