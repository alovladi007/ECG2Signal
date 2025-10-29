
import matplotlib.pyplot as plt
import numpy as np

def plot_ecg_signals(signals: dict[str, np.ndarray], sample_rate: int, output_path: str | None = None) -> None:
    n_leads = len(signals)
    fig, axes = plt.subplots(n_leads, 1, figsize=(12, n_leads * 2))
    if n_leads == 1:
        axes = [axes]
    
    for (name, signal), ax in zip(signals.items(), axes):
        time = np.arange(len(signal)) / sample_rate
        ax.plot(time, signal, 'k-', linewidth=0.5)
        ax.set_ylabel(name)
        ax.grid(True, alpha=0.3)
    
    axes[-1].set_xlabel('Time (s)')
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
    else:
        plt.show()
