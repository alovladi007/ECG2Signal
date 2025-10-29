
import numpy as np
from ecg2signal.layout.lead_layout import LeadLayoutDetector

def test_layout_detection():
    img = np.ones((1000, 1500, 3), dtype=np.uint8) * 255
    detector = LeadLayoutDetector()
    layout = detector.detect(img)
    
    assert layout.num_leads == 12
    assert layout.layout_type == "12-lead-standard"
