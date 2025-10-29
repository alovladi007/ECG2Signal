"""
WFDB (MIT/PhysioNet) format I/O for ECG signals.
"""

from pathlib import Path

import numpy as np
import wfdb
from loguru import logger


def write_wfdb(ecg_result, output_dir: str, record_name: str = "ecg") -> None:
    """
    Write ECG signals to WFDB format.

    Args:
        ecg_result: ECGResult object
        output_dir: Output directory path
        record_name: Record name

    The function creates two files:
    - {record_name}.dat: Binary signal data
    - {record_name}.hea: Header with metadata
    """
    from ecg2signal.types import ECGResult

    if not isinstance(ecg_result, ECGResult):
        raise TypeError("ecg_result must be ECGResult instance")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Prepare signals
    signal_names = sorted(ecg_result.signals.keys())
    p_signal = np.column_stack([ecg_result.signals[name] for name in signal_names])

    # Convert to physical units (millivolts)
    # WFDB expects integer ADC units, so we scale to preserve precision
    adc_gain = 1000  # 1000 ADC units per mV
    d_signal = (p_signal * adc_gain).astype(np.int16)

    # Prepare metadata
    sig_name = signal_names
    units = ["mV"] * len(signal_names)
    fmt = ["16"] * len(signal_names)
    adc_gain_list = [adc_gain] * len(signal_names)
    baseline = [0] * len(signal_names)

    # Comments with additional metadata
    comments = [
        f"Paper speed: {ecg_result.paper_settings.paper_speed} mm/s",
        f"Gain: {ecg_result.paper_settings.gain} mm/mV",
        f"Quality score: {ecg_result.quality_metrics.overall_score:.3f}",
        f"SNR: {ecg_result.quality_metrics.snr:.1f} dB",
    ]

    if ecg_result.intervals.heart_rate:
        comments.append(f"Heart rate: {ecg_result.intervals.heart_rate:.1f} BPM")

    # Write WFDB record
    try:
        wfdb.wrsamp(
            record_name=record_name,
            fs=ecg_result.sample_rate,
            units=units,
            sig_name=sig_name,
            p_signal=p_signal,
            d_signal=d_signal,
            fmt=fmt,
            adc_gain=adc_gain_list,
            baseline=baseline,
            comments=comments,
            write_dir=str(output_path),
        )

        logger.info(f"Wrote WFDB record: {output_path / record_name}")

    except Exception as e:
        logger.error(f"Failed to write WFDB record: {e}")
        raise


def read_wfdb(record_path: str) -> tuple[np.ndarray, dict]:
    """
    Read WFDB record.

    Args:
        record_path: Path to WFDB record (without extension)

    Returns:
        Tuple of (signals array, metadata dict)
    """
    try:
        record = wfdb.rdrecord(record_path)

        signals = record.p_signal
        metadata = {
            "sig_name": record.sig_name,
            "fs": record.fs,
            "units": record.units,
            "sig_len": record.sig_len,
            "n_sig": record.n_sig,
            "comments": record.comments,
        }

        logger.info(f"Read WFDB record: {record_path}")
        return signals, metadata

    except Exception as e:
        logger.error(f"Failed to read WFDB record: {e}")
        raise


def validate_wfdb_record(record_path: str) -> bool:
    """
    Validate WFDB record integrity.

    Args:
        record_path: Path to WFDB record (without extension)

    Returns:
        True if valid, False otherwise
    """
    try:
        record = wfdb.rdrecord(record_path)
        return record.sig_len > 0 and record.n_sig > 0
    except Exception:
        return False
