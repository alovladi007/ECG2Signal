"""
ECG2Signal: Production-grade ECG image to digital signal conversion.

This package provides tools to convert ECG images (scans, photos, PDFs) into
calibrated digital time-series signals with support for multiple clinical formats.
"""

try:
    from importlib.metadata import version
    __version__ = version("ecg2signal")
except Exception:
    __version__ = "0.1.0"

from ecg2signal.config import Settings
from ecg2signal.types import (
    ECGLead,
    ECGResult,
    ExportFormat,
    LeadLayout,
    PaperSettings,
    QualityMetrics,
)
__all__ = [
    "ECGConverter",
    "Settings",
    "ECGResult",
    "ECGLead",
    "PaperSettings",
    "LeadLayout",
    "QualityMetrics",
    "ExportFormat",
]


class ECGConverter:
    """
    Main converter class for ECG image to signal conversion.

    Example:
        >>> from ecg2signal import ECGConverter
        >>> converter = ECGConverter()
        >>> result = converter.convert("ecg_image.jpg")
        >>> result.export_wfdb("output/")
    """

    def __init__(self, settings: Settings | None = None):
        """
        Initialize the ECG converter.

        Args:
            settings: Configuration settings. If None, uses default settings.
        """
        from ecg2signal.logging_conf import setup_logging

        self.settings = settings or Settings()
        setup_logging(self.settings.log_level)

        # Lazy load heavy dependencies
        self._models_loaded = False
        self._models: dict = {}

    def _load_models(self) -> None:
        """Load ML models on first use."""
        if self._models_loaded:
            return

        from ecg2signal.layout.lead_layout import LeadLayoutDetector
        from ecg2signal.layout.ocr_labels import OCREngine
        from ecg2signal.segment.models.unet import UNetSegmenter

        self._models["unet"] = UNetSegmenter(self.settings.unet_model_path)
        self._models["ocr"] = OCREngine(self.settings.ocr_model_path)
        self._models["layout"] = LeadLayoutDetector(self.settings.layout_model_path)
        self._models_loaded = True

    def convert(
        self,
        input_path: str,
        paper_speed: float | None = None,
        gain: float | None = None,
        sample_rate: int | None = None,
    ) -> ECGResult:
        """
        Convert an ECG image to digital signals.

        Args:
            input_path: Path to input image or PDF
            paper_speed: Paper speed in mm/s (default: 25)
            gain: Gain in mm/mV (default: 10)
            sample_rate: Output sampling rate in Hz (default: 500)

        Returns:
            ECGResult containing signals, metadata, and quality metrics

        Raises:
            ValueError: If input file is invalid or processing fails
            FileNotFoundError: If input file doesn't exist
        """
        from pathlib import Path

        from loguru import logger

        from ecg2signal.clinical.intervals import compute_intervals
        from ecg2signal.clinical.quality import compute_quality_metrics
        from ecg2signal.io.image_io import load_image
        from ecg2signal.io.pdf import extract_pdf_pages
        from ecg2signal.preprocess.denoise import denoise_image
        from ecg2signal.preprocess.detect_page import detect_page_region
        from ecg2signal.preprocess.dewarp import dewarp_image
        from ecg2signal.preprocess.grid_detect import detect_grid
        from ecg2signal.preprocess.scale_calibrate import calibrate_scale
        from ecg2signal.reconstruct.align_leads import align_leads
        from ecg2signal.reconstruct.postprocess import postprocess_signals
        from ecg2signal.reconstruct.raster_to_signal import raster_to_signal
        from ecg2signal.reconstruct.resample import resample_signals
        from ecg2signal.segment.separate_layers import separate_layers
        from ecg2signal.segment.trace_curve import trace_curves

        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        logger.info(f"Processing ECG: {input_path}")

        # Load models
        self._load_models()

        # Step 1: Load image
        if input_file.suffix.lower() == ".pdf":
            pages = extract_pdf_pages(str(input_file))
            if not pages:
                raise ValueError("No pages extracted from PDF")
            image = pages[0]  # Process first page
            logger.info(f"Extracted {len(pages)} pages from PDF")
        else:
            image = load_image(str(input_file))

        logger.info(f"Loaded image: {image.shape}")

        # Step 2: Preprocessing
        page_region = detect_page_region(image)
        image_clean = denoise_image(page_region)
        image_dewarped = dewarp_image(image_clean)

        # Step 3: Grid detection and calibration
        grid_info = detect_grid(image_dewarped)
        paper_settings = calibrate_scale(
            image_dewarped,
            grid_info,
            paper_speed=paper_speed or self.settings.default_paper_speed,
            gain=gain or self.settings.default_gain,
        )

        logger.info(f"Calibration: {paper_settings.pixels_per_mm:.2f} px/mm")

        # Step 4: Layout detection and OCR
        layout = self._models["layout"].detect(image_dewarped)
        metadata = self._models["ocr"].extract_metadata(image_dewarped, layout)

        logger.info(f"Detected {len(layout.lead_boxes)} leads")

        # Step 5: Segmentation
        masks = self._models["unet"].segment(image_dewarped)
        layer_images = separate_layers(image_dewarped, masks)

        # Step 6: Trace extraction
        curves = trace_curves(layer_images["waveform"], layout)

        # Step 7: Signal reconstruction
        raw_signals = raster_to_signal(curves, paper_settings, layout)
        target_sr = sample_rate or self.settings.default_sample_rate
        signals = resample_signals(raw_signals, paper_settings, target_sr)
        signals = align_leads(signals)
        signals = postprocess_signals(signals, target_sr)

        logger.info(f"Reconstructed {len(signals)} signals at {target_sr} Hz")

        # Step 8: Clinical analysis
        intervals = compute_intervals(signals, target_sr)
        quality = compute_quality_metrics(signals, target_sr)

        # Build result
        result = ECGResult(
            signals=signals,
            sample_rate=target_sr,
            paper_settings=paper_settings,
            layout=layout,
            metadata=metadata,
            intervals=intervals,
            quality_metrics=quality,
        )

        logger.info(f"Processing complete. Quality score: {quality.overall_score:.2f}")
        return result

    def convert_batch(
        self,
        input_paths: list[str],
        output_dir: str,
        **kwargs,
    ) -> list[ECGResult]:
        """
        Convert multiple ECG images in batch.

        Args:
            input_paths: List of input file paths
            output_dir: Directory for outputs
            **kwargs: Arguments passed to convert()

        Returns:
            List of ECGResult objects
        """
        from pathlib import Path

        from loguru import logger
        from tqdm import tqdm

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results = []
        for input_path in tqdm(input_paths, desc="Converting ECGs"):
            try:
                result = self.convert(input_path, **kwargs)
                results.append(result)

                # Auto-export
                stem = Path(input_path).stem
                result.export_wfdb(str(output_path / stem))
            except Exception as e:
                logger.error(f"Failed to convert {input_path}: {e}")
                results.append(None)

        return results
