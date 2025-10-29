
import pytest
import numpy as np

@pytest.fixture
def sample_ecg_image():
    """Create a sample ECG image for testing."""
    return np.random.randint(0, 255, (1000, 1500, 3), dtype=np.uint8)

@pytest.fixture
def sample_signal():
    """Create a sample ECG signal."""
    t = np.linspace(0, 10, 5000)
    return np.sin(2 * np.pi * 1.2 * t) + 0.1 * np.random.randn(len(t))
