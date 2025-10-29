"""
Core data types and models for ECG2Signal.
"""

from enum import Enum
from typing import Any

import numpy as np
from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    """Supported export formats."""

    CSV = "csv"
    WFDB = "wfdb"
    EDF = "edf"
    JSON = "json"
    FHIR = "fhir"
    DICOM = "dicom"


class LeadName(str, Enum):
    """Standard 12-lead ECG lead names."""

    I = "I"
    II = "II"
    III = "III"
    AVR = "aVR"
    AVL = "aVL"
    AVF = "aVF"
    V1 = "V1"
    V2 = "V2"
    V3 = "V3"
    V4 = "V4"
    V5 = "V5"
    V6 = "V6"
    RHYTHM = "RHYTHM"  # Long rhythm strip


class PaperSettings(BaseModel):
    """ECG paper settings and calibration."""

    paper_speed: float = Field(25.0, description="Paper speed in mm/s")
    gain: float = Field(10.0, description="Gain in mm/mV")
    pixels_per_mm: float = Field(..., description="Calibration: pixels per mm")
    major_grid_mm: float = Field(5.0, description="Major grid spacing in mm")
    minor_grid_mm: float = Field(1.0, description="Minor grid spacing in mm")

    @property
    def pixels_per_second(self) -> float:
        """Calculate pixels per second."""
        return self.pixels_per_mm * self.paper_speed

    @property
    def pixels_per_mv(self) -> float:
        """Calculate pixels per millivolt."""
        return self.pixels_per_mm * self.gain

    class Config:
        frozen = True


class BoundingBox(BaseModel):
    """Bounding box for region detection."""

    x: int
    y: int
    width: int
    height: int
    confidence: float = 1.0

    @property
    def x2(self) -> int:
        return self.x + self.width

    @property
    def y2(self) -> int:
        return self.y + self.height

    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

    @property
    def area(self) -> int:
        return self.width * self.height


class ECGLead(BaseModel):
    """Single ECG lead information."""

    name: LeadName
    box: BoundingBox
    signal: list[float] | None = None
    duration_sec: float | None = None
    sample_rate: int | None = None

    class Config:
        arbitrary_types_allowed = True


class LeadLayout(BaseModel):
    """Layout information for 12-lead ECG."""

    leads: list[ECGLead]
    rhythm_strip: ECGLead | None = None
    layout_type: str = "12-lead-standard"  # or "3x4", "12x1", etc.
    image_width: int
    image_height: int

    @property
    def lead_boxes(self) -> dict[str, BoundingBox]:
        """Get mapping of lead names to bounding boxes."""
        return {lead.name.value: lead.box for lead in self.leads}

    @property
    def num_leads(self) -> int:
        """Get number of leads detected."""
        return len(self.leads)


class GridInfo(BaseModel):
    """Grid detection information."""

    has_grid: bool
    horizontal_lines: list[int] = Field(default_factory=list)
    vertical_lines: list[int] = Field(default_factory=list)
    grid_spacing_x: float | None = None
    grid_spacing_y: float | None = None
    grid_angle: float = 0.0  # Rotation angle in degrees
    confidence: float = 0.0


class ECGMetadata(BaseModel):
    """ECG metadata extracted from image."""

    patient_id: str | None = None
    patient_name: str | None = None
    age: int | None = None
    gender: str | None = None
    acquisition_date: str | None = None
    acquisition_time: str | None = None
    device_id: str | None = None
    hospital: str | None = None
    paper_speed: float | None = None
    gain: float | None = None
    filter_settings: str | None = None
    interpretation: str | None = None


class Intervals(BaseModel):
    """Clinical interval measurements."""

    heart_rate: float | None = Field(None, description="Heart rate in BPM")
    pr_interval: float | None = Field(None, description="PR interval in ms")
    qrs_duration: float | None = Field(None, description="QRS duration in ms")
    qt_interval: float | None = Field(None, description="QT interval in ms")
    qtc_interval: float | None = Field(None, description="QTc interval (corrected) in ms")
    rr_intervals: list[float] = Field(default_factory=list, description="RR intervals in ms")
    p_wave_duration: float | None = None
    t_wave_duration: float | None = None

    @property
    def is_normal(self) -> bool:
        """Check if intervals are within normal ranges."""
        checks = []
        if self.pr_interval:
            checks.append(120 <= self.pr_interval <= 200)
        if self.qrs_duration:
            checks.append(self.qrs_duration <= 120)
        if self.qtc_interval:
            checks.append(self.qtc_interval <= 450)
        return all(checks) if checks else False


class QualityMetrics(BaseModel):
    """Signal quality metrics."""

    snr: float = Field(..., description="Signal-to-noise ratio in dB")
    baseline_drift: float = Field(..., description="Baseline drift magnitude")
    clipping_ratio: float = Field(0.0, description="Fraction of clipped samples")
    coverage: float = Field(..., description="Fraction of valid signal coverage")
    confidence: float = Field(..., description="Overall confidence score")
    lead_quality: dict[str, float] = Field(default_factory=dict)

    @property
    def overall_score(self) -> float:
        """Compute overall quality score (0-1)."""
        score = 0.0
        score += min(self.snr / 30.0, 1.0) * 0.3  # SNR weight
        score += (1.0 - min(self.baseline_drift, 1.0)) * 0.2  # Drift weight
        score += (1.0 - self.clipping_ratio) * 0.2  # Clipping weight
        score += self.coverage * 0.2  # Coverage weight
        score += self.confidence * 0.1  # Confidence weight
        return max(0.0, min(1.0, score))

    @property
    def is_acceptable(self) -> bool:
        """Check if quality meets minimum standards."""
        return (
            self.snr >= 10.0
            and self.baseline_drift <= 0.3
            and self.clipping_ratio <= 0.05
            and self.coverage >= 0.8
        )


class ECGResult(BaseModel):
    """Complete ECG conversion result."""

    signals: dict[str, np.ndarray] = Field(..., description="Lead name -> signal array")
    sample_rate: int = Field(..., description="Sampling rate in Hz")
    paper_settings: PaperSettings
    layout: LeadLayout
    metadata: ECGMetadata
    intervals: Intervals
    quality_metrics: QualityMetrics

    class Config:
        arbitrary_types_allowed = True

    @property
    def duration_seconds(self) -> float:
        """Get signal duration in seconds."""
        if not self.signals:
            return 0.0
        first_signal = next(iter(self.signals.values()))
        return len(first_signal) / self.sample_rate

    @property
    def num_samples(self) -> int:
        """Get number of samples per lead."""
        if not self.signals:
            return 0
        first_signal = next(iter(self.signals.values()))
        return len(first_signal)

    def export_wfdb(self, output_dir: str, record_name: str = "ecg") -> None:
        """
        Export signals to WFDB format.

        Args:
            output_dir: Output directory path
            record_name: Record name (default: "ecg")
        """
        from ecg2signal.io.wfdb_io import write_wfdb

        write_wfdb(self, output_dir, record_name)

    def export_edf(self, output_path: str) -> None:
        """
        Export signals to EDF+ format.

        Args:
            output_path: Output file path
        """
        from ecg2signal.io.edf_io import write_edf

        write_edf(self, output_path)

    def export_fhir(self, patient_id: str, output_path: str) -> None:
        """
        Export to HL7 FHIR Observation format.

        Args:
            patient_id: Patient identifier
            output_path: Output JSON file path
        """
        from ecg2signal.io.fhir import write_fhir_observation

        write_fhir_observation(self, patient_id, output_path)

    def export_dicom(self, output_path: str) -> None:
        """
        Export to DICOM Waveform format.

        Args:
            output_path: Output DICOM file path
        """
        from ecg2signal.io.dcm_waveform import write_dicom_waveform

        write_dicom_waveform(self, output_path)

    def export_csv(self, output_dir: str) -> None:
        """
        Export signals to CSV files (one per lead).

        Args:
            output_dir: Output directory path
        """
        from pathlib import Path

        import pandas as pd

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for lead_name, signal in self.signals.items():
            time = np.arange(len(signal)) / self.sample_rate
            df = pd.DataFrame({"time_sec": time, "amplitude_mv": signal})
            df.to_csv(output_path / f"{lead_name}.csv", index=False)

    def export_json(self, output_path: str) -> None:
        """
        Export to JSON format with metadata.

        Args:
            output_path: Output JSON file path
        """
        import json
        from pathlib import Path

        data = {
            "sample_rate": self.sample_rate,
            "duration_seconds": self.duration_seconds,
            "num_samples": self.num_samples,
            "paper_settings": self.paper_settings.dict(),
            "metadata": self.metadata.dict(),
            "intervals": self.intervals.dict(),
            "quality_metrics": self.quality_metrics.dict(),
            "signals": {name: sig.tolist() for name, sig in self.signals.items()},
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

    def export_all(self, output_dir: str, record_name: str = "ecg") -> None:
        """
        Export to all supported formats.

        Args:
            output_dir: Output directory path
            record_name: Base record name
        """
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self.export_csv(str(output_path / "csv"))
        self.export_wfdb(str(output_path / "wfdb"), record_name)
        self.export_edf(str(output_path / f"{record_name}.edf"))
        self.export_json(str(output_path / f"{record_name}.json"))


class ProcessingConfig(BaseModel):
    """Configuration for processing pipeline."""

    use_gpu: bool = True
    batch_size: int = 1
    num_workers: int = 4
    enable_cache: bool = True
    min_quality_score: float = 0.6
    auto_orientation: bool = True
    denoise: bool = True
    remove_grid: bool = True
