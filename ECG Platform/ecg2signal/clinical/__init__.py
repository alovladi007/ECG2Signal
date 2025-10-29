"""
Clinical analysis module for ECG metrics and quality assessment.

This module provides comprehensive clinical analysis including:
- Basic interval measurements (PR, QRS, QT)
- Quality metrics and assessment
- Advanced arrhythmia detection (13 types)
- QT interval analysis with multiple correction formulas
- Automated clinical findings and interpretation
- Professional PDF report generation
"""

from ecg2signal.clinical.intervals import compute_intervals
from ecg2signal.clinical.quality import compute_quality_metrics
from ecg2signal.clinical.reports import generate_pdf_report

# Advanced clinical features (Option E)
from ecg2signal.clinical.arrhythmia import ArrhythmiaDetector, detect_arrhythmias
from ecg2signal.clinical.qt_analysis import QTAnalyzer, analyze_qt
from ecg2signal.clinical.findings import ClinicalInterpreter, interpret_ecg

__all__ = [
    # Basic analysis
    "compute_intervals",
    "compute_quality_metrics",
    "generate_pdf_report",

    # Advanced arrhythmia detection
    "ArrhythmiaDetector",
    "detect_arrhythmias",

    # QT interval analysis
    "QTAnalyzer",
    "analyze_qt",

    # Clinical interpretation
    "ClinicalInterpreter",
    "interpret_ecg",
]
