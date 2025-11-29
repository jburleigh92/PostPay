"""
Payment Service Domain

Handles ingestion, parsing, normalization, and persistence of
payment data from multiple providers.
"""

from .importer import fetch_and_persist_new_payments

__all__ = ["fetch_and_persist_new_payments"]
