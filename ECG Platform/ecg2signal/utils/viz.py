"""
Visualization utilities for ECG2Signal.

Beautiful plotting functions for signals, quality metrics, and clinical data.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


def plot_ecg_signals(
    signals: Dict[str, np.ndarray],
    fs: float = 500.0,
    duration: Optional[float] = None,
    title: str = "ECG Signals",
    figsize: Tuple[int, int] = (15, 10)
) -> Figure:
    """
    Plot ECG signals using matplotlib.
    
    Args:
        signals: Dictionary of lead names to signal arrays
        fs: Sampling frequency in Hz
        duration: Duration to plot in seconds (None = all)
        title: Plot title
        figsize: Figure size
        
    Returns:
        Matplotlib figure
    """
    n_leads = len(signals)
    fig, axes = plt.subplots(n_leads, 1, figsize=figsize, sharex=True)
    
    if n_leads == 1:
        axes = [axes]
    
    colors = plt.cm.Set3(np.linspace(0, 1, n_leads))
    
    for idx, (lead_name, signal) in enumerate(signals.items()):
        ax = axes[idx]
        
        # Calculate time array
        if duration:
            n_samples = int(duration * fs)
            signal = signal[:n_samples]
        
        time = np.arange(len(signal)) / fs
        
        # Plot
        ax.plot(time, signal, color=colors[idx], linewidth=1.5, label=lead_name)
        ax.set_ylabel('Amplitude (mV)', fontsize=10)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Add grid lines at standard intervals
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=0.5)
    
    axes[-1].set_xlabel('Time (s)', fontsize=12)
    fig.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    return fig


def create_quality_report(
    results: List[Dict],
    output_path: str
):
    """
    Create comprehensive quality report as HTML.
    
    Args:
        results: List of conversion results
        output_path: Path to save HTML report
    """
    from datetime import datetime
    
    html_parts = [
        "<html>",
        "<head>",
        "<title>ECG2Signal Quality Report</title>",
        "<style>",
        "body { font-family: Arial, sans-serif; margin: 20px; }",
        "h1 { color: #667eea; }",
        "h2 { color: #4ECDC4; margin-top: 30px; }",
        ".summary { background: #f5f5f5; padding: 15px; border-radius: 5px; }",
        ".metric { display: inline-block; margin: 10px; padding: 10px; background: white; border-radius: 5px; }",
        "</style>",
        "</head>",
        "<body>",
        f"<h1>ECG2Signal Quality Report</h1>",
        f"<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
        f"<div class='summary'>",
        f"<h2>Summary</h2>",
        f"<p>Total files processed: {len(results)}</p>",
    ]
    
    # Calculate summary statistics
    quality_scores = [r['result'].quality_metrics.overall_score 
                     for r in results if r['result'].quality_metrics]
    
    if quality_scores:
        html_parts.extend([
            f"<p>Average quality: {np.mean(quality_scores):.2%}</p>",
            f"<p>Min quality: {np.min(quality_scores):.2%}</p>",
            f"<p>Max quality: {np.max(quality_scores):.2%}</p>",
        ])
    
    html_parts.append("</div>")
    
    # Individual results
    for idx, result_data in enumerate(results, 1):
        result = result_data['result']
        filename = result_data['filename']
        
        html_parts.extend([
            f"<h2>Result {idx}: {filename}</h2>",
            "<div class='metric'>",
            f"<strong>Leads:</strong> {len(result.signals)}",
            "</div>",
        ])
        
        if result.quality_metrics:
            html_parts.extend([
                "<div class='metric'>",
                f"<strong>Quality:</strong> {result.quality_metrics.overall_score:.2%}",
                "</div>",
            ])
        
        if result.intervals and result.intervals.get('heart_rate'):
            html_parts.extend([
                "<div class='metric'>",
                f"<strong>Heart Rate:</strong> {result.intervals['heart_rate']:.0f} BPM",
                "</div>",
            ])
    
    html_parts.extend([
        "</body>",
        "</html>"
    ])
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write('\n'.join(html_parts))
