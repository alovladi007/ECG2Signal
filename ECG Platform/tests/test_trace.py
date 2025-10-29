
import numpy as np
from ecg2signal.segment.trace_curve import extract_curve_from_region

def test_curve_extraction():
    region = np.ones((100, 500), dtype=np.uint8) * 255
    region[50, :] = 0  # Black line at y=50
    
    curve = extract_curve_from_region(region)
    assert len(curve) == 500
    assert np.mean(curve) < 60  # Should be close to 50
