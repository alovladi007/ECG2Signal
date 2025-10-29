#!/bin/bash
cd /home/claude/ecg2signal

# Recreate all module files by copying from earlier
# Since they were deleted, let me recreate the structure properly

# Create all __init__.py files
for dir in ecg2signal/{io,preprocess,layout,segment,segment/models,reconstruct,clinical,training,training/data_synth,training/configs,api,api/routes,cli,ui,ui/assets,utils}; do
    touch "$dir/__init__.py"
done

echo "Created all __init__.py files"

# Create remaining layout modules
cat > ecg2signal/layout/lead_layout.py << 'EOF'
"""ECG lead layout detection."""
import numpy as np
import cv2
from loguru import logger
from ecg2signal.types import LeadLayout, ECGLead, BoundingBox, LeadName

class LeadLayoutDetector:
    def __init__(self, model_path: str | None = None):
        self.model_path = model_path
        
    def detect(self, image: np.ndarray) -> LeadLayout:
        h, w = image.shape[:2]
        layout_type = "12-lead-standard"
        leads = self._detect_standard_layout(image)
        rhythm_strip = self._detect_rhythm_strip(image, leads)
        
        return LeadLayout(leads=leads, rhythm_strip=rhythm_strip,
                         layout_type=layout_type, image_width=w, image_height=h)
    
    def _detect_standard_layout(self, image: np.ndarray) -> list[ECGLead]:
        h, w = image.shape[:2]
        leads = []
        lead_names = [LeadName.I, LeadName.AVR, LeadName.V1, LeadName.V4,
                     LeadName.II, LeadName.AVL, LeadName.V2, LeadName.V5,
                     LeadName.III, LeadName.AVF, LeadName.V3, LeadName.V6]
        
        rhythm_boundary = int(h * 0.75)
        lead_height = rhythm_boundary // 4
        lead_width = w // 3
        
        idx = 0
        for row in range(4):
            for col in range(3):
                if idx >= len(lead_names):
                    break
                box = BoundingBox(x=col*lead_width, y=row*lead_height,
                                width=lead_width, height=lead_height, confidence=0.9)
                leads.append(ECGLead(name=lead_names[idx], box=box))
                idx += 1
        return leads
    
    def _detect_rhythm_strip(self, image: np.ndarray, leads: list[ECGLead]) -> ECGLead | None:
        if not leads:
            return None
        h, w = image.shape[:2]
        max_y = max(lead.box.y2 for lead in leads)
        if max_y < h * 0.8:
            rhythm_height = h - max_y
            if rhythm_height > 50:
                box = BoundingBox(x=0, y=max_y, width=w, height=rhythm_height, confidence=0.8)
                return ECGLead(name=LeadName.RHYTHM, box=box)
        return None
EOF

cat > ecg2signal/layout/ocr_labels.py << 'EOF'
"""OCR engine for extracting ECG labels and metadata."""
import numpy as np
from loguru import logger
from ecg2signal.types import ECGMetadata, LeadLayout

class OCREngine:
    def __init__(self, model_path: str | None = None):
        self.model_path = model_path
        
    def extract_metadata(self, image: np.ndarray, layout: LeadLayout) -> ECGMetadata:
        # Simplified OCR - in production use transformer model
        return ECGMetadata(
            patient_id="UNKNOWN",
            paper_speed=25.0,
            gain=10.0,
        )
EOF

echo "Created layout modules"
