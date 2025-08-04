"""
FastAPI Backend for AICK Studio Abandoned Cart Recovery Agent

This package provides REST API endpoints for the frontend dashboard
and external integrations.
"""

from .main import app
from .routes import *

__all__ = ["app"]

