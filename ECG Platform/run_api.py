#!/usr/bin/env python3
"""
Run the ECG2Signal FastAPI server.

Usage:
    python run_api.py

Or with custom settings:
    python run_api.py --host 0.0.0.0 --port 8000 --reload
"""

import uvicorn
from ecg2signal.config import get_settings

if __name__ == "__main__":
    settings = get_settings()

    uvicorn.run(
        "ecg2signal.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        workers=1 if settings.api_reload else settings.api_workers,
        log_level=settings.log_level.lower(),
    )
