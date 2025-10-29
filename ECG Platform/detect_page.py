"""
Page detection and border cleanup for ECG images.
"""

import cv2
import numpy as np
from loguru import logger


def detect_page_region(image: np.ndarray, margin: int = 10) -> np.ndarray:
    """
    Detect and extract the main ECG page region from an image.

    Handles:
    - Border detection and cropping
    - Shadow/edge removal
    - Background cleanup

    Args:
        image: Input image (RGB or grayscale)
        margin: Margin to add around detected region (pixels)

    Returns:
        Cropped page region
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image.copy()

    # Apply slight blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use adaptive thresholding to find content
    binary = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 10
    )

    # Morphological operations to connect components
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # Find contours
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        logger.warning("No contours found, returning original image")
        return image

    # Find the largest contour (assumed to be the page)
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)

    # Add margin
    h_img, w_img = gray.shape[:2]
    x = max(0, x - margin)
    y = max(0, y - margin)
    w = min(w_img - x, w + 2 * margin)
    h = min(h_img - y, h + 2 * margin)

    # Crop the image
    if len(image.shape) == 3:
        cropped = image[y : y + h, x : x + w]
    else:
        cropped = image[y : y + h, x : x + w]

    logger.info(f"Detected page region: ({x}, {y}, {w}, {h})")
    return cropped


def remove_border_artifacts(image: np.ndarray, border_width: int = 20) -> np.ndarray:
    """
    Remove border artifacts and noise from image edges.

    Args:
        image: Input image
        border_width: Width of border to clean (pixels)

    Returns:
        Image with cleaned borders
    """
    # Create mask for central region
    h, w = image.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    mask[border_width:-border_width, border_width:-border_width] = 255

    # Apply mask
    if len(image.shape) == 3:
        result = image.copy()
        for c in range(3):
            result[:, :, c] = cv2.bitwise_and(image[:, :, c], mask)
    else:
        result = cv2.bitwise_and(image, mask)

    return result


def detect_orientation(image: np.ndarray) -> float:
    """
    Detect image orientation/rotation angle.

    Args:
        image: Input image

    Returns:
        Rotation angle in degrees (0, 90, 180, or 270)
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image.copy()

    # Detect edges
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Use Hough Line Transform to detect dominant lines
    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)

    if lines is None:
        return 0.0

    # Analyze angles
    angles = []
    for line in lines:
        rho, theta = line[0]
        angle = np.degrees(theta)
        angles.append(angle)

    # Find dominant angle (clustering around 0, 90, 180)
    angles = np.array(angles)

    # Normalize to 0-180
    angles = angles % 180

    # Find most common orientation
    hist, bins = np.histogram(angles, bins=36)  # 5-degree bins
    dominant_bin = np.argmax(hist)
    dominant_angle = bins[dominant_bin]

    # Snap to cardinal directions
    if dominant_angle < 22.5 or dominant_angle > 157.5:
        return 0.0
    elif 67.5 < dominant_angle < 112.5:
        return 90.0
    else:
        return 0.0


def auto_rotate(image: np.ndarray) -> tuple[np.ndarray, float]:
    """
    Automatically detect and correct image orientation.

    Args:
        image: Input image

    Returns:
        Tuple of (rotated image, rotation angle applied)
    """
    angle = detect_orientation(image)

    if abs(angle) < 1.0:
        return image, 0.0

    # Rotate image
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, -angle, 1.0)

    if len(image.shape) == 3:
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    else:
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=255)

    logger.info(f"Auto-rotated image by {angle} degrees")
    return rotated, angle


def normalize_background(image: np.ndarray) -> np.ndarray:
    """
    Normalize image background to white.

    Args:
        image: Input image

    Returns:
        Image with normalized background
    """
    if len(image.shape) == 3:
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)

        # Normalize L channel
        l_channel = lab[:, :, 0]
        l_mean = np.mean(l_channel)
        l_std = np.std(l_channel)

        l_normalized = ((l_channel - l_mean) / l_std * 50 + 200).astype(np.uint8)
        lab[:, :, 0] = np.clip(l_normalized, 0, 255)

        # Convert back to RGB
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    else:
        # Grayscale normalization
        mean = np.mean(image)
        std = np.std(image)
        result = ((image - mean) / std * 50 + 200).astype(np.uint8)
        result = np.clip(result, 0, 255)

    return result
