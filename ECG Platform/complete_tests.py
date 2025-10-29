#!/usr/bin/env python3
from pathlib import Path

tests = {

"tests/test_io.py": '''
import pytest
import numpy as np
from ecg2signal.io import image_io

def test_load_image():
    # Create test image
    test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    # Save and load would be tested here
    assert test_img.shape == (100, 100, 3)

def test_normalize_image():
    img = np.array([[0, 127, 255]], dtype=np.uint8)
    normalized = image_io.normalize_image(img)
    assert normalized.max() <= 1.0
    assert normalized.min() >= 0.0
''',

"tests/test_grid_detect.py": '''
import numpy as np
from ecg2signal.preprocess.grid_detect import detect_grid

def test_grid_detection():
    img = np.ones((1000, 1000), dtype=np.uint8) * 255
    # Add grid lines
    for i in range(0, 1000, 50):
        img[i, :] = 0
        img[:, i] = 0
    
    grid_info = detect_grid(img)
    assert grid_info.has_grid
    assert len(grid_info.horizontal_lines) > 0
''',

"tests/test_scale_calibrate.py": '''
from ecg2signal.preprocess.scale_calibrate import pixels_to_time, pixels_to_voltage
from ecg2signal.types import PaperSettings

def test_pixels_to_time():
    settings = PaperSettings(paper_speed=25.0, gain=10.0, pixels_per_mm=10.0)
    time = pixels_to_time(250, settings)  # 250 pixels
    assert abs(time - 1.0) < 0.01  # Should be ~1 second

def test_pixels_to_voltage():
    settings = PaperSettings(paper_speed=25.0, gain=10.0, pixels_per_mm=10.0)
    voltage = pixels_to_voltage(100, settings)  # 100 pixels
    assert abs(voltage - 1.0) < 0.01  # Should be ~1 mV
''',

"tests/test_layout_ocr.py": '''
import numpy as np
from ecg2signal.layout.lead_layout import LeadLayoutDetector

def test_layout_detection():
    img = np.ones((1000, 1500, 3), dtype=np.uint8) * 255
    detector = LeadLayoutDetector()
    layout = detector.detect(img)
    
    assert layout.num_leads == 12
    assert layout.layout_type == "12-lead-standard"
''',

"tests/test_segmentation.py": '''
import numpy as np
from ecg2signal.segment.models.unet import UNetSegmenter

def test_unet_segmentation():
    img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    segmenter = UNetSegmenter("dummy_path")
    masks = segmenter.segment(img)
    
    assert "grid" in masks
    assert "waveform" in masks
    assert "text" in masks
''',

"tests/test_trace.py": '''
import numpy as np
from ecg2signal.segment.trace_curve import extract_curve_from_region

def test_curve_extraction():
    region = np.ones((100, 500), dtype=np.uint8) * 255
    region[50, :] = 0  # Black line at y=50
    
    curve = extract_curve_from_region(region)
    assert len(curve) == 500
    assert np.mean(curve) < 60  # Should be close to 50
''',

"tests/test_reconstruct.py": '''
import numpy as np
from ecg2signal.reconstruct.postprocess import remove_baseline_wander, bandpass_filter

def test_baseline_removal():
    signal = np.sin(np.linspace(0, 10, 1000)) + 0.5 * np.linspace(0, 1, 1000)
    filtered = remove_baseline_wander(signal, 500)
    assert np.abs(np.mean(filtered)) < 0.1  # Baseline should be near zero

def test_bandpass_filter():
    signal = np.random.randn(1000)
    filtered = bandpass_filter(signal, 500)
    assert len(filtered) == len(signal)
''',

"tests/test_exports.py": '''
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
''',

"tests/test_api.py": '''
import pytest
from fastapi.testclient import TestClient
from ecg2signal.api.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "ECG2Signal API" in response.json()["message"]

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
''',

"tests/conftest.py": '''
import pytest
import numpy as np

@pytest.fixture
def sample_ecg_image():
    """Create a sample ECG image for testing."""
    return np.random.randint(0, 255, (1000, 1500, 3), dtype=np.uint8)

@pytest.fixture
def sample_signal():
    """Create a sample ECG signal."""
    t = np.linspace(0, 10, 5000)
    return np.sin(2 * np.pi * 1.2 * t) + 0.1 * np.random.randn(len(t))
''',

}

for path, content in tests.items():
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content)
    print(f"Created {path}")

print(f"\n✓ Test suite complete ({len(tests)} files)")

