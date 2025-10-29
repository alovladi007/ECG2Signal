"""
EDF+ (European Data Format) I/O for ECG signals.
"""

from datetime import datetime
from pathlib import Path

import numpy as np
import pyedflib
from loguru import logger


def write_edf(ecg_result, output_path: str) -> None:
    """
    Write ECG signals to EDF+ format.

    Args:
        ecg_result: ECGResult object
        output_path: Output EDF file path
    """
    from ecg2signal.types import ECGResult

    if not isinstance(ecg_result, ECGResult):
        raise TypeError("ecg_result must be ECGResult instance")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Prepare signals
    signal_names = sorted(ecg_result.signals.keys())
    signals = [ecg_result.signals[name] for name in signal_names]

    n_channels = len(signals)

    # Create channel info
    channel_info = []
    for i, name in enumerate(signal_names):
        ch_dict = {
            "label": name,
            "dimension": "mV",
            "sample_rate": ecg_result.sample_rate,
            "physical_max": float(np.max(signals[i])),
            "physical_min": float(np.min(signals[i])),
            "digital_max": 32767,
            "digital_min": -32768,
            "transducer": "ECG electrode",
            "prefilter": "None",
        }
        channel_info.append(ch_dict)

    # Create EDF writer
    try:
        with pyedflib.EdfWriter(str(output_file), n_channels, file_type=pyedflib.FILETYPE_EDFPLUS) as writer:
            # Set header info
            header = {
                "technician": "ECG2Signal",
                "recording_additional": "Converted from ECG image",
                "patientname": ecg_result.metadata.patient_name or "Unknown",
                "patient_additional": "",
                "patientcode": ecg_result.metadata.patient_id or "",
                "equipment": ecg_result.metadata.device_id or "ECG2Signal",
                "admincode": "",
                "gender": _map_gender(ecg_result.metadata.gender),
                "startdate": _parse_date(ecg_result.metadata.acquisition_date),
                "birthdate": "",
            }

            writer.setHeader(header)

            # Set channel info
            for i, ch_info in enumerate(channel_info):
                writer.setSignalHeader(i, ch_info)

            # Write signals
            for i, signal in enumerate(signals):
                writer.writeSamples([signal])

        logger.info(f"Wrote EDF+ file: {output_path}")

    except Exception as e:
        logger.error(f"Failed to write EDF+ file: {e}")
        raise


def read_edf(edf_path: str) -> tuple[np.ndarray, dict]:
    """
    Read EDF file.

    Args:
        edf_path: Path to EDF file

    Returns:
        Tuple of (signals array, metadata dict)
    """
    try:
        with pyedflib.EdfReader(edf_path) as reader:
            n_channels = reader.signals_in_file
            signal_labels = reader.getSignalLabels()
            sample_rates = [reader.getSampleFrequency(i) for i in range(n_channels)]

            # Read all signals
            signals = []
            for i in range(n_channels):
                signal = reader.readSignal(i)
                signals.append(signal)

            signals = np.column_stack(signals)

            metadata = {
                "n_channels": n_channels,
                "signal_labels": signal_labels,
                "sample_rates": sample_rates,
                "patient_name": reader.getPatientName(),
                "patient_code": reader.getPatientCode(),
                "technician": reader.getTechnician(),
                "equipment": reader.getEquipment(),
                "start_datetime": reader.getStartdatetime(),
            }

            logger.info(f"Read EDF file: {edf_path}")
            return signals, metadata

    except Exception as e:
        logger.error(f"Failed to read EDF file: {e}")
        raise


def _map_gender(gender: str | None) -> int:
    """
    Map gender string to EDF code.

    Args:
        gender: Gender string ('M', 'F', 'Male', 'Female', etc.)

    Returns:
        Gender code (0=Unknown, 1=Male, 2=Female)
    """
    if not gender:
        return 0

    gender_lower = gender.lower()
    if gender_lower in ["m", "male"]:
        return 1
    elif gender_lower in ["f", "female"]:
        return 2
    return 0


def _parse_date(date_str: str | None) -> datetime:
    """
    Parse date string to datetime.

    Args:
        date_str: Date string in various formats

    Returns:
        datetime object, or current datetime if parsing fails
    """
    if not date_str:
        return datetime.now()

    # Try common formats
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    # If all fail, return current datetime
    logger.warning(f"Could not parse date '{date_str}', using current datetime")
    return datetime.now()


def validate_edf(edf_path: str) -> bool:
    """
    Validate EDF file integrity.

    Args:
        edf_path: Path to EDF file

    Returns:
        True if valid, False otherwise
    """
    try:
        with pyedflib.EdfReader(edf_path) as reader:
            return reader.signals_in_file > 0
    except Exception:
        return False
