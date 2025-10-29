
import numpy as np
from loguru import logger
from ecg2signal.types import LeadLayout, ECGLead, BoundingBox, LeadName

class LeadLayoutDetector:
    def __init__(self, model_path: str | None = None):
        self.model_path = model_path
        
    def detect(self, image: np.ndarray) -> LeadLayout:
        h, w = image.shape[:2]
        leads = self._detect_standard_layout(image)
        rhythm_strip = self._detect_rhythm_strip(image, leads)
        return LeadLayout(leads=leads, rhythm_strip=rhythm_strip,
                         layout_type="12-lead-standard", image_width=w, image_height=h)
    
    def _detect_standard_layout(self, image: np.ndarray) -> list[ECGLead]:
        h, w = image.shape[:2]
        leads, lead_names = [], [LeadName.I, LeadName.AVR, LeadName.V1, LeadName.V4,
                     LeadName.II, LeadName.AVL, LeadName.V2, LeadName.V5,
                     LeadName.III, LeadName.AVF, LeadName.V3, LeadName.V6]
        rhythm_boundary, lead_height, lead_width = int(h * 0.75), int(h * 0.75) // 4, w // 3
        idx = 0
        for row in range(4):
            for col in range(3):
                if idx >= len(lead_names): break
                leads.append(ECGLead(name=lead_names[idx], box=BoundingBox(
                    x=col*lead_width, y=row*lead_height, width=lead_width, height=lead_height, confidence=0.9)))
                idx += 1
        return leads
    
    def _detect_rhythm_strip(self, image: np.ndarray, leads: list[ECGLead]) -> ECGLead | None:
        if not leads: return None
        h, w, max_y = image.shape[:2][0], image.shape[:2][1], max(lead.box.y2 for lead in leads)
        if max_y < h * 0.8 and (rhythm_height := h - max_y) > 50:
            return ECGLead(name=LeadName.RHYTHM, box=BoundingBox(x=0, y=max_y, width=w, height=rhythm_height, confidence=0.8))
        return None
