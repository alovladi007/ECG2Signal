
import tempfile
from pathlib import Path
import numpy as np
from ecg2signal.types import ECGResult, PaperSettings, LeadLayout, ECGMetadata, Intervals, QualityMetrics

def test_csv_export():
    signals = {"I": np.random.randn(1000), "II": np.random.randn(1000)}
    result = create_test_result(signals)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        result.export_csv(tmpdir)
        csv_files = list(Path(tmpdir).glob("*.csv"))
        assert len(csv_files) == 2

def test_json_export():
    signals = {"I": np.random.randn(1000)}
    result = create_test_result(signals)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "ecg.json"
        result.export_json(str(output_file))
        assert output_file.exists()

def create_test_result(signals):
    paper_settings = PaperSettings(paper_speed=25.0, gain=10.0, pixels_per_mm=10.0)
    layout = LeadLayout(leads=[], layout_type="test", image_width=1000, image_height=1000)
    metadata = ECGMetadata()
    intervals = Intervals()
    quality = QualityMetrics(snr=20.0, baseline_drift=0.1, coverage=0.9, confidence=0.8)
    
    return ECGResult(
        signals=signals,
        sample_rate=500,
        paper_settings=paper_settings,
        layout=layout,
        metadata=metadata,
        intervals=intervals,
        quality_metrics=quality,
    )
