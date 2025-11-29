"""
Database package for PostPay.

Exposes:
- get_connection: create a SQLite connection
- initialize_schema: create required tables

This package reflects the database logic originally embedded directly in
PostPay4.py, now separated into a clean, modular structure.
"""

from .connection import get_connection
from .migrate import initialize_schema
