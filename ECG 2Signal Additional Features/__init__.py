"""
Clinical analysis module for ECG2Signal.

Provides comprehensive clinical analysis including:
- Interval measurements (PR, QRS, QT, RR)
- Arrhythmia detection
- QT interval analysis
- Automated clinical findings
- Quality assessment
- PDF report generation
"""

from ecg2signal.clinical.arrhythmia import (
    ArrhythmiaDetection,
    ArrhythmiaDetector,
    ArrhythmiaReport,
    ArrhythmiaType,
)
from ecg2signal.clinical.findings import (
    AutomatedFindings,
    ClinicalConclusion,
    ClinicalFinding,
    ClinicalInterpreter,
    FindingCategory,
    Severity,
)
from ecg2signal.clinical.intervals import compute_intervals
from ecg2signal.clinical.quality import compute_quality_metrics
from ecg2signal.clinical.qt_analysis import (
    QTAnalysis,
    QTAnalyzer,
    QTCorrectionMethod,
    QTDispersion,
    QTMeasurement,
    QTRiskLevel,
)
from ecg2signal.clinical.reports import generate_pdf_report

__all__ = [
    # Intervals
    "compute_intervals",
    # Arrhythmia
    "ArrhythmiaType",
    "ArrhythmiaDetection",
    "ArrhythmiaReport",
    "ArrhythmiaDetector",
    # QT Analysis
    "QTCorrectionMethod",
    "QTRiskLevel",
    "QTMeasurement",
    "QTDispersion",
    "QTAnalysis",
    "QTAnalyzer",
    # Clinical Findings
    "Severity",
    "FindingCategory",
    "ClinicalFinding",
    "ClinicalConclusion",
    "AutomatedFindings",
    "ClinicalInterpreter",
    # Quality
    "compute_quality_metrics",
    # Reports
    "generate_pdf_report",
]
