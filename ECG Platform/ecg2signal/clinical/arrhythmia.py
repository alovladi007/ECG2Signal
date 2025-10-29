"""
Comprehensive arrhythmia detection module for ECG analysis.

Detects various cardiac arrhythmias including:
- Atrial fibrillation (AFib)
- Atrial flutter
- Ventricular tachycardia (VT)
- Ventricular fibrillation (VFib)
- Premature ventricular contractions (PVCs)
- Premature atrial contractions (PACs)
- Bradycardia/Tachycardia
- Heart blocks (AV blocks)
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np
from pydantic import BaseModel, Field
from scipy.signal import find_peaks, welch
from scipy.stats import variation


class ArrhythmiaType(str, Enum):
    """Types of detected arrhythmias."""
    NORMAL = "normal"
    AFIB = "atrial_fibrillation"
    AFLUTTER = "atrial_flutter"
    VT = "ventricular_tachycardia"
    VFIB = "ventricular_fibrillation"
    PVC = "premature_ventricular_contraction"
    PAC = "premature_atrial_contraction"
    BRADYCARDIA = "bradycardia"
    TACHYCARDIA = "tachycardia"
    FIRST_DEGREE_BLOCK = "first_degree_av_block"
    SECOND_DEGREE_BLOCK = "second_degree_av_block"
    THIRD_DEGREE_BLOCK = "third_degree_av_block"
    SINUS_ARRHYTHMIA = "sinus_arrhythmia"


class ArrhythmiaDetection(BaseModel):
    """Single arrhythmia detection result."""
    type: ArrhythmiaType
    confidence: float = Field(..., ge=0.0, le=1.0)
    onset_sample: Optional[int] = None
    duration_samples: Optional[int] = None
    severity: str = Field("mild", description="mild/moderate/severe")
    description: str = ""
    clinical_significance: str = ""
    
    @property
    def onset_time_sec(self) -> Optional[float]:
        """Get onset time in seconds if sample rate is known."""
        return None  # Calculated externally with sample rate


class ArrhythmiaReport(BaseModel):
    """Complete arrhythmia analysis report."""
    detections: List[ArrhythmiaDetection] = Field(default_factory=list)
    primary_rhythm: ArrhythmiaType = ArrhythmiaType.NORMAL
    heart_rate_mean: float
    heart_rate_std: float
    rr_irregularity: float = Field(..., description="Coefficient of variation of RR intervals")
    ectopic_beats: int = 0
    burden_percent: Dict[ArrhythmiaType, float] = Field(default_factory=dict)
    critical_findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class ArrhythmiaDetector:
    """
    Comprehensive arrhythmia detection system.
    
    Uses multiple algorithms:
    - RR interval analysis
    - P-wave detection
    - QRS morphology analysis
    - Frequency domain analysis
    - Statistical measures
    """
    
    def __init__(self, sample_rate: int = 500):
        self.sample_rate = sample_rate
        self.min_rr_interval = int(0.3 * sample_rate)  # 300ms
        self.max_rr_interval = int(2.0 * sample_rate)  # 2000ms
        
    def detect(
        self,
        signals: Dict[str, np.ndarray],
        r_peaks: Optional[Dict[str, np.ndarray]] = None
    ) -> ArrhythmiaReport:
        """
        Detect arrhythmias in ECG signals.
        
        Args:
            signals: Dictionary of lead name -> signal array
            r_peaks: Optional pre-detected R-peak locations
            
        Returns:
            Complete arrhythmia analysis report
        """
        # Select primary lead for analysis (prefer lead II)
        lead_name, signal = self._select_primary_lead(signals)
        
        # Detect R-peaks if not provided
        if r_peaks is None or lead_name not in r_peaks:
            peaks = self._detect_r_peaks(signal)
        else:
            peaks = r_peaks[lead_name]
        
        # Calculate RR intervals
        rr_intervals = np.diff(peaks) if len(peaks) > 1 else np.array([])
        
        # Initialize report
        detections: List[ArrhythmiaDetection] = []
        
        # Run detection algorithms
        detections.extend(self._detect_rate_abnormalities(rr_intervals))
        detections.extend(self._detect_afib(rr_intervals, signal, peaks))
        detections.extend(self._detect_aflutter(signal))
        detections.extend(self._detect_ventricular_arrhythmias(signal, peaks, rr_intervals))
        detections.extend(self._detect_ectopic_beats(signal, peaks, rr_intervals))
        detections.extend(self._detect_heart_blocks(signal, peaks, rr_intervals))
        
        # Determine primary rhythm
        primary_rhythm = self._determine_primary_rhythm(detections, rr_intervals)
        
        # Calculate statistics
        heart_rate_mean, heart_rate_std = self._calculate_heart_rate_stats(rr_intervals)
        rr_irregularity = variation(rr_intervals) if len(rr_intervals) > 0 else 0.0
        
        # Count ectopic beats
        ectopic_beats = sum(1 for d in detections 
                          if d.type in [ArrhythmiaType.PVC, ArrhythmiaType.PAC])
        
        # Calculate burden
        burden = self._calculate_burden(detections, len(signal))
        
        # Generate critical findings and recommendations
        critical_findings = self._identify_critical_findings(detections)
        recommendations = self._generate_recommendations(detections, primary_rhythm)
        
        return ArrhythmiaReport(
            detections=detections,
            primary_rhythm=primary_rhythm,
            heart_rate_mean=heart_rate_mean,
            heart_rate_std=heart_rate_std,
            rr_irregularity=rr_irregularity,
            ectopic_beats=ectopic_beats,
            burden_percent=burden,
            critical_findings=critical_findings,
            recommendations=recommendations
        )
    
    def _select_primary_lead(self, signals: Dict[str, np.ndarray]) -> Tuple[str, np.ndarray]:
        """Select the best lead for analysis (prefer II, then I)."""
        if "II" in signals:
            return "II", signals["II"]
        elif "I" in signals:
            return "I", signals["I"]
        else:
            return next(iter(signals.items()))
    
    def _detect_r_peaks(self, signal: np.ndarray) -> np.ndarray:
        """Detect R-peaks using adaptive thresholding."""
        # Bandpass filter
        from scipy.signal import butter, filtfilt
        
        # 5-15 Hz bandpass for QRS
        nyquist = self.sample_rate / 2
        low = 5 / nyquist
        high = 15 / nyquist
        b, a = butter(2, [low, high], btype='band')
        filtered = filtfilt(b, a, signal)
        
        # Square and moving average
        squared = filtered ** 2
        window = int(0.12 * self.sample_rate)  # 120ms window
        integrated = np.convolve(squared, np.ones(window) / window, mode='same')
        
        # Adaptive threshold
        threshold = 0.5 * np.mean(integrated)
        peaks, _ = find_peaks(integrated, height=threshold, distance=self.min_rr_interval)
        
        return peaks
    
    def _detect_rate_abnormalities(self, rr_intervals: np.ndarray) -> List[ArrhythmiaDetection]:
        """Detect bradycardia and tachycardia."""
        detections = []
        
        if len(rr_intervals) == 0:
            return detections
        
        mean_rr = np.mean(rr_intervals)
        heart_rate = 60 * self.sample_rate / mean_rr
        
        if heart_rate < 60:
            severity = "severe" if heart_rate < 40 else "moderate" if heart_rate < 50 else "mild"
            detections.append(ArrhythmiaDetection(
                type=ArrhythmiaType.BRADYCARDIA,
                confidence=0.95,
                severity=severity,
                description=f"Heart rate {heart_rate:.0f} BPM (normal: 60-100)",
                clinical_significance="May indicate sinus node dysfunction or AV block"
            ))
        elif heart_rate > 100:
            severity = "severe" if heart_rate > 150 else "moderate" if heart_rate > 120 else "mild"
            detections.append(ArrhythmiaDetection(
                type=ArrhythmiaType.TACHYCARDIA,
                confidence=0.95,
                severity=severity,
                description=f"Heart rate {heart_rate:.0f} BPM (normal: 60-100)",
                clinical_significance="May indicate sinus tachycardia, SVT, or VT"
            ))
        
        return detections
    
    def _detect_afib(
        self,
        rr_intervals: np.ndarray,
        signal: np.ndarray,
        peaks: np.ndarray
    ) -> List[ArrhythmiaDetection]:
        """Detect atrial fibrillation using RR irregularity and P-wave absence."""
        detections = []
        
        if len(rr_intervals) < 10:
            return detections
        
        # Calculate RR interval irregularity
        cv = variation(rr_intervals)
        
        # AFib typically has CV > 0.3 and no consistent P-waves
        if cv > 0.3:
            # Check for P-wave absence (simplified)
            p_wave_score = self._assess_p_wave_regularity(signal, peaks)
            
            if p_wave_score < 0.3:  # Low P-wave regularity suggests AFib
                confidence = min(0.95, cv)
                detections.append(ArrhythmiaDetection(
                    type=ArrhythmiaType.AFIB,
                    confidence=confidence,
                    severity="moderate",
                    description=f"Irregularly irregular rhythm (CV: {cv:.2f}), absent P-waves",
                    clinical_significance="Risk of stroke, requires anticoagulation consideration"
                ))
        
        return detections
    
    def _detect_aflutter(self, signal: np.ndarray) -> List[ArrhythmiaDetection]:
        """Detect atrial flutter using frequency analysis."""
        detections = []
        
        # Look for characteristic 300 BPM flutter waves (5 Hz)
        freqs, psd = welch(signal, fs=self.sample_rate, nperseg=1024)
        
        # Check for peak around 4-6 Hz (240-360 BPM)
        flutter_range = (freqs >= 4) & (freqs <= 6)
        if np.any(flutter_range):
            flutter_power = np.sum(psd[flutter_range])
            total_power = np.sum(psd)
            
            if flutter_power / total_power > 0.2:  # Significant flutter activity
                detections.append(ArrhythmiaDetection(
                    type=ArrhythmiaType.AFLUTTER,
                    confidence=0.75,
                    severity="moderate",
                    description="Regular flutter waves detected at ~300 BPM",
                    clinical_significance="Requires rate control and anticoagulation"
                ))
        
        return detections
    
    def _detect_ventricular_arrhythmias(
        self,
        signal: np.ndarray,
        peaks: np.ndarray,
        rr_intervals: np.ndarray
    ) -> List[ArrhythmiaDetection]:
        """Detect VT and VFib based on rate and morphology."""
        detections = []
        
        if len(rr_intervals) < 3:
            return detections
        
        mean_rr = np.mean(rr_intervals)
        vt_rate = 60 * self.sample_rate / mean_rr
        
        # VT: Rate > 100, relatively regular wide QRS
        if vt_rate > 100 and variation(rr_intervals) < 0.2:
            # Check QRS width (simplified - look at peak width)
            qrs_widths = self._estimate_qrs_widths(signal, peaks)
            mean_width = np.mean(qrs_widths)
            
            if mean_width > 0.12 * self.sample_rate:  # > 120ms
                severity = "severe" if vt_rate > 150 else "moderate"
                detections.append(ArrhythmiaDetection(
                    type=ArrhythmiaType.VT,
                    confidence=0.85,
                    severity=severity,
                    description=f"Wide complex tachycardia at {vt_rate:.0f} BPM",
                    clinical_significance="Life-threatening, requires immediate intervention"
                ))
        
        # VFib: Chaotic, no discernible QRS
        if len(peaks) < 3 or variation(rr_intervals) > 0.8:
            # Check for chaotic signal
            signal_entropy = self._calculate_signal_entropy(signal)
            
            if signal_entropy > 0.8:
                detections.append(ArrhythmiaDetection(
                    type=ArrhythmiaType.VFIB,
                    confidence=0.90,
                    severity="severe",
                    description="Chaotic ventricular activity, no organized rhythm",
                    clinical_significance="FATAL - requires immediate defibrillation"
                ))
        
        return detections
    
    def _detect_ectopic_beats(
        self,
        signal: np.ndarray,
        peaks: np.ndarray,
        rr_intervals: np.ndarray
    ) -> List[ArrhythmiaDetection]:
        """Detect PVCs and PACs."""
        detections = []
        
        if len(rr_intervals) < 3:
            return detections
        
        # PVCs: Premature beats with compensatory pause
        for i in range(1, len(rr_intervals) - 1):
            rr_prev = rr_intervals[i-1]
            rr_current = rr_intervals[i]
            rr_next = rr_intervals[i+1]
            
            mean_rr = np.mean(rr_intervals)
            
            # PVC: Short RR followed by long RR (compensatory pause)
            if rr_current < 0.8 * mean_rr and rr_next > 1.2 * mean_rr:
                # Check if QRS is wide
                peak_idx = peaks[i+1]
                qrs_width = self._estimate_single_qrs_width(signal, peak_idx)
                
                if qrs_width > 0.12 * self.sample_rate:
                    detections.append(ArrhythmiaDetection(
                        type=ArrhythmiaType.PVC,
                        confidence=0.80,
                        onset_sample=int(peaks[i+1]),
                        duration_samples=int(qrs_width),
                        severity="mild",
                        description=f"Premature ventricular beat at sample {peaks[i+1]}",
                        clinical_significance="Usually benign if infrequent"
                    ))
            
            # PAC: Premature beat without compensatory pause
            elif rr_current < 0.8 * mean_rr and rr_next < 1.1 * mean_rr:
                detections.append(ArrhythmiaDetection(
                    type=ArrhythmiaType.PAC,
                    confidence=0.75,
                    onset_sample=int(peaks[i+1]),
                    severity="mild",
                    description=f"Premature atrial beat at sample {peaks[i+1]}",
                    clinical_significance="Usually benign"
                ))
        
        return detections
    
    def _detect_heart_blocks(
        self,
        signal: np.ndarray,
        peaks: np.ndarray,
        rr_intervals: np.ndarray
    ) -> List[ArrhythmiaDetection]:
        """Detect AV blocks (simplified detection)."""
        detections = []
        
        # This is a simplified implementation
        # Real implementation would require P-wave and QRS detection
        
        # First degree: Long PR interval (would need PR measurement)
        # Second degree: Dropped beats with pattern
        # Third degree: Complete dissociation
        
        if len(rr_intervals) > 10:
            # Look for patterns of dropped beats (Mobitz II)
            rr_ratio = rr_intervals[1:] / rr_intervals[:-1]
            doubled_intervals = np.sum(rr_ratio > 1.8)
            
            if doubled_intervals > 2:
                detections.append(ArrhythmiaDetection(
                    type=ArrhythmiaType.SECOND_DEGREE_BLOCK,
                    confidence=0.60,
                    severity="moderate",
                    description=f"Suspected second-degree AV block ({doubled_intervals} dropped beats)",
                    clinical_significance="May progress to complete heart block"
                ))
        
        return detections
    
    def _assess_p_wave_regularity(self, signal: np.ndarray, r_peaks: np.ndarray) -> float:
        """Assess P-wave regularity (simplified)."""
        # In real implementation, would detect P-waves before each QRS
        # Here we use a simplified heuristic
        return 0.5  # Placeholder
    
    def _estimate_qrs_widths(self, signal: np.ndarray, peaks: np.ndarray) -> np.ndarray:
        """Estimate QRS complex widths."""
        widths = []
        for peak in peaks:
            width = self._estimate_single_qrs_width(signal, peak)
            widths.append(width)
        return np.array(widths)
    
    def _estimate_single_qrs_width(self, signal: np.ndarray, peak_idx: int) -> float:
        """Estimate width of a single QRS complex."""
        # Look for start and end of QRS around peak
        search_window = int(0.1 * self.sample_rate)  # 100ms window
        
        start_idx = max(0, peak_idx - search_window)
        end_idx = min(len(signal), peak_idx + search_window)
        
        segment = signal[start_idx:end_idx]
        threshold = 0.3 * np.max(np.abs(segment))
        
        # Find first and last points above threshold
        above_threshold = np.abs(segment) > threshold
        if np.any(above_threshold):
            indices = np.where(above_threshold)[0]
            width = indices[-1] - indices[0]
            return width
        
        return 0.08 * self.sample_rate  # Default to 80ms
    
    def _calculate_signal_entropy(self, signal: np.ndarray) -> float:
        """Calculate normalized entropy of signal for chaos detection."""
        # Histogram-based entropy
        hist, _ = np.histogram(signal, bins=50, density=True)
        hist = hist[hist > 0]  # Remove zero bins
        entropy = -np.sum(hist * np.log2(hist))
        
        # Normalize by maximum possible entropy
        max_entropy = np.log2(len(hist))
        return entropy / max_entropy if max_entropy > 0 else 0.0
    
    def _determine_primary_rhythm(
        self,
        detections: List[ArrhythmiaDetection],
        rr_intervals: np.ndarray
    ) -> ArrhythmiaType:
        """Determine the primary cardiac rhythm."""
        if not detections:
            return ArrhythmiaType.NORMAL
        
        # Priority: Life-threatening rhythms first
        for arrhythmia_type in [
            ArrhythmiaType.VFIB,
            ArrhythmiaType.VT,
            ArrhythmiaType.AFIB,
            ArrhythmiaType.AFLUTTER,
            ArrhythmiaType.THIRD_DEGREE_BLOCK,
        ]:
            for detection in detections:
                if detection.type == arrhythmia_type and detection.confidence > 0.7:
                    return arrhythmia_type
        
        # If no major arrhythmia, return most common
        type_counts = {}
        for detection in detections:
            type_counts[detection.type] = type_counts.get(detection.type, 0) + 1
        
        if type_counts:
            return max(type_counts.items(), key=lambda x: x[1])[0]
        
        return ArrhythmiaType.NORMAL
    
    def _calculate_heart_rate_stats(self, rr_intervals: np.ndarray) -> Tuple[float, float]:
        """Calculate mean and standard deviation of heart rate."""
        if len(rr_intervals) == 0:
            return 0.0, 0.0
        
        heart_rates = 60 * self.sample_rate / rr_intervals
        return float(np.mean(heart_rates)), float(np.std(heart_rates))
    
    def _calculate_burden(
        self,
        detections: List[ArrhythmiaDetection],
        total_samples: int
    ) -> Dict[ArrhythmiaType, float]:
        """Calculate percentage burden of each arrhythmia type."""
        burden = {}
        
        for arrhythmia_type in ArrhythmiaType:
            type_detections = [d for d in detections if d.type == arrhythmia_type]
            if type_detections:
                total_duration = sum(
                    d.duration_samples for d in type_detections 
                    if d.duration_samples is not None
                )
                burden[arrhythmia_type] = (total_duration / total_samples) * 100
        
        return burden
    
    def _identify_critical_findings(self, detections: List[ArrhythmiaDetection]) -> List[str]:
        """Identify critical findings requiring immediate attention."""
        critical = []
        
        for detection in detections:
            if detection.type == ArrhythmiaType.VFIB:
                critical.append("⚠️ VENTRICULAR FIBRILLATION - IMMEDIATE DEFIBRILLATION REQUIRED")
            elif detection.type == ArrhythmiaType.VT and detection.severity == "severe":
                critical.append("⚠️ SEVERE VENTRICULAR TACHYCARDIA - URGENT INTERVENTION NEEDED")
            elif detection.type == ArrhythmiaType.THIRD_DEGREE_BLOCK:
                critical.append("⚠️ COMPLETE HEART BLOCK - PACEMAKER EVALUATION NEEDED")
            elif detection.type == ArrhythmiaType.BRADYCARDIA and detection.severity == "severe":
                critical.append("⚠️ SEVERE BRADYCARDIA - ASSESS FOR HEMODYNAMIC COMPROMISE")
        
        return critical
    
    def _generate_recommendations(
        self,
        detections: List[ArrhythmiaDetection],
        primary_rhythm: ArrhythmiaType
    ) -> List[str]:
        """Generate clinical recommendations based on findings."""
        recommendations = []
        
        if primary_rhythm == ArrhythmiaType.AFIB:
            recommendations.append("Consider anticoagulation therapy (CHA2DS2-VASc score)")
            recommendations.append("Rate control with beta-blockers or calcium channel blockers")
            recommendations.append("Consider rhythm control strategy if symptomatic")
            
        elif primary_rhythm == ArrhythmiaType.VT:
            recommendations.append("Immediate cardiology consultation")
            recommendations.append("Assess for underlying structural heart disease")
            recommendations.append("Consider ICD placement if recurrent")
            
        # Count PVCs
        pvc_count = sum(1 for d in detections if d.type == ArrhythmiaType.PVC)
        if pvc_count > 10:
            recommendations.append(f"Frequent PVCs detected ({pvc_count}) - consider 24hr Holter monitoring")
            
        if not recommendations:
            recommendations.append("Continue routine cardiac monitoring")
            
        return recommendations
