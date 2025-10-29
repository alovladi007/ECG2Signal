
import numpy as np

def separate_layers(image: np.ndarray, masks: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    return {"waveform": image, "grid": np.zeros_like(image), "text": np.zeros_like(image)}
