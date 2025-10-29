
import numpy as np
from ecg2signal.segment.models.unet import UNetSegmenter

def test_unet_segmentation():
    img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    segmenter = UNetSegmenter("dummy_path")
    masks = segmenter.segment(img)
    
    assert "grid" in masks
    assert "waveform" in masks
    assert "text" in masks
