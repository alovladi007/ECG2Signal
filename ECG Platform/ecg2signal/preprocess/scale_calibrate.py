"""
Scale calibration for ECG images: converting pixels to physical units (mm, seconds, mV).
"""

import numpy as np
from loguru import logger

from ecg2signal.types import GridInfo, PaperSettings


def calibrate_scale(
    image: np.ndarray,
    grid_info: GridInfo,
    paper_speed: float = 25.0,
    gain: float = 10.0,
) -> PaperSettings:
    """
    Calibrate pixel-to-physical-unit conversion.

    Standard ECG settings:
    - Paper speed: 25 mm/s or 50 mm/s
    - Gain: 10 mm/mV (standard) or 5 mm/mV, 20 mm/mV
    - Grid: Major squares 5mm x 5mm, minor squares 1mm x 1mm

    Args:
        image: Input ECG image
        grid_info: Detected grid information
        paper_speed: Paper speed in mm/s (default: 25)
        gain: Gain in mm/mV (default: 10)

    Returns:
        PaperSettings with calibration parameters
    """
    pixels_per_mm = estimate_pixels_per_mm(image, grid_info)

    logger.info(
        f"Scale calibration: {pixels_per_mm:.2f} px/mm, "
        f"paper_speed={paper_speed} mm/s, gain={gain} mm/mV"
    )

    return PaperSettings(
        paper_speed=paper_speed,
        gain=gain,
        pixels_per_mm=pixels_per_mm,
        major_grid_mm=5.0,
        minor_grid_mm=1.0,
    )


def estimate_pixels_per_mm(image: np.ndarray, grid_info: GridInfo) -> float:
    """
    Estimate pixels per millimeter from grid spacing.

    Standard ECG grid:
    - Major grid: 5mm x 5mm
    - Minor grid: 1mm x 1mm

    Args:
        image: Input image
        grid_info: Detected grid information

    Returns:
        Pixels per millimeter
    """
    if not grid_info.has_grid:
        # Fallback: estimate from image DPI or use default
        logger.warning("No grid detected, using default calibration")
        return estimate_from_image_size(image)

    # Use grid spacing to compute pixels per mm
    # Assume detected spacing is either minor (1mm) or major (5mm) grid
    spacing_x = grid_info.grid_spacing_x or 0
    spacing_y = grid_info.grid_spacing_y or 0

    if spacing_x == 0 or spacing_y == 0:
        logger.warning("Invalid grid spacing, using default calibration")
        return estimate_from_image_size(image)

    # Detect if spacing corresponds to minor (1mm) or major (5mm) grid
    avg_spacing = (spacing_x + spacing_y) / 2

    # Heuristic: if spacing is small (<20 pixels), likely minor grid (1mm)
    # if spacing is larger (>50 pixels), likely major grid (5mm)
    if avg_spacing < 30:
        # Minor grid: 1mm
        pixels_per_mm = avg_spacing / 1.0
        logger.info(f"Detected minor grid spacing: {avg_spacing:.1f} px = 1mm")
    else:
        # Major grid: 5mm
        pixels_per_mm = avg_spacing / 5.0
        logger.info(f"Detected major grid spacing: {avg_spacing:.1f} px = 5mm")

    return pixels_per_mm


def estimate_from_image_size(image: np.ndarray) -> float:
    """
    Estimate pixels per mm from image dimensions.

    Assumes standard ECG paper size:
    - Width: ~250mm (10 inches)
    - Height: ~170mm (6.7 inches)

    Args:
        image: Input image

    Returns:
        Estimated pixels per millimeter
    """
    h, w = image.shape[:2]

    # Assume image width corresponds to ~250mm of ECG paper
    pixels_per_mm = w / 250.0

    logger.info(f"Estimated from image size: {pixels_per_mm:.2f} px/mm")
    return pixels_per_mm


def detect_calibration_pulse(image: np.ndarray, grid_info: GridInfo) -> tuple[float, float] | None:
    """
    Detect calibration pulse (if present) to determine gain.

    Standard calibration pulse: 1mV amplitude at the beginning of ECG

    Args:
        image: Input image
        grid_info: Grid information

    Returns:
        Tuple of (pulse_height_pixels, pulse_amplitude_mv) or None
    """
    # Look for calibration pulse in left region of image
    # Typically a square wave at the start

    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image.copy()

    # Search in left 20% of image
    search_width = gray.shape[1] // 5
    search_region = gray[:, :search_width]

    # Look for vertical edges (pulse edges)
    edges = cv2.Canny(search_region, 50, 150)

    # Find vertical lines
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=10)

    if lines is None:
        return None

    # Analyze lines to find calibration pulse
    # Calibration pulse typically has two parallel vertical lines with a horizontal segment
    vertical_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if abs(x2 - x1) < 10:  # Vertical line
            vertical_lines.append((x1, y1, y2))

    if len(vertical_lines) < 2:
        return None

    # Find pulse height (distance between horizontal segments)
    # This is a simplified heuristic
    pulse_height = 0.0
    for i, (x1, y1_1, y2_1) in enumerate(vertical_lines):
        for x2, y1_2, y2_2 in vertical_lines[i + 1 :]:
            if abs(x1 - x2) < 50:  # Lines close in x
                height = abs((y1_1 + y2_1) / 2 - (y1_2 + y2_2) / 2)
                if height > pulse_height:
                    pulse_height = height

    if pulse_height > 0:
        # Assume calibration pulse is 1mV (standard)
        logger.info(f"Detected calibration pulse: {pulse_height:.1f} pixels = 1 mV")
        return (pulse_height, 1.0)

    return None


def pixels_to_time(pixels: float, paper_settings: PaperSettings) -> float:
    """
    Convert pixel distance to time (seconds).

    Args:
        pixels: Horizontal pixel distance
        paper_settings: Calibration settings

    Returns:
        Time in seconds
    """
    mm = pixels / paper_settings.pixels_per_mm
    seconds = mm / paper_settings.paper_speed
    return seconds


def pixels_to_voltage(pixels: float, paper_settings: PaperSettings) -> float:
    """
    Convert pixel distance to voltage (millivolts).

    Args:
        pixels: Vertical pixel distance
        paper_settings: Calibration settings

    Returns:
        Voltage in millivolts
    """
    mm = pixels / paper_settings.pixels_per_mm
    millivolts = mm / paper_settings.gain
    return millivolts


def time_to_pixels(seconds: float, paper_settings: PaperSettings) -> float:
    """
    Convert time to pixel distance.

    Args:
        seconds: Time in seconds
        paper_settings: Calibration settings

    Returns:
        Horizontal pixel distance
    """
    mm = seconds * paper_settings.paper_speed
    pixels = mm * paper_settings.pixels_per_mm
    return pixels


def voltage_to_pixels(millivolts: float, paper_settings: PaperSettings) -> float:
    """
    Convert voltage to pixel distance.

    Args:
        millivolts: Voltage in millivolts
        paper_settings: Calibration settings

    Returns:
        Vertical pixel distance
    """
    mm = millivolts * paper_settings.gain
    pixels = mm * paper_settings.pixels_per_mm
    return pixels


def validate_calibration(paper_settings: PaperSettings) -> tuple[bool, str]:
    """
    Validate calibration parameters.

    Args:
        paper_settings: Calibration settings

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check pixels_per_mm is reasonable
    if paper_settings.pixels_per_mm < 1.0 or paper_settings.pixels_per_mm > 100.0:
        return False, f"Invalid pixels_per_mm: {paper_settings.pixels_per_mm}"

    # Check paper speed is standard
    if paper_settings.paper_speed not in [12.5, 25.0, 50.0]:
        logger.warning(f"Non-standard paper speed: {paper_settings.paper_speed} mm/s")

    # Check gain is standard
    if paper_settings.gain not in [5.0, 10.0, 20.0]:
        logger.warning(f"Non-standard gain: {paper_settings.gain} mm/mV")

    return True, ""


# Import cv2 for detect_calibration_pulse
import cv2
