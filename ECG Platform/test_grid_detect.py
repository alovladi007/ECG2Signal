
import numpy as np
from ecg2signal.preprocess.grid_detect import detect_grid

def test_grid_detection():
    img = np.ones((1000, 1000), dtype=np.uint8) * 255
    # Add grid lines
    for i in range(0, 1000, 50):
        img[i, :] = 0
        img[:, i] = 0
    
    grid_info = detect_grid(img)
    assert grid_info.has_grid
    assert len(grid_info.horizontal_lines) > 0
