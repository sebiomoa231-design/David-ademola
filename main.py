"""Render-compatible entrypoint for the preserved David AI backend.

The application implementation remains in ``app.main``. This shim keeps
existing Render services that start with ``uvicorn main:app`` compatible while
allowing local and container deployments to use the package entrypoint too.
"""

from app.main import app

__all__ = ["app"]
