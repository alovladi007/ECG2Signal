#!/usr/bin/env python3
"""
Run the ECG2Signal Streamlit UI.

Usage:
    python run_ui.py

Or use streamlit directly:
    streamlit run ecg2signal/ui/app.py
"""

import sys
import subprocess
from pathlib import Path

if __name__ == "__main__":
    ui_file = Path(__file__).parent / "ecg2signal" / "ui" / "app.py"

    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(ui_file),
        "--server.port=8501",
        "--server.address=0.0.0.0",
    ])
