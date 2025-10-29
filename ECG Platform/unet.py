
import numpy as np
from loguru import logger

class UNetSegmenter:
    def __init__(self, model_path: str):
        self.model_path = model_path
        logger.info(f"Initialized U-Net segmenter")
        
    def segment(self, image: np.ndarray) -> dict[str, np.ndarray]:
        h, w = image.shape[:2]
        return {
            "grid": np.zeros((h, w), dtype=np.uint8),
            "waveform": np.ones((h, w), dtype=np.uint8) * 255,
            "text": np.zeros((h, w), dtype=np.uint8),
        }
