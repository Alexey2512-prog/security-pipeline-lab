"""Intentionally vulnerable training application.

Never expose this application to the public internet.
"""

from .main import create_app

__all__ = ["create_app"]

