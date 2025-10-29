"""
Automated clinical findings and interpretation module.

Provides comprehensive automated interpretation of ECG findings including:
- Rhythm analysis
- Axis determination
- Morphology assessment
- Clinical significance
- Differential diagnoses
- Recommendations
"""

from enum import Enum
from typing import Dict, List, Optional, Set

import numpy as np
from pydantic import BaseModel, Field

from ecg2signal.clinical.arrhythmia import ArrhythmiaReport, ArrhythmiaType
from ecg2signal.clinical.qt_analysis import QTAnalysis, QTRiskLevel
from ecg2signal.types import Intervals, QualityMetrics


class Severity(str, Enum):
    """Severity levels for findings."""
    NORMAL = "normal"
    BENIGN = "benign"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class FindingCategory(str, Enum):
    """Categories of ECG findings."""
    RHYTHM = "rhythm"
    CONDUCTION = "conduction"
    ISCHEMIA = "ischemia"
    HYPERTROPHY = "hypertrophy"
    ELECTROLYTE = "electrolyte"
    DRUG_EFFECT = "drug_effect"
    ARTIFACT = "artifact"


class ClinicalFinding(BaseModel):
    """A single clinical finding."""
    category: FindingCategory
    name: str
    description: str
    severity: Severity
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)
    clinical_significance: str = ""
    differential_diagnoses: List[str] = Field(default_factory=list)
    
    @property
    def is_critical(self) -> bool:
        """Check if finding is critical."""
        return self.severity == Severity.CRITICAL


class ClinicalConclusion(BaseModel):
    """Overall clinical conclusion."""
    primary_diagnosis: str
    additional_findings: List[str] = Field(default_factory=list)
    severity: Severity
    urgent_action_required: bool = False
    recommendations: List[str] = Field(default_factory=list)
    follow_up: str = ""
    prognosis: str = ""


class AutomatedFindings(BaseModel):
    """Complete automated findings report."""
    findings: List[ClinicalFinding] = Field(default_factory=list)
    conclusion: ClinicalConclusion
    axis: Optional[str] = None
    rhythm_description: str = ""
    rate_description: str = ""
    interval_description: str = ""
    morphology_notes: List[str] = Field(default_factory=list)
    comparison_with_normal: Dict[str, str] = Field(default_factory=dict)
    
    @property
    def critical_findings(self) -> List[ClinicalFinding]:
        """Get all critical findings."""
        return [f for f in self.findings if f.is_critical]
    
    @property
    def abnormal_findings(self) -> List[ClinicalFinding]:
        """Get all abnormal findings."""
        return [f for f in self.findings 
                if f.severity not in [Severity.NORMAL, Severity.BENIGN]]


class ClinicalInterpreter:
    """
    Automated clinical interpreter for ECG data.
    
    Analyzes ECG data and generates comprehensive clinical findings
    with interpretations, diagnoses, and recommendations.
    """
    
    def __init__(self):
        self.confidence_threshold = 0.6
        
    def interpret(
        self,
        signals: Dict[str, np.ndarray],
        sample_rate: int,
        intervals: Intervals,
        quality: QualityMetrics,
        arrhythmia: Optional[ArrhythmiaReport] = None,
        qt_analysis: Optional[QTAnalysis] = None,
        patient_age: Optional[int] = None,
        patient_gender: Optional[str] = None
    ) -> AutomatedFindings:
        """
        Generate comprehensive automated clinical findings.
        
        Args:
            signals: ECG signals by lead
            sample_rate: Sampling rate in Hz
            intervals: Measured intervals
            quality: Quality metrics
            arrhythmia: Optional arrhythmia analysis
            qt_analysis: Optional QT analysis
            patient_age: Optional patient age
            patient_gender: Optional patient gender
            
        Returns:
            Complete automated findings report
        """
        findings: List[ClinicalFinding] = []
        
        # 1. Assess rhythm
        rhythm_findings = self._assess_rhythm(intervals, arrhythmia)
        findings.extend(rhythm_findings)
        
        # 2. Assess heart rate
        rate_findings = self._assess_heart_rate(intervals, patient_age)
        findings.extend(rate_findings)
        
        # 3. Assess intervals
        interval_findings = self._assess_intervals(intervals, patient_gender)
        findings.extend(interval_findings)
        
        # 4. Assess QT intervals
        if qt_analysis:
            qt_findings = self._assess_qt_intervals(qt_analysis, patient_gender)
            findings.extend(qt_findings)
        
        # 5. Assess axis
        axis, axis_findings = self._assess_axis(signals)
        findings.extend(axis_findings)
        
        # 6. Assess morphology
        morphology_findings = self._assess_morphology(signals, sample_rate)
        findings.extend(morphology_findings)
        
        # 7. Assess for ischemia
        ischemia_findings = self._assess_ischemia(signals, sample_rate)
        findings.extend(ischemia_findings)
        
        # 8. Assess for hypertrophy
        hypertrophy_findings = self._assess_hypertrophy(signals, sample_rate)
        findings.extend(hypertrophy_findings)
        
        # 9. Assess quality issues
        quality_findings = self._assess_quality_issues(quality)
        findings.extend(quality_findings)
        
        # Generate descriptions
        rhythm_desc = self._generate_rhythm_description(intervals, arrhythmia)
        rate_desc = self._generate_rate_description(intervals, patient_age)
        interval_desc = self._generate_interval_description(intervals)
        morphology_notes = self._generate_morphology_notes(signals)
        
        # Generate comparison with normal
        comparison = self._compare_with_normal(intervals, qt_analysis, patient_age, patient_gender)
        
        # Generate overall conclusion
        conclusion = self._generate_conclusion(findings, arrhythmia, qt_analysis)
        
        return AutomatedFindings(
            findings=findings,
            conclusion=conclusion,
            axis=axis,
            rhythm_description=rhythm_desc,
            rate_description=rate_desc,
            interval_description=interval_desc,
            morphology_notes=morphology_notes,
            comparison_with_normal=comparison
        )
    
    def _assess_rhythm(
        self,
        intervals: Intervals,
        arrhythmia: Optional[ArrhythmiaReport]
    ) -> List[ClinicalFinding]:
        """Assess cardiac rhythm."""
        findings = []
        
        if arrhythmia:
            # Use arrhythmia analysis if available
            if arrhythmia.primary_rhythm != ArrhythmiaType.NORMAL:
                severity = self._map_arrhythmia_severity(arrhythmia.primary_rhythm)
                findings.append(ClinicalFinding(
                    category=FindingCategory.RHYTHM,
                    name=arrhythmia.primary_rhythm.value.replace('_', ' ').title(),
                    description=f"Primary rhythm: {arrhythmia.primary_rhythm.value}",
                    severity=severity,
                    confidence=0.85,
                    evidence=[f"RR irregularity: {arrhythmia.rr_irregularity:.2f}"],
                    clinical_significance=self._get_arrhythmia_significance(arrhythmia.primary_rhythm)
                ))
        else:
            # Basic rhythm assessment from intervals
            if intervals.rr_intervals:
                rr_cv = np.std(intervals.rr_intervals) / np.mean(intervals.rr_intervals)
                
                if rr_cv < 0.1:
                    findings.append(ClinicalFinding(
                        category=FindingCategory.RHYTHM,
                        name="Regular Sinus Rhythm",
                        description="Normal sinus rhythm with regular RR intervals",
                        severity=Severity.NORMAL,
                        confidence=0.90,
                        evidence=[f"RR variability: {rr_cv:.1%}"]
                    ))
                elif rr_cv > 0.3:
                    findings.append(ClinicalFinding(
                        category=FindingCategory.RHYTHM,
                        name="Irregular Rhythm",
                        description="Irregularly irregular rhythm detected",
                        severity=Severity.MODERATE,
                        confidence=0.80,
                        evidence=[f"RR variability: {rr_cv:.1%}"],
                        clinical_significance="Consider atrial fibrillation",
                        differential_diagnoses=["Atrial fibrillation", "Atrial flutter with variable block"]
                    ))
        
        return findings
    
    def _assess_heart_rate(
        self,
        intervals: Intervals,
        patient_age: Optional[int]
    ) -> List[ClinicalFinding]:
        """Assess heart rate."""
        findings = []
        
        if intervals.heart_rate is None:
            return findings
        
        hr = intervals.heart_rate
        
        # Adjust normal range by age
        if patient_age:
            if patient_age < 1:
                normal_range = (100, 160)
            elif patient_age < 3:
                normal_range = (90, 150)
            elif patient_age < 10:
                normal_range = (70, 120)
            else:
                normal_range = (60, 100)
        else:
            normal_range = (60, 100)
        
        if hr < normal_range[0]:
            severity = Severity.SEVERE if hr < 40 else Severity.MODERATE if hr < 50 else Severity.MILD
            findings.append(ClinicalFinding(
                category=FindingCategory.RHYTHM,
                name="Bradycardia",
                description=f"Heart rate {hr:.0f} BPM (normal: {normal_range[0]}-{normal_range[1]})",
                severity=severity,
                confidence=0.95,
                evidence=[f"HR: {hr:.0f} BPM"],
                clinical_significance="May indicate sinus node dysfunction, AV block, or vagal tone",
                differential_diagnoses=[
                    "Sinus bradycardia",
                    "Second-degree AV block",
                    "Third-degree AV block",
                    "Medication effect (beta-blockers, calcium channel blockers)"
                ]
            ))
        elif hr > normal_range[1]:
            severity = Severity.SEVERE if hr > 150 else Severity.MODERATE if hr > 120 else Severity.MILD
            findings.append(ClinicalFinding(
                category=FindingCategory.RHYTHM,
                name="Tachycardia",
                description=f"Heart rate {hr:.0f} BPM (normal: {normal_range[0]}-{normal_range[1]})",
                severity=severity,
                confidence=0.95,
                evidence=[f"HR: {hr:.0f} BPM"],
                clinical_significance="May indicate sinus tachycardia, SVT, or VT",
                differential_diagnoses=[
                    "Sinus tachycardia",
                    "Supraventricular tachycardia",
                    "Atrial fibrillation with RVR",
                    "Ventricular tachycardia"
                ]
            ))
        
        return findings
    
    def _assess_intervals(
        self,
        intervals: Intervals,
        patient_gender: Optional[str]
    ) -> List[ClinicalFinding]:
        """Assess PR, QRS, and QT intervals."""
        findings = []
        
        # PR interval
        if intervals.pr_interval:
            if intervals.pr_interval < 120:
                findings.append(ClinicalFinding(
                    category=FindingCategory.CONDUCTION,
                    name="Short PR Interval",
                    description=f"PR interval {intervals.pr_interval:.0f} ms (normal: 120-200)",
                    severity=Severity.MILD,
                    confidence=0.85,
                    evidence=[f"PR: {intervals.pr_interval:.0f} ms"],
                    clinical_significance="May indicate pre-excitation (WPW syndrome)",
                    differential_diagnoses=["WPW syndrome", "Lown-Ganong-Levine syndrome"]
                ))
            elif intervals.pr_interval > 200:
                severity = Severity.MODERATE if intervals.pr_interval < 250 else Severity.SEVERE
                findings.append(ClinicalFinding(
                    category=FindingCategory.CONDUCTION,
                    name="Prolonged PR Interval (First-Degree AV Block)",
                    description=f"PR interval {intervals.pr_interval:.0f} ms (normal: 120-200)",
                    severity=severity,
                    confidence=0.90,
                    evidence=[f"PR: {intervals.pr_interval:.0f} ms"],
                    clinical_significance="First-degree AV block, may progress",
                    differential_diagnoses=["First-degree AV block", "Medication effect", "Ischemia"]
                ))
        
        # QRS duration
        if intervals.qrs_duration:
            if intervals.qrs_duration > 120:
                severity = Severity.MODERATE if intervals.qrs_duration < 140 else Severity.SEVERE
                findings.append(ClinicalFinding(
                    category=FindingCategory.CONDUCTION,
                    name="Wide QRS Complex",
                    description=f"QRS duration {intervals.qrs_duration:.0f} ms (normal: <120)",
                    severity=severity,
                    confidence=0.88,
                    evidence=[f"QRS: {intervals.qrs_duration:.0f} ms"],
                    clinical_significance="Bundle branch block or ventricular origin",
                    differential_diagnoses=[
                        "Right bundle branch block",
                        "Left bundle branch block",
                        "Ventricular rhythm",
                        "Hyperkalemia"
                    ]
                ))
        
        return findings
    
    def _assess_qt_intervals(
        self,
        qt_analysis: QTAnalysis,
        patient_gender: Optional[str]
    ) -> List[ClinicalFinding]:
        """Assess QT/QTc intervals."""
        findings = []
        
        if qt_analysis.risk_level == QTRiskLevel.BORDERLINE:
            findings.append(ClinicalFinding(
                category=FindingCategory.CONDUCTION,
                name="Borderline QT Prolongation",
                description=qt_analysis.interpretation,
                severity=Severity.MILD,
                confidence=0.80,
                evidence=[f"QTc: {qt_analysis.mean_qtc:.0f} ms"],
                clinical_significance="Monitor for progression, check medications",
                differential_diagnoses=qt_analysis.drug_interactions[:3] if qt_analysis.drug_interactions else []
            ))
        elif qt_analysis.risk_level == QTRiskLevel.PROLONGED:
            findings.append(ClinicalFinding(
                category=FindingCategory.CONDUCTION,
                name="Prolonged QT Interval",
                description=qt_analysis.interpretation,
                severity=Severity.SEVERE,
                confidence=0.88,
                evidence=[f"QTc: {qt_analysis.mean_qtc:.0f} ms"],
                clinical_significance="Risk of torsades de pointes and sudden cardiac death",
                differential_diagnoses=[
                    "Congenital long QT syndrome",
                    "Drug-induced QT prolongation",
                    "Electrolyte imbalance",
                    "Myocardial ischemia"
                ]
            ))
        elif qt_analysis.risk_level == QTRiskLevel.SEVERELY_PROLONGED:
            findings.append(ClinicalFinding(
                category=FindingCategory.CONDUCTION,
                name="Severely Prolonged QT Interval",
                description=qt_analysis.interpretation,
                severity=Severity.CRITICAL,
                confidence=0.92,
                evidence=[f"QTc: {qt_analysis.mean_qtc:.0f} ms"],
                clinical_significance="CRITICAL: High risk of sudden cardiac death",
                differential_diagnoses=[
                    "Congenital long QT syndrome (types 1-17)",
                    "Severe electrolyte abnormality",
                    "Drug toxicity"
                ]
            ))
        
        # QT dispersion
        if qt_analysis.dispersion and qt_analysis.dispersion.is_abnormal:
            findings.append(ClinicalFinding(
                category=FindingCategory.CONDUCTION,
                name="Increased QT Dispersion",
                description=f"QT dispersion {qt_analysis.dispersion.dispersion:.0f} ms (normal: <100)",
                severity=Severity.MODERATE,
                confidence=0.75,
                evidence=[f"Dispersion: {qt_analysis.dispersion.dispersion:.0f} ms"],
                clinical_significance="Associated with increased arrhythmia risk"
            ))
        
        return findings
    
    def _assess_axis(
        self,
        signals: Dict[str, np.ndarray]
    ) -> tuple[Optional[str], List[ClinicalFinding]]:
        """Assess QRS axis."""
        findings = []
        
        # Simplified axis calculation using leads I and aVF
        if "I" not in signals or "aVF" not in signals:
            return None, findings
        
        lead_i = signals["I"]
        lead_avf = signals["aVF"]
        
        # Calculate mean QRS amplitude
        i_amplitude = np.mean(lead_i)
        avf_amplitude = np.mean(lead_avf)
        
        # Determine axis
        if i_amplitude > 0 and avf_amplitude > 0:
            axis = "Normal axis (0° to +90°)"
            severity = Severity.NORMAL
        elif i_amplitude > 0 and avf_amplitude < 0:
            axis = "Left axis deviation (-30° to -90°)"
            severity = Severity.MILD
            findings.append(ClinicalFinding(
                category=FindingCategory.CONDUCTION,
                name="Left Axis Deviation",
                description=axis,
                severity=severity,
                confidence=0.75,
                evidence=[f"Lead I: positive, aVF: negative"],
                clinical_significance="May indicate left ventricular hypertrophy or LAFB",
                differential_diagnoses=[
                    "Left anterior fascicular block",
                    "Left ventricular hypertrophy",
                    "Inferior MI"
                ]
            ))
        elif i_amplitude < 0 and avf_amplitude > 0:
            axis = "Right axis deviation (+90° to +180°)"
            severity = Severity.MODERATE
            findings.append(ClinicalFinding(
                category=FindingCategory.CONDUCTION,
                name="Right Axis Deviation",
                description=axis,
                severity=severity,
                confidence=0.75,
                evidence=[f"Lead I: negative, aVF: positive"],
                clinical_significance="May indicate right ventricular hypertrophy or pulmonary disease",
                differential_diagnoses=[
                    "Right ventricular hypertrophy",
                    "Chronic lung disease",
                    "Pulmonary embolism",
                    "Left posterior fascicular block"
                ]
            ))
        else:
            axis = "Extreme axis deviation (northwest axis)"
            severity = Severity.SEVERE
            findings.append(ClinicalFinding(
                category=FindingCategory.CONDUCTION,
                name="Extreme Axis Deviation",
                description=axis,
                severity=severity,
                confidence=0.70,
                evidence=[f"Lead I: negative, aVF: negative"],
                clinical_significance="Unusual axis, consider lead misplacement or complex pathology"
            ))
        
        return axis, findings
    
    def _assess_morphology(
        self,
        signals: Dict[str, np.ndarray],
        sample_rate: int
    ) -> List[ClinicalFinding]:
        """Assess ECG morphology."""
        findings = []
        
        # This would be more sophisticated in production
        # Here we do basic checks
        
        for lead_name, signal in signals.items():
            # Check for poor R-wave progression (in V leads)
            if lead_name in ["V1", "V2", "V3"]:
                r_amplitude = np.max(signal) - np.median(signal)
                if r_amplitude < 0.1:  # Very low amplitude
                    findings.append(ClinicalFinding(
                        category=FindingCategory.MORPHOLOGY,
                        name=f"Poor R-Wave Progression in {lead_name}",
                        description=f"Low R-wave amplitude in {lead_name}",
                        severity=Severity.MILD,
                        confidence=0.65,
                        evidence=[f"{lead_name} amplitude: {r_amplitude:.2f} mV"],
                        clinical_significance="May indicate anterior MI or lead misplacement"
                    ))
        
        return findings
    
    def _assess_ischemia(
        self,
        signals: Dict[str, np.ndarray],
        sample_rate: int
    ) -> List[ClinicalFinding]:
        """Assess for signs of ischemia/infarction."""
        findings = []
        
        # Look for ST segment changes (simplified)
        for lead_name, signal in signals.items():
            # This is highly simplified - real implementation would be much more complex
            baseline = np.median(signal)
            st_segment = signal[int(0.08 * sample_rate):int(0.12 * sample_rate)]
            st_elevation = np.mean(st_segment) - baseline
            
            if st_elevation > 0.2:  # >2mm elevation
                findings.append(ClinicalFinding(
                    category=FindingCategory.ISCHEMIA,
                    name=f"ST Elevation in {lead_name}",
                    description=f"ST segment elevation detected in {lead_name}",
                    severity=Severity.CRITICAL,
                    confidence=0.70,
                    evidence=[f"ST elevation: {st_elevation:.2f} mV"],
                    clinical_significance="STEMI - requires immediate intervention",
                    differential_diagnoses=[
                        "Acute myocardial infarction",
                        "Pericarditis",
                        "Early repolarization"
                    ]
                ))
            elif st_elevation < -0.1:  # >1mm depression
                findings.append(ClinicalFinding(
                    category=FindingCategory.ISCHEMIA,
                    name=f"ST Depression in {lead_name}",
                    description=f"ST segment depression detected in {lead_name}",
                    severity=Severity.SEVERE,
                    confidence=0.70,
                    evidence=[f"ST depression: {st_elevation:.2f} mV"],
                    clinical_significance="Myocardial ischemia or NSTEMI",
                    differential_diagnoses=[
                        "Myocardial ischemia",
                        "NSTEMI",
                        "Digitalis effect"
                    ]
                ))
        
        return findings
    
    def _assess_hypertrophy(
        self,
        signals: Dict[str, np.ndarray],
        sample_rate: int
    ) -> List[ClinicalFinding]:
        """Assess for ventricular hypertrophy."""
        findings = []
        
        # Simplified voltage criteria
        if "V1" in signals and "V5" in signals:
            s_v1 = abs(np.min(signals["V1"]))
            r_v5 = np.max(signals["V5"])
            
            # Sokolow-Lyon criteria: S in V1 + R in V5/V6 > 35 mm
            sokolow_lyon = s_v1 + r_v5
            
            if sokolow_lyon > 3.5:  # 35mm in mV
                findings.append(ClinicalFinding(
                    category=FindingCategory.HYPERTROPHY,
                    name="Left Ventricular Hypertrophy",
                    description=f"Voltage criteria for LVH (Sokolow-Lyon: {sokolow_lyon:.1f} mV)",
                    severity=Severity.MODERATE,
                    confidence=0.75,
                    evidence=[f"S(V1) + R(V5) = {sokolow_lyon:.1f} mV"],
                    clinical_significance="Associated with hypertension and heart failure risk",
                    differential_diagnoses=[
                        "Essential hypertension",
                        "Aortic stenosis",
                        "Athletic heart"
                    ]
                ))
        
        return findings
    
    def _assess_quality_issues(self, quality: QualityMetrics) -> List[ClinicalFinding]:
        """Assess quality-related issues."""
        findings = []
        
        if quality.snr < 10:
            findings.append(ClinicalFinding(
                category=FindingCategory.ARTIFACT,
                name="Poor Signal Quality",
                description=f"Low signal-to-noise ratio ({quality.snr:.1f} dB)",
                severity=Severity.MILD,
                confidence=0.95,
                evidence=[f"SNR: {quality.snr:.1f} dB"],
                clinical_significance="Interpretation may be limited by signal quality"
            ))
        
        if quality.baseline_drift > 0.3:
            findings.append(ClinicalFinding(
                category=FindingCategory.ARTIFACT,
                name="Baseline Wander",
                description="Significant baseline drift detected",
                severity=Severity.MILD,
                confidence=0.90,
                evidence=[f"Drift: {quality.baseline_drift:.2f}"],
                clinical_significance="May affect ST segment interpretation"
            ))
        
        if quality.clipping_ratio > 0.05:
            findings.append(ClinicalFinding(
                category=FindingCategory.ARTIFACT,
                name="Signal Clipping",
                description=f"{quality.clipping_ratio:.1%} of signal clipped",
                severity=Severity.MODERATE,
                confidence=0.95,
                evidence=[f"Clipping: {quality.clipping_ratio:.1%}"],
                clinical_significance="Amplitude measurements may be inaccurate"
            ))
        
        return findings
    
    def _map_arrhythmia_severity(self, arrhythmia_type: ArrhythmiaType) -> Severity:
        """Map arrhythmia type to severity."""
        severity_map = {
            ArrhythmiaType.VFIB: Severity.CRITICAL,
            ArrhythmiaType.VT: Severity.CRITICAL,
            ArrhythmiaType.THIRD_DEGREE_BLOCK: Severity.CRITICAL,
            ArrhythmiaType.AFIB: Severity.SEVERE,
            ArrhythmiaType.AFLUTTER: Severity.SEVERE,
            ArrhythmiaType.SECOND_DEGREE_BLOCK: Severity.MODERATE,
            ArrhythmiaType.FIRST_DEGREE_BLOCK: Severity.MILD,
            ArrhythmiaType.PVC: Severity.MILD,
            ArrhythmiaType.PAC: Severity.BENIGN,
            ArrhythmiaType.BRADYCARDIA: Severity.MODERATE,
            ArrhythmiaType.TACHYCARDIA: Severity.MODERATE,
        }
        return severity_map.get(arrhythmia_type, Severity.MILD)
    
    def _get_arrhythmia_significance(self, arrhythmia_type: ArrhythmiaType) -> str:
        """Get clinical significance of arrhythmia."""
        significance_map = {
            ArrhythmiaType.VFIB: "FATAL - Immediate defibrillation required",
            ArrhythmiaType.VT: "Life-threatening - High risk of sudden cardiac death",
            ArrhythmiaType.AFIB: "Stroke risk - Consider anticoagulation",
            ArrhythmiaType.THIRD_DEGREE_BLOCK: "Complete AV dissociation - Pacemaker needed",
        }
        return significance_map.get(arrhythmia_type, "")
    
    def _generate_rhythm_description(
        self,
        intervals: Intervals,
        arrhythmia: Optional[ArrhythmiaReport]
    ) -> str:
        """Generate rhythm description."""
        if arrhythmia and arrhythmia.primary_rhythm != ArrhythmiaType.NORMAL:
            return f"{arrhythmia.primary_rhythm.value.replace('_', ' ').title()}"
        
        if intervals.rr_intervals:
            rr_cv = np.std(intervals.rr_intervals) / np.mean(intervals.rr_intervals)
            if rr_cv < 0.1:
                return "Regular sinus rhythm"
            else:
                return "Irregularly irregular rhythm"
        
        return "Rhythm assessment limited"
    
    def _generate_rate_description(
        self,
        intervals: Intervals,
        patient_age: Optional[int]
    ) -> str:
        """Generate heart rate description."""
        if intervals.heart_rate is None:
            return "Heart rate could not be determined"
        
        hr = intervals.heart_rate
        
        if patient_age and patient_age < 10:
            return f"Heart rate {hr:.0f} BPM (pediatric)"
        elif hr < 60:
            return f"Bradycardia at {hr:.0f} BPM"
        elif hr > 100:
            return f"Tachycardia at {hr:.0f} BPM"
        else:
            return f"Normal heart rate at {hr:.0f} BPM"
    
    def _generate_interval_description(self, intervals: Intervals) -> str:
        """Generate interval description."""
        parts = []
        
        if intervals.pr_interval:
            if intervals.pr_interval < 120 or intervals.pr_interval > 200:
                parts.append(f"PR {intervals.pr_interval:.0f} ms (abnormal)")
            else:
                parts.append(f"PR {intervals.pr_interval:.0f} ms (normal)")
        
        if intervals.qrs_duration:
            if intervals.qrs_duration > 120:
                parts.append(f"QRS {intervals.qrs_duration:.0f} ms (wide)")
            else:
                parts.append(f"QRS {intervals.qrs_duration:.0f} ms (normal)")
        
        if intervals.qtc_interval:
            if intervals.qtc_interval > 450:
                parts.append(f"QTc {intervals.qtc_interval:.0f} ms (prolonged)")
            else:
                parts.append(f"QTc {intervals.qtc_interval:.0f} ms (normal)")
        
        return ", ".join(parts) if parts else "Intervals within normal limits"
    
    def _generate_morphology_notes(self, signals: Dict[str, np.ndarray]) -> List[str]:
        """Generate morphology notes."""
        notes = []
        
        # Check precordial leads
        v_leads = [k for k in signals.keys() if k.startswith('V')]
        if v_leads:
            notes.append(f"Precordial leads present: {', '.join(v_leads)}")
        
        # Check limb leads
        limb_leads = [k for k in signals.keys() if k in ['I', 'II', 'III', 'aVR', 'aVL', 'aVF']]
        if limb_leads:
            notes.append(f"Limb leads present: {', '.join(limb_leads)}")
        
        return notes
    
    def _compare_with_normal(
        self,
        intervals: Intervals,
        qt_analysis: Optional[QTAnalysis],
        patient_age: Optional[int],
        patient_gender: Optional[str]
    ) -> Dict[str, str]:
        """Compare findings with normal values."""
        comparison = {}
        
        # Heart rate
        if intervals.heart_rate:
            normal_range = "60-100 BPM"
            if patient_age and patient_age < 10:
                normal_range = "70-120 BPM (pediatric)"
            
            if intervals.heart_rate < 60:
                comparison["Heart Rate"] = f"{intervals.heart_rate:.0f} BPM (below normal {normal_range})"
            elif intervals.heart_rate > 100:
                comparison["Heart Rate"] = f"{intervals.heart_rate:.0f} BPM (above normal {normal_range})"
            else:
                comparison["Heart Rate"] = f"{intervals.heart_rate:.0f} BPM (normal)"
        
        # PR interval
        if intervals.pr_interval:
            if intervals.pr_interval < 120:
                comparison["PR Interval"] = f"{intervals.pr_interval:.0f} ms (short, normal: 120-200 ms)"
            elif intervals.pr_interval > 200:
                comparison["PR Interval"] = f"{intervals.pr_interval:.0f} ms (long, normal: 120-200 ms)"
            else:
                comparison["PR Interval"] = f"{intervals.pr_interval:.0f} ms (normal)"
        
        # QRS duration
        if intervals.qrs_duration:
            if intervals.qrs_duration > 120:
                comparison["QRS Duration"] = f"{intervals.qrs_duration:.0f} ms (wide, normal: <120 ms)"
            else:
                comparison["QRS Duration"] = f"{intervals.qrs_duration:.0f} ms (normal)"
        
        # QTc
        if qt_analysis:
            gender_str = f" ({patient_gender})" if patient_gender else ""
            if qt_analysis.is_prolonged:
                comparison["QTc"] = f"{qt_analysis.mean_qtc:.0f} ms (prolonged{gender_str})"
            else:
                comparison["QTc"] = f"{qt_analysis.mean_qtc:.0f} ms (normal{gender_str})"
        
        return comparison
    
    def _generate_conclusion(
        self,
        findings: List[ClinicalFinding],
        arrhythmia: Optional[ArrhythmiaReport],
        qt_analysis: Optional[QTAnalysis]
    ) -> ClinicalConclusion:
        """Generate overall clinical conclusion."""
        # Determine primary diagnosis
        critical_findings = [f for f in findings if f.severity == Severity.CRITICAL]
        severe_findings = [f for f in findings if f.severity == Severity.SEVERE]
        
        if critical_findings:
            primary_diagnosis = critical_findings[0].name
            severity = Severity.CRITICAL
            urgent = True
        elif severe_findings:
            primary_diagnosis = severe_findings[0].name
            severity = Severity.SEVERE
            urgent = True
        elif findings:
            # Find most significant finding
            severity_order = [Severity.CRITICAL, Severity.SEVERE, Severity.MODERATE, Severity.MILD, Severity.BENIGN]
            for sev in severity_order:
                matching = [f for f in findings if f.severity == sev]
                if matching:
                    primary_diagnosis = matching[0].name
                    severity = sev
                    urgent = False
                    break
            else:
                primary_diagnosis = "Normal ECG"
                severity = Severity.NORMAL
                urgent = False
        else:
            primary_diagnosis = "Normal ECG"
            severity = Severity.NORMAL
            urgent = False
        
        # Collect additional findings
        additional = [f.name for f in findings if f.name != primary_diagnosis][:5]
        
        # Generate recommendations
        recommendations = []
        
        if urgent:
            recommendations.append("⚠️ URGENT: Immediate cardiology consultation required")
        
        if arrhythmia and arrhythmia.recommendations:
            recommendations.extend(arrhythmia.recommendations[:3])
        
        if qt_analysis and qt_analysis.clinical_notes:
            recommendations.extend(qt_analysis.clinical_notes[:2])
        
        if not recommendations:
            recommendations.append("Continue routine cardiac monitoring")
            recommendations.append("Repeat ECG in 6-12 months or if symptoms develop")
        
        # Follow-up
        if urgent:
            follow_up = "Immediate follow-up required"
        elif severity in [Severity.SEVERE, Severity.MODERATE]:
            follow_up = "Follow-up within 1-2 weeks"
        else:
            follow_up = "Routine follow-up as scheduled"
        
        # Prognosis
        if severity == Severity.CRITICAL:
            prognosis = "Guarded - requires immediate intervention"
        elif severity == Severity.SEVERE:
            prognosis = "Fair with appropriate treatment"
        else:
            prognosis = "Good with monitoring"
        
        return ClinicalConclusion(
            primary_diagnosis=primary_diagnosis,
            additional_findings=additional,
            severity=severity,
            urgent_action_required=urgent,
            recommendations=recommendations,
            follow_up=follow_up,
            prognosis=prognosis
        )
