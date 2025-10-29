
import tempfile
from pathlib import Path

def create_temp_dir() -> Path:
    return Path(tempfile.mkdtemp(prefix='ecg2signal_'))
