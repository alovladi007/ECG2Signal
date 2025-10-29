
import numpy as np
from ecg2signal.types import ECGMetadata, LeadLayout

class OCREngine:
    def __init__(self, model_path: str | None = None):
        self.model_path = model_path
        
    def extract_metadata(self, image: np.ndarray, layout: LeadLayout) -> ECGMetadata:
        return ECGMetadata(patient_id="UNKNOWN", paper_speed=25.0, gain=10.0)
