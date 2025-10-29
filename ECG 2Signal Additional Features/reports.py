"""
Comprehensive clinical report generation for ECG analysis.

Generates professional PDF reports with:
- Patient demographics
- ECG measurements
- Automated findings
- Visual waveforms
- Clinical interpretations
- Recommendations
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec

from ecg2signal.clinical.arrhythmia import ArrhythmiaReport
from ecg2signal.clinical.findings import AutomatedFindings
from ecg2signal.clinical.qt_analysis import QTAnalysis
from ecg2signal.types import ECGResult


def generate_pdf_report(
    ecg_result: ECGResult,
    output_path: str,
    arrhythmia_report: Optional[ArrhythmiaReport] = None,
    qt_analysis: Optional[QTAnalysis] = None,
    automated_findings: Optional[AutomatedFindings] = None,
    patient_name: Optional[str] = None,
    patient_age: Optional[int] = None,
    patient_gender: Optional[str] = None,
    institution: str = "ECG2Signal Analysis System"
) -> None:
    """
    Generate comprehensive PDF clinical report.
    
    Args:
        ecg_result: ECG conversion result with signals and measurements
        output_path: Path for output PDF file
        arrhythmia_report: Optional arrhythmia analysis
        qt_analysis: Optional QT interval analysis
        automated_findings: Optional automated clinical findings
        patient_name: Optional patient name
        patient_age: Optional patient age in years
        patient_gender: Optional patient gender ('M' or 'F')
        institution: Institution name for report header
    """
    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Create PDF
    with PdfPages(output_path) as pdf:
        # Page 1: Demographics and Summary
        _create_summary_page(
            pdf, ecg_result, arrhythmia_report, qt_analysis, automated_findings,
            patient_name, patient_age, patient_gender, institution
        )
        
        # Page 2: Waveform Display
        _create_waveform_page(pdf, ecg_result)
        
        # Page 3: Measurements and Intervals
        _create_measurements_page(pdf, ecg_result, qt_analysis)
        
        # Page 4: Automated Findings (if available)
        if automated_findings:
            _create_findings_page(pdf, automated_findings)
        
        # Page 5: Arrhythmia Analysis (if available)
        if arrhythmia_report:
            _create_arrhythmia_page(pdf, arrhythmia_report)
        
        # Page 6: QT Analysis Details (if available and prolonged)
        if qt_analysis and qt_analysis.is_prolonged:
            _create_qt_analysis_page(pdf, qt_analysis)


def _create_summary_page(
    pdf: PdfPages,
    ecg_result: ECGResult,
    arrhythmia_report: Optional[ArrhythmiaReport],
    qt_analysis: Optional[QTAnalysis],
    automated_findings: Optional[AutomatedFindings],
    patient_name: Optional[str],
    patient_age: Optional[int],
    patient_gender: Optional[str],
    institution: str
) -> None:
    """Create summary page with demographics and key findings."""
    fig = plt.figure(figsize=(8.5, 11))
    gs = GridSpec(20, 1, figure=fig, hspace=0.5)
    
    # Header
    ax_header = fig.add_subplot(gs[0:2, 0])
    ax_header.axis('off')
    ax_header.text(0.5, 0.7, institution, ha='center', va='center', 
                   fontsize=16, fontweight='bold')
    ax_header.text(0.5, 0.3, "ECG ANALYSIS REPORT", ha='center', va='center',
                   fontsize=14, fontweight='bold')
    
    # Patient Demographics
    ax_demo = fig.add_subplot(gs[2:5, 0])
    ax_demo.axis('off')
    
    demo_text = "PATIENT INFORMATION\n" + "="*50 + "\n"
    demo_text += f"Name: {patient_name or 'Not provided'}\n"
    demo_text += f"Age: {patient_age or 'Not provided'} years\n"
    demo_text += f"Gender: {patient_gender or 'Not provided'}\n"
    demo_text += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    ax_demo.text(0.05, 0.95, demo_text, ha='left', va='top',
                 fontsize=10, family='monospace',
                 transform=ax_demo.transAxes)
    
    # Key Measurements
    ax_measure = fig.add_subplot(gs[5:10, 0])
    ax_measure.axis('off')
    
    measure_text = "\nKEY MEASUREMENTS\n" + "="*50 + "\n"
    measure_text += f"Heart Rate: {ecg_result.intervals.heart_rate or 'N/A':.0f} BPM\n"
    measure_text += f"PR Interval: {ecg_result.intervals.pr_interval or 'N/A':.0f} ms\n"
    measure_text += f"QRS Duration: {ecg_result.intervals.qrs_duration or 'N/A':.0f} ms\n"
    measure_text += f"QT Interval: {ecg_result.intervals.qt_interval or 'N/A':.0f} ms\n"
    measure_text += f"QTc Interval: {ecg_result.intervals.qtc_interval or 'N/A':.0f} ms\n"
    
    if automated_findings and automated_findings.axis:
        measure_text += f"QRS Axis: {automated_findings.axis}\n"
    
    ax_measure.text(0.05, 0.95, measure_text, ha='left', va='top',
                    fontsize=10, family='monospace',
                    transform=ax_measure.transAxes)
    
    # Primary Findings
    ax_findings = fig.add_subplot(gs[10:16, 0])
    ax_findings.axis('off')
    
    findings_text = "\nINTERPRETATION\n" + "="*50 + "\n"
    
    if automated_findings:
        findings_text += f"{automated_findings.conclusion.primary_diagnosis}\n\n"
        
        if automated_findings.conclusion.urgent_action_required:
            findings_text += "⚠️  URGENT ACTION REQUIRED\n\n"
        
        # Critical findings
        if automated_findings.critical_findings:
            findings_text += "CRITICAL FINDINGS:\n"
            for finding in automated_findings.critical_findings:
                findings_text += f"  • {finding.name}: {finding.description}\n"
            findings_text += "\n"
        
        # Additional findings
        if automated_findings.conclusion.additional_findings:
            findings_text += "ADDITIONAL FINDINGS:\n"
            for finding in automated_findings.conclusion.additional_findings[:3]:
                findings_text += f"  • {finding}\n"
    else:
        if arrhythmia_report:
            findings_text += f"Rhythm: {arrhythmia_report.primary_rhythm.value}\n"
            findings_text += f"Mean HR: {arrhythmia_report.heart_rate_mean:.0f} BPM\n"
        else:
            findings_text += "Rhythm: Regular sinus rhythm\n"
    
    ax_findings.text(0.05, 0.95, findings_text, ha='left', va='top',
                     fontsize=9, family='monospace',
                     transform=ax_findings.transAxes)
    
    # Recommendations
    ax_recs = fig.add_subplot(gs[16:20, 0])
    ax_recs.axis('off')
    
    recs_text = "\nRECOMMENDATIONS\n" + "="*50 + "\n"
    
    if automated_findings and automated_findings.conclusion.recommendations:
        for i, rec in enumerate(automated_findings.conclusion.recommendations[:4], 1):
            recs_text += f"{i}. {rec}\n"
    else:
        recs_text += "1. Continue routine cardiac monitoring\n"
        recs_text += "2. Repeat ECG if symptoms develop\n"
    
    ax_recs.text(0.05, 0.95, recs_text, ha='left', va='top',
                 fontsize=9, family='monospace',
                 transform=ax_recs.transAxes)
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def _create_waveform_page(pdf: PdfPages, ecg_result: ECGResult) -> None:
    """Create page with ECG waveform display."""
    fig = plt.figure(figsize=(11, 8.5))  # Landscape
    
    # Standard 12-lead layout (3 columns x 4 rows + rhythm strip)
    leads_order = ['I', 'aVR', 'V1', 'V4',
                   'II', 'aVL', 'V2', 'V5',
                   'III', 'aVF', 'V3', 'V6']
    
    # Create subplots for each lead
    for idx, lead_name in enumerate(leads_order):
        if lead_name not in ecg_result.signals:
            continue
        
        row = idx // 4
        col = idx % 4
        ax = plt.subplot(4, 4, idx + 1)
        
        signal = ecg_result.signals[lead_name]
        time = np.arange(len(signal)) / ecg_result.sample_rate
        
        # Plot 2.5 seconds of signal
        samples_to_plot = min(int(2.5 * ecg_result.sample_rate), len(signal))
        
        ax.plot(time[:samples_to_plot], signal[:samples_to_plot], 'k-', linewidth=0.8)
        ax.set_title(lead_name, fontweight='bold')
        ax.set_xlim(0, 2.5)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Time (s)', fontsize=8)
        ax.set_ylabel('mV', fontsize=8)
        ax.tick_params(labelsize=7)
    
    plt.suptitle('12-Lead ECG', fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def _create_measurements_page(
    pdf: PdfPages,
    ecg_result: ECGResult,
    qt_analysis: Optional[QTAnalysis]
) -> None:
    """Create page with detailed measurements."""
    fig = plt.figure(figsize=(8.5, 11))
    gs = GridSpec(15, 2, figure=fig, hspace=0.8, wspace=0.4)
    
    # Title
    ax_title = fig.add_subplot(gs[0, :])
    ax_title.axis('off')
    ax_title.text(0.5, 0.5, 'DETAILED MEASUREMENTS', ha='center', va='center',
                  fontsize=14, fontweight='bold')
    
    # Intervals table
    ax_intervals = fig.add_subplot(gs[1:5, 0])
    ax_intervals.axis('off')
    
    intervals_data = []
    intervals_data.append(['Measurement', 'Value', 'Normal Range'])
    intervals_data.append(['Heart Rate', 
                          f"{ecg_result.intervals.heart_rate or 0:.0f} BPM",
                          '60-100 BPM'])
    intervals_data.append(['PR Interval', 
                          f"{ecg_result.intervals.pr_interval or 0:.0f} ms",
                          '120-200 ms'])
    intervals_data.append(['QRS Duration', 
                          f"{ecg_result.intervals.qrs_duration or 0:.0f} ms",
                          '<120 ms'])
    intervals_data.append(['QT Interval', 
                          f"{ecg_result.intervals.qt_interval or 0:.0f} ms",
                          '350-450 ms'])
    intervals_data.append(['QTc Interval', 
                          f"{ecg_result.intervals.qtc_interval or 0:.0f} ms",
                          '<450 ms'])
    
    table = ax_intervals.table(cellText=intervals_data, loc='center',
                               cellLoc='left', colWidths=[0.4, 0.3, 0.3])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # Style header row
    for i in range(3):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Quality metrics
    ax_quality = fig.add_subplot(gs[1:5, 1])
    ax_quality.axis('off')
    
    quality_data = []
    quality_data.append(['Quality Metric', 'Value', 'Status'])
    quality_data.append(['SNR', 
                        f"{ecg_result.quality_metrics.snr:.1f} dB",
                        'Good' if ecg_result.quality_metrics.snr > 20 else 'Poor'])
    quality_data.append(['Baseline Drift', 
                        f"{ecg_result.quality_metrics.baseline_drift:.2f}",
                        'Good' if ecg_result.quality_metrics.baseline_drift < 0.3 else 'Poor'])
    quality_data.append(['Clipping', 
                        f"{ecg_result.quality_metrics.clipping_ratio:.1%}",
                        'Good' if ecg_result.quality_metrics.clipping_ratio < 0.05 else 'Poor'])
    quality_data.append(['Overall Quality', 
                        f"{ecg_result.quality_metrics.overall_score:.0%}",
                        'Good' if ecg_result.quality_metrics.overall_score > 0.7 else 'Poor'])
    
    qtable = ax_quality.table(cellText=quality_data, loc='center',
                              cellLoc='left', colWidths=[0.4, 0.3, 0.3])
    qtable.auto_set_font_size(False)
    qtable.set_fontsize(9)
    qtable.scale(1, 2)
    
    # Style header row
    for i in range(3):
        qtable[(0, i)].set_facecolor('#2196F3')
        qtable[(0, i)].set_text_props(weight='bold', color='white')
    
    # QT Analysis details (if available)
    if qt_analysis and qt_analysis.measurements:
        ax_qt = fig.add_subplot(gs[6:10, :])
        ax_qt.axis('off')
        ax_qt.text(0.5, 0.9, 'QT INTERVAL ANALYSIS', ha='center', va='top',
                   fontsize=12, fontweight='bold', transform=ax_qt.transAxes)
        
        qt_text = f"\nQTc Correction Methods:\n"
        qt_text += f"  Bazett:      {qt_analysis.mean_qtc:.0f} ms\n"
        
        # Get first measurement for all correction methods
        if qt_analysis.measurements:
            m = qt_analysis.measurements[0]
            qt_text += f"  Fridericia:  {m.qtc_fridericia:.0f} ms\n"
            qt_text += f"  Framingham:  {m.qtc_framingham:.0f} ms\n"
            qt_text += f"  Hodges:      {m.qtc_hodges:.0f} ms\n"
        
        qt_text += f"\nRisk Level: {qt_analysis.risk_level.value.upper()}\n"
        
        if qt_analysis.dispersion:
            qt_text += f"\nQT Dispersion: {qt_analysis.dispersion.dispersion:.0f} ms\n"
            qt_text += f"Status: {'ABNORMAL' if qt_analysis.dispersion.is_abnormal else 'Normal'}\n"
        
        ax_qt.text(0.05, 0.75, qt_text, ha='left', va='top',
                   fontsize=9, family='monospace',
                   transform=ax_qt.transAxes)
    
    # RR interval histogram
    if ecg_result.intervals.rr_intervals:
        ax_rr = fig.add_subplot(gs[11:15, :])
        rr_intervals = ecg_result.intervals.rr_intervals
        
        ax_rr.hist(rr_intervals, bins=20, edgecolor='black', alpha=0.7)
        ax_rr.axvline(np.mean(rr_intervals), color='red', linestyle='--',
                     label=f'Mean: {np.mean(rr_intervals):.0f} ms')
        ax_rr.set_xlabel('RR Interval (ms)')
        ax_rr.set_ylabel('Frequency')
        ax_rr.set_title('RR Interval Distribution')
        ax_rr.legend()
        ax_rr.grid(True, alpha=0.3)
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def _create_findings_page(pdf: PdfPages, findings: AutomatedFindings) -> None:
    """Create page with automated clinical findings."""
    fig = plt.figure(figsize=(8.5, 11))
    fig.suptitle('AUTOMATED CLINICAL FINDINGS', fontsize=14, fontweight='bold')
    
    ax = fig.add_subplot(111)
    ax.axis('off')
    
    y_pos = 0.95
    line_height = 0.04
    
    # Conclusion
    ax.text(0.05, y_pos, 'PRIMARY DIAGNOSIS:', ha='left', va='top',
            fontsize=11, fontweight='bold', transform=ax.transAxes)
    y_pos -= line_height
    
    ax.text(0.05, y_pos, findings.conclusion.primary_diagnosis, ha='left', va='top',
            fontsize=10, transform=ax.transAxes)
    y_pos -= line_height * 2
    
    # Critical findings
    if findings.critical_findings:
        ax.text(0.05, y_pos, 'CRITICAL FINDINGS:', ha='left', va='top',
                fontsize=11, fontweight='bold', color='red',
                transform=ax.transAxes)
        y_pos -= line_height
        
        for finding in findings.critical_findings:
            text = f"• {finding.name}\n  {finding.description}\n  {finding.clinical_significance}"
            ax.text(0.08, y_pos, text, ha='left', va='top',
                    fontsize=9, color='red', transform=ax.transAxes)
            y_pos -= line_height * 3
    
    # All findings grouped by severity
    y_pos -= line_height
    ax.text(0.05, y_pos, 'ALL FINDINGS:', ha='left', va='top',
            fontsize=11, fontweight='bold', transform=ax.transAxes)
    y_pos -= line_height
    
    for finding in findings.findings:
        if y_pos < 0.1:  # Stop if running out of space
            break
        
        severity_color = {
            'critical': 'red',
            'severe': 'orange',
            'moderate': 'gold',
            'mild': 'green',
            'benign': 'blue',
            'normal': 'green'
        }.get(finding.severity.value, 'black')
        
        text = f"• [{finding.severity.value.upper()}] {finding.name}"
        ax.text(0.08, y_pos, text, ha='left', va='top',
                fontsize=9, color=severity_color, fontweight='bold',
                transform=ax.transAxes)
        y_pos -= line_height
        
        ax.text(0.10, y_pos, f"{finding.description}", ha='left', va='top',
                fontsize=8, transform=ax.transAxes)
        y_pos -= line_height
        
        if finding.clinical_significance:
            ax.text(0.10, y_pos, f"Significance: {finding.clinical_significance}",
                    ha='left', va='top', fontsize=8, fontstyle='italic',
                    transform=ax.transAxes)
            y_pos -= line_height
        
        y_pos -= line_height * 0.5
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def _create_arrhythmia_page(pdf: PdfPages, arrhythmia: ArrhythmiaReport) -> None:
    """Create page with arrhythmia analysis details."""
    fig = plt.figure(figsize=(8.5, 11))
    fig.suptitle('ARRHYTHMIA ANALYSIS', fontsize=14, fontweight='bold')
    
    ax = fig.add_subplot(111)
    ax.axis('off')
    
    y_pos = 0.95
    line_height = 0.04
    
    # Primary rhythm
    ax.text(0.05, y_pos, f'Primary Rhythm: {arrhythmia.primary_rhythm.value.replace("_", " ").title()}',
            ha='left', va='top', fontsize=11, fontweight='bold',
            transform=ax.transAxes)
    y_pos -= line_height * 2
    
    # Statistics
    stats_text = f"Heart Rate: {arrhythmia.heart_rate_mean:.0f} ± {arrhythmia.heart_rate_std:.0f} BPM\n"
    stats_text += f"RR Irregularity: {arrhythmia.rr_irregularity:.2f}\n"
    stats_text += f"Ectopic Beats: {arrhythmia.ectopic_beats}\n"
    
    ax.text(0.05, y_pos, stats_text, ha='left', va='top',
            fontsize=10, family='monospace', transform=ax.transAxes)
    y_pos -= line_height * 4
    
    # Critical findings
    if arrhythmia.critical_findings:
        ax.text(0.05, y_pos, 'CRITICAL FINDINGS:', ha='left', va='top',
                fontsize=11, fontweight='bold', color='red',
                transform=ax.transAxes)
        y_pos -= line_height
        
        for finding in arrhythmia.critical_findings:
            ax.text(0.08, y_pos, f"• {finding}", ha='left', va='top',
                    fontsize=9, color='red', transform=ax.transAxes)
            y_pos -= line_height
    
    # Detections
    y_pos -= line_height
    ax.text(0.05, y_pos, 'DETECTIONS:', ha='left', va='top',
            fontsize=11, fontweight='bold', transform=ax.transAxes)
    y_pos -= line_height
    
    for detection in arrhythmia.detections[:10]:  # Show first 10
        if y_pos < 0.2:
            break
        
        text = f"• {detection.type.value.replace('_', ' ').title()}"
        text += f" (confidence: {detection.confidence:.0%})"
        
        ax.text(0.08, y_pos, text, ha='left', va='top',
                fontsize=9, transform=ax.transAxes)
        y_pos -= line_height
        
        if detection.description:
            ax.text(0.10, y_pos, detection.description, ha='left', va='top',
                    fontsize=8, fontstyle='italic', transform=ax.transAxes)
            y_pos -= line_height
        
        y_pos -= line_height * 0.5
    
    # Recommendations
    y_pos -= line_height
    ax.text(0.05, y_pos, 'RECOMMENDATIONS:', ha='left', va='top',
            fontsize=11, fontweight='bold', transform=ax.transAxes)
    y_pos -= line_height
    
    for i, rec in enumerate(arrhythmia.recommendations, 1):
        if y_pos < 0.05:
            break
        ax.text(0.08, y_pos, f"{i}. {rec}", ha='left', va='top',
                fontsize=9, transform=ax.transAxes)
        y_pos -= line_height * 1.5
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def _create_qt_analysis_page(pdf: PdfPages, qt_analysis: QTAnalysis) -> None:
    """Create detailed QT analysis page."""
    fig = plt.figure(figsize=(8.5, 11))
    fig.suptitle('QT INTERVAL ANALYSIS', fontsize=14, fontweight='bold')
    
    ax = fig.add_subplot(111)
    ax.axis('off')
    
    y_pos = 0.95
    line_height = 0.04
    
    # Interpretation
    ax.text(0.05, y_pos, 'INTERPRETATION:', ha='left', va='top',
            fontsize=11, fontweight='bold', transform=ax.transAxes)
    y_pos -= line_height
    
    ax.text(0.05, y_pos, qt_analysis.interpretation, ha='left', va='top',
            fontsize=10, transform=ax.transAxes, wrap=True)
    y_pos -= line_height * 3
    
    # Clinical notes
    ax.text(0.05, y_pos, 'CLINICAL NOTES:', ha='left', va='top',
            fontsize=11, fontweight='bold', transform=ax.transAxes)
    y_pos -= line_height
    
    for note in qt_analysis.clinical_notes:
        ax.text(0.08, y_pos, f"• {note}", ha='left', va='top',
                fontsize=9, transform=ax.transAxes)
        y_pos -= line_height * 1.5
    
    # Drug interactions
    if qt_analysis.drug_interactions:
        y_pos -= line_height
        ax.text(0.05, y_pos, 'QT-PROLONGING DRUGS TO AVOID:', ha='left', va='top',
                fontsize=11, fontweight='bold', color='red',
                transform=ax.transAxes)
        y_pos -= line_height
        
        for drug in qt_analysis.drug_interactions:
            if y_pos < 0.1:
                break
            ax.text(0.08, y_pos, f"• {drug}", ha='left', va='top',
                    fontsize=8, color='red', transform=ax.transAxes)
            y_pos -= line_height
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)
