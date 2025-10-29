
import numpy as np

def align_leads(signals: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    max_len = max(len(s) for s in signals.values())
    aligned = {}
    for name, signal in signals.items():
        if len(signal) < max_len:
            padded = np.pad(signal, (0, max_len - len(signal)), mode='edge')
            aligned[name] = padded
        else:
            aligned[name] = signal[:max_len]
    return aligned
