
"""Render synthetic ECG images."""
import numpy as np
import matplotlib.pyplot as plt

def render_ecg_to_image(signal, paper_speed=25.0, gain=10.0, dpi=300):
    """Render ECG signal to image with grid."""
    duration = len(signal) / 500  # Assume 500 Hz
    
    fig, ax = plt.subplots(figsize=(10, 4), dpi=dpi)
    time = np.arange(len(signal)) / 500
    ax.plot(time, signal, 'k-', linewidth=0.5)
    ax.grid(True, which='both', linestyle='-', linewidth=0.3, alpha=0.5)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude (mV)')
    
    # Convert to image
    fig.canvas.draw()
    img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    plt.close(fig)
    
    return img
