"""
PostPay CLI Entrypoint
----------------------

This module exposes a simple CLI that maps to the main PostPay
runtime orchestration function. It allows the package to be run as:

    postpay run
"""

from postpay.main import main


def run():
    """Run the PostPay automation engine."""
    main()
