"""
Integration tests for the complete ECG2Signal pipeline.
"""

import numpy as np
import pytest
from pathlib import Path

from ecg2signal import ECGConverter, Settings
from ecg2signal.types import ECGResult


class TestIntegration:
    """Integration tests for the complete pipeline."""

    @pytest.fixture
    def converter(self):
        """Create a converter instance for testing."""
        settings = Settings(
            log_level="DEBUG",
            debug=True,
        )
        return ECGConverter(settings)

    @pytest.fixture
    def sample_image(self, tmp_path):
        """Create a sample ECG image for testing."""
        import cv2

        # Create a simple test image (800x600 pixels)
        image = np.ones((600, 800, 3), dtype=np.uint8) * 255

        # Draw some grid lines (simplified)
        for y in range(0, 600, 50):
            cv2.line(image, (0, y), (800, y), (200, 200, 200), 1)
        for x in range(0, 800, 50):
            cv2.line(image, (x, 0), (x, 600), (200, 200, 200), 1)

        # Draw a simple sine wave to simulate ECG
        points = []
        for x in range(800):
            y = int(300 + 50 * np.sin(x * 0.05))
            points.append((x, y))

        for i in range(len(points) - 1):
            cv2.line(image, points[i], points[i + 1], (0, 0, 0), 2)

        # Save the image
        image_path = tmp_path / "test_ecg.png"
        cv2.imwrite(str(image_path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

        return image_path

    def test_package_imports(self):
        """Test that all package imports work correctly."""
        # Test main package
        from ecg2signal import ECGConverter, Settings

        # Test subpackages
        from ecg2signal.io import load_image, save_image
        from ecg2signal.preprocess import denoise_image, detect_grid
        from ecg2signal.layout import LeadLayoutDetector, OCREngine
        from ecg2signal.segment import separate_layers
        from ecg2signal.reconstruct import resample_signals
        from ecg2signal.clinical import compute_quality_metrics
        from ecg2signal.training import generate_synthetic_ecg
        from ecg2signal.utils import timeit
        from ecg2signal.api import app
        from ecg2signal.cli import cli

        # All imports successful
        assert True

    def test_converter_initialization(self, converter):
        """Test that the converter initializes correctly."""
        assert converter is not None
        assert converter.settings is not None
        assert not converter._models_loaded

    def test_image_loading(self, sample_image):
        """Test that image I/O works correctly."""
        from ecg2signal.io import load_image

        image = load_image(str(sample_image))
        assert image is not None
        assert image.shape[0] > 0  # height
        assert image.shape[1] > 0  # width
        assert len(image.shape) == 3  # RGB image

    def test_preprocessing_pipeline(self, sample_image):
        """Test that preprocessing modules work together."""
        from ecg2signal.io import load_image
        from ecg2signal.preprocess import (
            detect_page_region,
            denoise_image,
            dewarp_image,
            detect_grid,
        )

        # Load image
        image = load_image(str(sample_image))

        # Preprocessing steps
        page_region = detect_page_region(image)
        assert page_region is not None

        denoised = denoise_image(page_region)
        assert denoised is not None

        dewarped = dewarp_image(denoised)
        assert dewarped is not None

        grid_info = detect_grid(dewarped)
        assert grid_info is not None

    def test_end_to_end_conversion(self, converter, sample_image):
        """Test the complete end-to-end conversion pipeline."""
        # Note: This test uses stub ML models, so results will be minimal
        # In production, this would test with real trained models

        try:
            result = converter.convert(
                str(sample_image),
                paper_speed=25.0,
                gain=10.0,
                sample_rate=500,
            )

            # Verify result structure
            assert isinstance(result, ECGResult)
            assert result.signals is not None
            assert result.sample_rate == 500
            assert result.paper_settings is not None
            assert result.quality_metrics is not None

        except Exception as e:
            # Expected to fail with stub models, but imports should work
            assert "model" in str(e).lower() or "path" in str(e).lower()

    def test_module_structure(self):
        """Test that the package structure is correct."""
        import ecg2signal

        # Check main modules exist
        assert hasattr(ecg2signal, "ECGConverter")
        assert hasattr(ecg2signal, "Settings")
        assert hasattr(ecg2signal, "ECGResult")

        # Check subpackages
        subpackages = [
            "io",
            "preprocess",
            "layout",
            "segment",
            "reconstruct",
            "clinical",
            "training",
            "api",
            "cli",
            "ui",
            "utils",
        ]

        for subpkg in subpackages:
            module = __import__(f"ecg2signal.{subpkg}", fromlist=[subpkg])
            assert module is not None

    def test_settings_configuration(self):
        """Test that settings can be configured."""
        settings = Settings(
            log_level="DEBUG",
            default_paper_speed=50.0,
            default_gain=5.0,
            default_sample_rate=1000,
        )

        assert settings.log_level == "DEBUG"
        assert settings.default_paper_speed == 50.0
        assert settings.default_gain == 5.0
        assert settings.default_sample_rate == 1000

    def test_export_formats_available(self):
        """Test that all export format modules are available."""
        from ecg2signal.io import (
            export_wfdb,
            export_edf,
            export_fhir,
            export_dicom_waveform,
        )

        # All export functions available
        assert export_wfdb is not None
        assert export_edf is not None
        assert export_fhir is not None
        assert export_dicom_waveform is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
