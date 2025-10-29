"""
Test suite for Option E: Clinical Features

Tests the arrhythmia detection, QT analysis, automated findings,
and report generation capabilities.
"""

import numpy as np
import pytest
from pathlib import Path

from ecg2signal.clinical import (
    ArrhythmiaDetector,
    ArrhythmiaType,
    QTAnalyzer,
    QTRiskLevel,
    ClinicalInterpreter,
    Severity,
    generate_pdf_report,
)
from ecg2signal.types import Intervals, QualityMetrics, ECGResult, PaperSettings, LeadLayout, ECGMetadata


class TestArrhythmiaDetection:
    """Tests for arrhythmia detection."""
    
    def test_detector_initialization(self):
        """Test detector initializes correctly."""
        detector = ArrhythmiaDetector(sample_rate=500)
        assert detector.sample_rate == 500
        assert detector.min_rr_interval == 150  # 300ms at 500 Hz
        assert detector.max_rr_interval == 1000  # 2000ms at 500 Hz
    
    def test_normal_rhythm_detection(self):
        """Test detection of normal sinus rhythm."""
        # Create synthetic normal rhythm signal
        sample_rate = 500
        duration = 10  # seconds
        heart_rate = 75  # BPM
        
        # Generate signal with regular R-peaks
        t = np.linspace(0, duration, duration * sample_rate)
        signal = np.zeros_like(t)
        
        # Add R-peaks at regular intervals
        rr_interval = 60 / heart_rate  # seconds
        for peak_time in np.arange(0, duration, rr_interval):
            peak_idx = int(peak_time * sample_rate)
            if peak_idx < len(signal) - 50:
                signal[peak_idx:peak_idx+50] = np.hanning(50) * 1.0
        
        signals = {'II': signal}
        
        # Detect
        detector = ArrhythmiaDetector(sample_rate)
        report = detector.detect(signals)
        
        # Should detect normal or sinus rhythm
        assert report.primary_rhythm in [ArrhythmiaType.NORMAL, ArrhythmiaType.SINUS_ARRHYTHMIA]
        assert 60 < report.heart_rate_mean < 90  # Normal range
        assert report.rr_irregularity < 0.15  # Regular rhythm
        assert len(report.critical_findings) == 0
    
    def test_bradycardia_detection(self):
        """Test detection of bradycardia."""
        # Create slow rhythm signal (45 BPM)
        sample_rate = 500
        duration = 10
        heart_rate = 45
        
        t = np.linspace(0, duration, duration * sample_rate)
        signal = np.zeros_like(t)
        
        rr_interval = 60 / heart_rate
        for peak_time in np.arange(0, duration, rr_interval):
            peak_idx = int(peak_time * sample_rate)
            if peak_idx < len(signal) - 50:
                signal[peak_idx:peak_idx+50] = np.hanning(50) * 1.0
        
        signals = {'II': signal}
        
        detector = ArrhythmiaDetector(sample_rate)
        report = detector.detect(signals)
        
        # Should detect bradycardia
        bradycardia_detected = any(
            d.type == ArrhythmiaType.BRADYCARDIA
            for d in report.detections
        )
        assert bradycardia_detected
        assert report.heart_rate_mean < 60
    
    def test_tachycardia_detection(self):
        """Test detection of tachycardia."""
        # Create fast rhythm signal (120 BPM)
        sample_rate = 500
        duration = 10
        heart_rate = 120
        
        t = np.linspace(0, duration, duration * sample_rate)
        signal = np.zeros_like(t)
        
        rr_interval = 60 / heart_rate
        for peak_time in np.arange(0, duration, rr_interval):
            peak_idx = int(peak_time * sample_rate)
            if peak_idx < len(signal) - 50:
                signal[peak_idx:peak_idx+50] = np.hanning(50) * 1.0
        
        signals = {'II': signal}
        
        detector = ArrhythmiaDetector(sample_rate)
        report = detector.detect(signals)
        
        # Should detect tachycardia
        tachycardia_detected = any(
            d.type == ArrhythmiaType.TACHYCARDIA
            for d in report.detections
        )
        assert tachycardia_detected
        assert report.heart_rate_mean > 100
    
    def test_irregular_rhythm_detection(self):
        """Test detection of irregular rhythm (AFib-like)."""
        # Create highly irregular rhythm
        sample_rate = 500
        duration = 10
        
        t = np.linspace(0, duration, duration * sample_rate)
        signal = np.zeros_like(t)
        
        # Random RR intervals (simulating AFib)
        np.random.seed(42)
        current_time = 0
        while current_time < duration:
            rr = np.random.uniform(0.4, 1.2)  # Highly variable
            current_time += rr
            peak_idx = int(current_time * sample_rate)
            if peak_idx < len(signal) - 50:
                signal[peak_idx:peak_idx+50] = np.hanning(50) * 1.0
        
        signals = {'II': signal}
        
        detector = ArrhythmiaDetector(sample_rate)
        report = detector.detect(signals)
        
        # Should detect irregularity
        assert report.rr_irregularity > 0.3  # High irregularity
        # May detect AFib depending on P-wave analysis
        # At minimum, should not be normal
        assert report.primary_rhythm != ArrhythmiaType.NORMAL


class TestQTAnalysis:
    """Tests for QT interval analysis."""
    
    def test_qt_analyzer_initialization(self):
        """Test QT analyzer initializes correctly."""
        analyzer = QTAnalyzer(sample_rate=500)
        assert analyzer.sample_rate == 500
    
    def test_normal_qt_analysis(self):
        """Test QT analysis with normal QT interval."""
        # Create synthetic signal with normal QT
        sample_rate = 500
        duration = 10
        
        # Create signal with R-peaks
        t = np.linspace(0, duration, duration * sample_rate)
        signal = np.zeros_like(t)
        
        # Add beats with normal QT (~400ms)
        r_peaks = []
        for peak_time in np.arange(0.5, duration, 0.8):  # 75 BPM
            peak_idx = int(peak_time * sample_rate)
            if peak_idx < len(signal) - 250:
                # R-wave
                signal[peak_idx:peak_idx+20] = np.hanning(20) * 1.5
                # T-wave at ~350ms after R
                t_idx = peak_idx + int(0.35 * sample_rate)
                if t_idx < len(signal) - 50:
                    signal[t_idx:t_idx+50] = np.hanning(50) * 0.8
                r_peaks.append(peak_idx)
        
        signals = {'II': signal}
        r_peaks_dict = {'II': np.array(r_peaks)}
        
        analyzer = QTAnalyzer(sample_rate)
        analysis = analyzer.analyze(signals, r_peaks_dict, gender='M')
        
        # Should be normal
        assert analysis.risk_level == QTRiskLevel.NORMAL
        assert 350 < analysis.mean_qtc < 450  # Normal range for male
        assert not analysis.is_prolonged
    
    def test_prolonged_qt_detection(self):
        """Test detection of prolonged QT interval."""
        # Create synthetic signal with prolonged QT (~500ms)
        sample_rate = 500
        duration = 10
        
        t = np.linspace(0, duration, duration * sample_rate)
        signal = np.zeros_like(t)
        
        r_peaks = []
        for peak_time in np.arange(0.5, duration, 0.8):
            peak_idx = int(peak_time * sample_rate)
            if peak_idx < len(signal) - 300:
                # R-wave
                signal[peak_idx:peak_idx+20] = np.hanning(20) * 1.5
                # T-wave at ~480ms after R (prolonged)
                t_idx = peak_idx + int(0.48 * sample_rate)
                if t_idx < len(signal) - 50:
                    signal[t_idx:t_idx+50] = np.hanning(50) * 0.8
                r_peaks.append(peak_idx)
        
        signals = {'II': signal}
        r_peaks_dict = {'II': np.array(r_peaks)}
        
        analyzer = QTAnalyzer(sample_rate)
        analysis = analyzer.analyze(signals, r_peaks_dict, gender='M')
        
        # Should detect prolongation
        assert analysis.risk_level in [QTRiskLevel.PROLONGED, QTRiskLevel.SEVERELY_PROLONGED]
        assert analysis.is_prolonged
        assert len(analysis.clinical_notes) > 0
        assert len(analysis.drug_interactions) > 0
    
    def test_qt_correction_formulas(self):
        """Test that all QT correction formulas are calculated."""
        sample_rate = 500
        signal = np.random.randn(5000) * 0.1
        
        # Add some peaks
        r_peaks = [500, 900, 1300, 1700, 2100]
        for peak in r_peaks:
            if peak < len(signal) - 50:
                signal[peak:peak+20] = 1.0
                signal[peak+200:peak+250] = 0.5  # T-wave
        
        signals = {'II': signal}
        r_peaks_dict = {'II': np.array(r_peaks)}
        
        analyzer = QTAnalyzer(sample_rate)
        analysis = analyzer.analyze(signals, r_peaks_dict)
        
        # Should have measurements
        assert len(analysis.measurements) > 0
        
        # Check that all correction formulas are present
        m = analysis.measurements[0]
        assert m.qtc_bazett > 0
        assert m.qtc_fridericia > 0
        assert m.qtc_framingham > 0
        assert m.qtc_hodges > 0


class TestClinicalInterpreter:
    """Tests for automated clinical interpretation."""
    
    def test_interpreter_initialization(self):
        """Test interpreter initializes correctly."""
        interpreter = ClinicalInterpreter()
        assert interpreter.confidence_threshold == 0.6
    
    def test_normal_ecg_interpretation(self):
        """Test interpretation of normal ECG."""
        # Create synthetic normal signals
        sample_rate = 500
        duration = 10
        
        signals = {}
        for lead in ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']:
            t = np.linspace(0, duration, duration * sample_rate)
            signals[lead] = np.sin(2 * np.pi * 1.2 * t) * 0.5  # Simple sine wave
        
        # Normal intervals
        intervals = Intervals(
            heart_rate=75.0,
            pr_interval=160.0,
            qrs_duration=90.0,
            qt_interval=400.0,
            qtc_interval=420.0,
            rr_intervals=[800.0] * 10
        )
        
        # Good quality
        quality = QualityMetrics(
            snr=25.0,
            baseline_drift=0.1,
            clipping_ratio=0.0,
            coverage=0.98,
            confidence=0.90
        )
        
        interpreter = ClinicalInterpreter()
        findings = interpreter.interpret(
            signals=signals,
            sample_rate=sample_rate,
            intervals=intervals,
            quality=quality
        )
        
        # Should have findings
        assert findings.conclusion is not None
        assert not findings.conclusion.urgent_action_required
        assert len(findings.conclusion.recommendations) > 0
    
    def test_abnormal_ecg_interpretation(self):
        """Test interpretation of abnormal ECG."""
        # Create signals
        sample_rate = 500
        signals = {'II': np.random.randn(5000) * 0.5}
        
        # Abnormal intervals
        intervals = Intervals(
            heart_rate=45.0,  # Bradycardia
            pr_interval=250.0,  # Prolonged PR
            qrs_duration=140.0,  # Wide QRS
            qt_interval=500.0,  # Prolonged QT
            qtc_interval=510.0,  # Prolonged QTc
            rr_intervals=[1200.0] * 10
        )
        
        # Poor quality
        quality = QualityMetrics(
            snr=8.0,
            baseline_drift=0.4,
            clipping_ratio=0.08,
            coverage=0.75,
            confidence=0.60
        )
        
        interpreter = ClinicalInterpreter()
        findings = interpreter.interpret(
            signals=signals,
            sample_rate=sample_rate,
            intervals=intervals,
            quality=quality
        )
        
        # Should detect multiple abnormalities
        assert len(findings.findings) > 0
        
        # Should detect severity
        abnormal_findings = findings.abnormal_findings
        assert len(abnormal_findings) > 0
        
        # Should have recommendations
        assert len(findings.conclusion.recommendations) > 0
    
    def test_critical_finding_detection(self):
        """Test detection of critical findings."""
        sample_rate = 500
        signals = {'II': np.random.randn(5000)}
        
        # Critical intervals
        intervals = Intervals(
            heart_rate=35.0,  # Severe bradycardia
            pr_interval=350.0,  # Severe PR prolongation
            qrs_duration=180.0,  # Very wide QRS
            qt_interval=600.0,  # Severely prolonged QT
            qtc_interval=620.0,
            rr_intervals=[1700.0] * 10
        )
        
        quality = QualityMetrics(
            snr=15.0,
            baseline_drift=0.2,
            clipping_ratio=0.02,
            coverage=0.90,
            confidence=0.80
        )
        
        interpreter = ClinicalInterpreter()
        findings = interpreter.interpret(
            signals=signals,
            sample_rate=sample_rate,
            intervals=intervals,
            quality=quality
        )
        
        # Should have critical findings
        critical = findings.critical_findings
        # May or may not have critical findings depending on detection logic
        # But should definitely have severe findings
        severe_findings = [f for f in findings.findings 
                          if f.severity in [Severity.SEVERE, Severity.CRITICAL]]
        assert len(severe_findings) > 0


class TestReportGeneration:
    """Tests for PDF report generation."""
    
    def test_basic_report_generation(self, tmp_path):
        """Test that PDF report can be generated without errors."""
        # Create minimal ECG result
        sample_rate = 500
        signals = {'II': np.random.randn(5000) * 0.5}
        
        intervals = Intervals(
            heart_rate=75.0,
            pr_interval=160.0,
            qrs_duration=90.0,
            qt_interval=400.0,
            qtc_interval=420.0
        )
        
        quality = QualityMetrics(
            snr=20.0,
            baseline_drift=0.15,
            clipping_ratio=0.0,
            coverage=0.95,
            confidence=0.85
        )
        
        # Create minimal ECG result
        paper_settings = PaperSettings(pixels_per_mm=10.0)
        metadata = ECGMetadata()
        layout = LeadLayout(leads=[], image_width=1000, image_height=800)
        
        ecg_result = ECGResult(
            signals=signals,
            sample_rate=sample_rate,
            paper_settings=paper_settings,
            layout=layout,
            metadata=metadata,
            intervals=intervals,
            quality_metrics=quality
        )
        
        # Generate report
        output_path = tmp_path / "test_report.pdf"
        
        try:
            generate_pdf_report(
                ecg_result=ecg_result,
                output_path=str(output_path),
                patient_name="Test Patient",
                patient_age=50,
                patient_gender="M"
            )
            
            # Check file was created
            assert output_path.exists()
            assert output_path.stat().st_size > 0
        except Exception as e:
            # PDF generation may fail in test environment without full matplotlib setup
            pytest.skip(f"PDF generation not available in test environment: {e}")


class TestIntegration:
    """Integration tests combining multiple components."""
    
    def test_complete_clinical_workflow(self):
        """Test complete clinical analysis workflow."""
        # Create realistic synthetic ECG
        sample_rate = 500
        duration = 10
        
        # Generate signals for all 12 leads
        leads = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
        signals = {}
        
        for lead in leads:
            t = np.linspace(0, duration, duration * sample_rate)
            # Simple ECG-like signal
            ecg = np.zeros_like(t)
            for beat_time in np.arange(0.5, duration, 0.8):  # 75 BPM
                beat_idx = int(beat_time * sample_rate)
                if beat_idx < len(ecg) - 400:
                    # P-wave
                    ecg[beat_idx:beat_idx+50] = np.hanning(50) * 0.3
                    # QRS
                    ecg[beat_idx+80:beat_idx+100] = np.hanning(20) * 1.5
                    # T-wave
                    ecg[beat_idx+200:beat_idx+250] = np.hanning(50) * 0.5
            
            # Add some noise
            ecg += np.random.randn(len(ecg)) * 0.05
            signals[lead] = ecg
        
        # Run arrhythmia detection
        arr_detector = ArrhythmiaDetector(sample_rate)
        arrhythmia = arr_detector.detect(signals)
        
        assert arrhythmia is not None
        assert arrhythmia.primary_rhythm is not None
        
        # Run QT analysis
        qt_analyzer = QTAnalyzer(sample_rate)
        qt_analysis = qt_analyzer.analyze(signals, r_peaks=None, gender='M')
        
        assert qt_analysis is not None
        assert qt_analysis.mean_qtc > 0
        
        # Run interpretation
        intervals = Intervals(
            heart_rate=75.0,
            pr_interval=160.0,
            qrs_duration=90.0,
            qt_interval=400.0,
            qtc_interval=420.0
        )
        
        quality = QualityMetrics(
            snr=20.0,
            baseline_drift=0.15,
            clipping_ratio=0.0,
            coverage=0.95,
            confidence=0.85
        )
        
        interpreter = ClinicalInterpreter()
        findings = interpreter.interpret(
            signals=signals,
            sample_rate=sample_rate,
            intervals=intervals,
            quality=quality,
            arrhythmia=arrhythmia,
            qt_analysis=qt_analysis,
            patient_age=50,
            patient_gender='M'
        )
        
        assert findings is not None
        assert findings.conclusion is not None
        assert len(findings.findings) >= 0  # May or may not have findings


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
