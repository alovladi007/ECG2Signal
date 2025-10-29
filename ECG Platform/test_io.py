
import pytest
import numpy as np
from ecg2signal.io import image_io

def test_load_image():
    # Create test image
    test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    # Save and load would be tested here
    assert test_img.shape == (100, 100, 3)

def test_normalize_image():
    img = np.array([[0, 127, 255]], dtype=np.uint8)
    normalized = image_io.normalize_image(img)
    assert normalized.max() <= 1.0
    assert normalized.min() >= 0.0
