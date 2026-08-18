"""David AI — CORS Configuration for Frontend-Backend Connection.

Configures Cross-Origin Resource Sharing to allow the frontend
to communicate with the backend API securely.
"""
from __future__ import annotations

import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def get_allowed_origins() -> List[str]:
    """Get the list of allowed CORS origins.

    Includes:
    - The deployed frontend URL (custom domain or Manus-deployed)
    - Local development URLs
    - Any additional origins from environment
    """
    origins = [
        # Production frontend (will be updated with actual deployed URL)
        "https://david-ai-command-center.manus.space",
        "https://david-ai.manus.space",
        # Render deployment
        "https://david-ademola.onrender.com",
        "https://david-ai-frontend.onrender.com",
        # Local development
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Add any custom origins from environment
    extra_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    if extra_origins:
        origins.extend([o.strip() for o in extra_origins.split(",") if o.strip()])

    # Add the frontend URL from environment
    frontend_url = os.getenv("FRONTEND_URL", "")
    if frontend_url and frontend_url not in origins:
        origins.append(frontend_url)

    return origins


def configure_cors(app: FastAPI) -> None:
    """Add CORS middleware to the FastAPI application.

    This allows the frontend to:
    - Make API requests to the backend
    - Send authentication headers
    - Use WebSocket connections
    - Access response headers
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_allowed_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[
            "X-Request-ID",
            "X-Provider-Used",
            "X-Task-ID",
            "X-Plan-ID",
        ],
    )
