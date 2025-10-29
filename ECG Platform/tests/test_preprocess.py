
"""Tests for preprocessing modules."""
import numpy as np
from ecg2signal.preprocess import detect_page, denoise, dewarp

def test_detect_page():
    img = np.random.randint(0, 255, (1000, 1000, 3), dtype=np.uint8)
    result = detect_page.detect_page_region(img)
    assert result.shape[0] > 0 and result.shape[1] > 0
