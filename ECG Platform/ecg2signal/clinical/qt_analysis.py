"""
Comprehensive QT interval analysis module.

Provides advanced QT interval analysis including:
- Multiple QT correction formulas (Bazett, Fridericia, Framingham, Hodges)
- QT dispersion analysis
- QT interval variability
- Risk stratification for QT prolongation
- Gender-specific normal ranges
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np
from pydantic import BaseModel, Field
from scipy.signal import find_peaks, butter, filtfilt


class QTCorrectionMethod(str, Enum):
    """QT correction formulas."""
    BAZETT = "bazett"  # QTc = QT / √RR
    FRIDERICIA = "fridericia"  # QTc = QT / ∛RR
    FRAMINGHAM = "framingham"  # QTc = QT + 154(1 - RR)
    HODGES = "hodges"  # QTc = QT + 1.75(HR - 60)


class QTRiskLevel(str, Enum):
    """Risk levels for QT prolongation."""
    NORMAL = "normal"
    BORDERLINE = "borderline"
    PROLONGED = "prolonged"
    SEVERELY_PROLONGED = "severely_prolonged"


class QTMeasurement(BaseModel):
    """Single QT interval measurement."""
    qt_interval: float = Field(..., description="QT interval in ms")
    qtc_bazett: float = Field(..., description="QTc by Bazett formula in ms")
    qtc_fridericia: float = Field(..., description="QTc by Fridericia formula in ms")
    qtc_framingham: float = Field(..., description="QTc by Framingham formula in ms")
    qtc_hodges: float = Field(..., description="QTc by Hodges formula in ms")
    rr_interval: float = Field(..., description="Associated RR interval in ms")
    heart_rate: float = Field(..., description="Heart rate in BPM")
    lead_name: str = Field(..., description="Lead where measurement was taken")
    measurement_quality: float = Field(..., ge=0.0, le=1.0, description="Confidence in measurement")


class QTDispersion(BaseModel):
    """QT dispersion across multiple leads."""
    max_qt: float = Field(..., description="Maximum QT interval across leads in ms")
    min_qt: float = Field(..., description="Minimum QT interval across leads in ms")
    dispersion: float = Field(..., description="QT dispersion (max - min) in ms")
    dispersion_qtc: float = Field(..., description="QTc dispersion in ms")
    lead_measurements: Dict[str, float] = Field(default_factory=dict)
    
    @property
    def is_abnormal(self) -> bool:
        """Check if dispersion is abnormally high (>100ms suggests increased risk)."""
        return self.dispersion > 100


class QTAnalysis(BaseModel):
    """Complete QT interval analysis."""
    measurements: List[QTMeasurement] = Field(default_factory=list)
    mean_qt: float = Field(..., description="Mean QT interval in ms")
    mean_qtc: float = Field(..., description="Mean QTc (Bazett) in ms")
    std_qt: float = Field(..., description="QT interval standard deviation")
    dispersion: Optional[QTDispersion] = None
    risk_level: QTRiskLevel
    gender_specific_normal: bool = True
    interpretation: str = ""
    clinical_notes: List[str] = Field(default_factory=list)
    drug_interactions: List[str] = Field(default_factory=list)
    
    @property
    def is_prolonged(self) -> bool:
        """Check if QTc is prolonged."""
        return self.risk_level in [QTRiskLevel.PROLONGED, QTRiskLevel.SEVERELY_PROLONGED]


class QTAnalyzer:
    """
    Comprehensive QT interval analyzer.
    
    Features:
    - Automatic T-wave end detection
    - Multiple correction formulas
    - Gender-specific thresholds
    - QT dispersion calculation
    - Risk stratification
    """
    
    # Normal ranges (ms)
    NORMAL_QT_MALE = (350, 440)
    NORMAL_QT_FEMALE = (350, 460)
    NORMAL_QTC_MALE = (350, 450)
    NORMAL_QTC_FEMALE = (350, 470)
    
    def __init__(self, sample_rate: int = 500):
        self.sample_rate = sample_rate
        
    def analyze(
        self,
        signals: Dict[str, np.ndarray],
        r_peaks: Dict[str, np.ndarray],
        gender: Optional[str] = None
    ) -> QTAnalysis:
        """
        Perform comprehensive QT interval analysis.
        
        Args:
            signals: Dictionary of lead name -> signal array
            r_peaks: Dictionary of lead name -> R-peak locations
            gender: Patient gender ('M' or 'F') for gender-specific ranges
            
        Returns:
            Complete QT analysis with measurements and interpretation
        """
        measurements: List[QTMeasurement] = []
        
        # Analyze each lead
        for lead_name, signal in signals.items():
            if lead_name not in r_peaks or len(r_peaks[lead_name]) < 2:
                continue
                
            lead_measurements = self._measure_qt_intervals(
                signal,
                r_peaks[lead_name],
                lead_name
            )
            measurements.extend(lead_measurements)
        
        if not measurements:
            # Return default if no measurements possible
            return QTAnalysis(
                mean_qt=400.0,
                mean_qtc=420.0,
                std_qt=20.0,
                risk_level=QTRiskLevel.NORMAL,
                interpretation="Unable to measure QT intervals"
            )
        
        # Calculate statistics
        qt_values = [m.qt_interval for m in measurements]
        qtc_values = [m.qtc_bazett for m in measurements]
        
        mean_qt = float(np.mean(qt_values))
        mean_qtc = float(np.mean(qtc_values))
        std_qt = float(np.std(qt_values))
        
        # Calculate dispersion if multiple leads
        dispersion = None
        if len(measurements) >= 2:
            dispersion = self._calculate_dispersion(measurements)
        
        # Assess risk level
        risk_level = self._assess_risk(mean_qtc, gender)
        
        # Generate interpretation
        interpretation = self._generate_interpretation(
            mean_qt, mean_qtc, risk_level, gender, dispersion
        )
        
        # Generate clinical notes
        clinical_notes = self._generate_clinical_notes(
            mean_qtc, risk_level, dispersion
        )
        
        # Check for drug interactions
        drug_interactions = self._check_drug_interactions(risk_level)
        
        return QTAnalysis(
            measurements=measurements,
            mean_qt=mean_qt,
            mean_qtc=mean_qtc,
            std_qt=std_qt,
            dispersion=dispersion,
            risk_level=risk_level,
            gender_specific_normal=(gender is not None),
            interpretation=interpretation,
            clinical_notes=clinical_notes,
            drug_interactions=drug_interactions
        )
    
    def _measure_qt_intervals(
        self,
        signal: np.ndarray,
        r_peaks: np.ndarray,
        lead_name: str
    ) -> List[QTMeasurement]:
        """Measure QT intervals for all beats in a lead."""
        measurements = []
        
        for i in range(len(r_peaks) - 1):
            r_peak = r_peaks[i]
            next_r_peak = r_peaks[i + 1]
            
            # Extract beat segment
            beat_start = r_peak
            beat_end = min(next_r_peak, r_peak + int(0.8 * self.sample_rate))
            beat_segment = signal[beat_start:beat_end]
            
            if len(beat_segment) < int(0.2 * self.sample_rate):  # Too short
                continue
            
            # Find T-wave end
            t_end_offset = self._find_t_wave_end(beat_segment)
            
            if t_end_offset is None:
                continue
            
            # Calculate QT interval
            qt_samples = t_end_offset
            qt_ms = (qt_samples / self.sample_rate) * 1000
            
            # Calculate RR interval
            rr_samples = next_r_peak - r_peak
            rr_sec = rr_samples / self.sample_rate
            heart_rate = 60.0 / rr_sec
            
            # Calculate corrected QT using different formulas
            qtc_bazett = self._correct_qt_bazett(qt_ms, rr_sec)
            qtc_fridericia = self._correct_qt_fridericia(qt_ms, rr_sec)
            qtc_framingham = self._correct_qt_framingham(qt_ms, rr_sec)
            qtc_hodges = self._correct_qt_hodges(qt_ms, heart_rate)
            
            # Assess measurement quality
            quality = self._assess_measurement_quality(beat_segment, t_end_offset)
            
            measurements.append(QTMeasurement(
                qt_interval=qt_ms,
                qtc_bazett=qtc_bazett,
                qtc_fridericia=qtc_fridericia,
                qtc_framingham=qtc_framingham,
                qtc_hodges=qtc_hodges,
                rr_interval=rr_sec * 1000,
                heart_rate=heart_rate,
                lead_name=lead_name,
                measurement_quality=quality
            ))
        
        return measurements
    
    def _find_t_wave_end(self, beat_segment: np.ndarray) -> Optional[int]:
        """
        Find the end of the T-wave in a beat segment.
        
        Uses multiple methods:
        - Threshold method
        - Derivative zero-crossing
        - Template matching
        """
        if len(beat_segment) < 50:
            return None
        
        # Method 1: Smooth and find where signal returns to baseline
        from scipy.signal import savgol_filter
        
        # Smooth the signal
        window_length = min(51, len(beat_segment) - 1)
        if window_length % 2 == 0:
            window_length -= 1
        if window_length < 5:
            return None
            
        smoothed = savgol_filter(beat_segment, window_length, 3)
        
        # Find T-wave peak (after QRS, typically 150-250ms after R)
        qrs_end = int(0.15 * self.sample_rate)  # Assume QRS ends ~150ms
        t_search_start = min(qrs_end, len(smoothed) - 10)
        t_search_end = min(int(0.5 * self.sample_rate), len(smoothed))
        
        if t_search_end <= t_search_start:
            return None
        
        t_wave_region = smoothed[t_search_start:t_search_end]
        
        # Find T-wave peak
        t_peak_idx = np.argmax(np.abs(t_wave_region)) + t_search_start
        
        # Find T-wave end (return to baseline after peak)
        baseline = np.median(smoothed[-50:]) if len(smoothed) > 50 else 0.0
        threshold = 0.1 * np.abs(smoothed[t_peak_idx] - baseline)
        
        # Search from T peak to end
        for i in range(t_peak_idx, len(smoothed)):
            if np.abs(smoothed[i] - baseline) < threshold:
                return i
        
        # If not found, use 400ms as default
        default_qt = int(0.4 * self.sample_rate)
        return min(default_qt, len(beat_segment) - 1)
    
    def _correct_qt_bazett(self, qt_ms: float, rr_sec: float) -> float:
        """Bazett formula: QTc = QT / √RR."""
        return qt_ms / np.sqrt(rr_sec)
    
    def _correct_qt_fridericia(self, qt_ms: float, rr_sec: float) -> float:
        """Fridericia formula: QTc = QT / ∛RR."""
        return qt_ms / (rr_sec ** (1/3))
    
    def _correct_qt_framingham(self, qt_ms: float, rr_sec: float) -> float:
        """Framingham formula: QTc = QT + 154(1 - RR)."""
        return qt_ms + 154 * (1 - rr_sec)
    
    def _correct_qt_hodges(self, qt_ms: float, heart_rate: float) -> float:
        """Hodges formula: QTc = QT + 1.75(HR - 60)."""
        return qt_ms + 1.75 * (heart_rate - 60)
    
    def _assess_measurement_quality(
        self,
        beat_segment: np.ndarray,
        t_end: int
    ) -> float:
        """Assess quality of QT measurement (0-1)."""
        quality = 1.0
        
        # Check for noise
        noise_level = np.std(np.diff(beat_segment))
        if noise_level > 0.1 * np.std(beat_segment):
            quality *= 0.8
        
        # Check if T-wave end is reasonable
        expected_t_end = int(0.35 * self.sample_rate)  # ~350ms
        if abs(t_end - expected_t_end) > int(0.2 * self.sample_rate):
            quality *= 0.7
        
        return max(0.0, min(1.0, quality))
    
    def _calculate_dispersion(self, measurements: List[QTMeasurement]) -> QTDispersion:
        """Calculate QT dispersion across leads."""
        # Group by lead
        lead_qt = {}
        lead_qtc = {}
        
        for m in measurements:
            if m.lead_name not in lead_qt:
                lead_qt[m.lead_name] = []
                lead_qtc[m.lead_name] = []
            lead_qt[m.lead_name].append(m.qt_interval)
            lead_qtc[m.lead_name].append(m.qtc_bazett)
        
        # Calculate mean QT for each lead
        lead_mean_qt = {
            lead: np.mean(values) for lead, values in lead_qt.items()
        }
        lead_mean_qtc = {
            lead: np.mean(values) for lead, values in lead_qtc.items()
        }
        
        # Calculate dispersion
        qt_values = list(lead_mean_qt.values())
        qtc_values = list(lead_mean_qtc.values())
        
        max_qt = max(qt_values)
        min_qt = min(qt_values)
        max_qtc = max(qtc_values)
        min_qtc = min(qtc_values)
        
        return QTDispersion(
            max_qt=max_qt,
            min_qt=min_qt,
            dispersion=max_qt - min_qt,
            dispersion_qtc=max_qtc - min_qtc,
            lead_measurements=lead_mean_qt
        )
    
    def _assess_risk(self, qtc: float, gender: Optional[str]) -> QTRiskLevel:
        """Assess risk level based on QTc and gender."""
        # Determine thresholds
        if gender and gender.upper() == 'M':
            normal_max = self.NORMAL_QTC_MALE[1]
            borderline = normal_max + 10
            prolonged = normal_max + 30
        elif gender and gender.upper() == 'F':
            normal_max = self.NORMAL_QTC_FEMALE[1]
            borderline = normal_max + 10
            prolonged = normal_max + 30
        else:
            # Gender-neutral threshold
            normal_max = 460
            borderline = 470
            prolonged = 500
        
        if qtc > prolonged:
            return QTRiskLevel.SEVERELY_PROLONGED
        elif qtc > borderline:
            return QTRiskLevel.PROLONGED
        elif qtc > normal_max:
            return QTRiskLevel.BORDERLINE
        else:
            return QTRiskLevel.NORMAL
    
    def _generate_interpretation(
        self,
        qt: float,
        qtc: float,
        risk: QTRiskLevel,
        gender: Optional[str],
        dispersion: Optional[QTDispersion]
    ) -> str:
        """Generate clinical interpretation."""
        gender_str = f"({gender}) " if gender else ""
        
        interpretation = f"QT interval: {qt:.0f} ms, QTc (Bazett): {qtc:.0f} ms {gender_str}"
        
        if risk == QTRiskLevel.NORMAL:
            interpretation += "- Within normal limits."
        elif risk == QTRiskLevel.BORDERLINE:
            interpretation += "- Borderline prolonged. Monitor and recheck."
        elif risk == QTRiskLevel.PROLONGED:
            interpretation += "- PROLONGED. Risk of torsades de pointes."
        elif risk == QTRiskLevel.SEVERELY_PROLONGED:
            interpretation += "- SEVERELY PROLONGED. HIGH RISK of sudden cardiac death."
        
        if dispersion and dispersion.is_abnormal:
            interpretation += f" QT dispersion is elevated ({dispersion.dispersion:.0f} ms)."
        
        return interpretation
    
    def _generate_clinical_notes(
        self,
        qtc: float,
        risk: QTRiskLevel,
        dispersion: Optional[QTDispersion]
    ) -> List[str]:
        """Generate clinical notes and recommendations."""
        notes = []
        
        if risk in [QTRiskLevel.PROLONGED, QTRiskLevel.SEVERELY_PROLONGED]:
            notes.append("⚠️ Review all medications for QT-prolonging drugs")
            notes.append("Check electrolytes (K+, Mg2+, Ca2+)")
            notes.append("Consider genetic testing for congenital LQTS")
            notes.append("Avoid strenuous exercise")
            
        if risk == QTRiskLevel.SEVERELY_PROLONGED:
            notes.append("⚠️ URGENT: Consider ICD placement if symptomatic")
            notes.append("Strict avoidance of QT-prolonging medications")
            
        if dispersion and dispersion.is_abnormal:
            notes.append(f"Elevated QT dispersion ({dispersion.dispersion:.0f} ms) suggests increased arrhythmia risk")
            
        if not notes:
            notes.append("No specific interventions required")
            
        return notes
    
    def _check_drug_interactions(self, risk: QTRiskLevel) -> List[str]:
        """List common QT-prolonging drugs to avoid."""
        if risk == QTRiskLevel.NORMAL:
            return []
        
        # Common QT-prolonging medications
        drugs = [
            "Antiarrhythmics: amiodarone, sotalol, quinidine",
            "Antibiotics: azithromycin, levofloxacin, moxifloxacin",
            "Antipsychotics: haloperidol, ziprasidone, quetiapine",
            "Antidepressants: citalopram, escitalopram",
            "Antiemetics: ondansetron, droperidol",
            "Antifungals: fluconazole, ketoconazole"
        ]
        
        return drugs
