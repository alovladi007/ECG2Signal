"""
Grid detection for ECG images using Hough Transform and morphology.
"""

import cv2
import numpy as np
from loguru import logger

from ecg2signal.types import GridInfo


def detect_grid(image: np.ndarray, min_lines: int = 5) -> GridInfo:
    """
    Detect ECG grid lines in an image.

    Args:
        image: Input image (RGB or grayscale)
        min_lines: Minimum number of lines to consider grid detected

    Returns:
        GridInfo with detected grid information
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image.copy()

    # Detect horizontal and vertical lines
    h_lines = detect_lines(gray, orientation="horizontal")
    v_lines = detect_lines(gray, orientation="vertical")

    has_grid = len(h_lines) >= min_lines and len(v_lines) >= min_lines

    if not has_grid:
        logger.warning(f"Grid not detected (h={len(h_lines)}, v={len(v_lines)} lines)")
        return GridInfo(has_grid=False, confidence=0.0)

    # Compute grid spacing
    grid_spacing_x = compute_spacing(v_lines) if len(v_lines) > 1 else None
    grid_spacing_y = compute_spacing(h_lines) if len(h_lines) > 1 else None

    # Estimate grid angle
    grid_angle = estimate_grid_angle(gray, h_lines, v_lines)

    # Compute confidence
    confidence = compute_grid_confidence(h_lines, v_lines, grid_spacing_x, grid_spacing_y)

    logger.info(
        f"Grid detected: {len(h_lines)} horizontal, {len(v_lines)} vertical lines, "
        f"spacing=({grid_spacing_x:.1f}, {grid_spacing_y:.1f}), angle={grid_angle:.2f}°"
    )

    return GridInfo(
        has_grid=True,
        horizontal_lines=h_lines,
        vertical_lines=v_lines,
        grid_spacing_x=grid_spacing_x,
        grid_spacing_y=grid_spacing_y,
        grid_angle=grid_angle,
        confidence=confidence,
    )


def detect_lines(image: np.ndarray, orientation: str = "horizontal") -> list[int]:
    """
    Detect lines of specific orientation using Hough Transform.

    Args:
        image: Grayscale image
        orientation: 'horizontal' or 'vertical'

    Returns:
        List of line positions (y-coordinates for horizontal, x-coordinates for vertical)
    """
    # Edge detection
    edges = cv2.Canny(image, 30, 90, apertureSize=3)

    # Morphological operations to enhance lines
    if orientation == "horizontal":
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    else:  # vertical
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))

    enhanced = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # Hough Line Transform
    lines = cv2.HoughLinesP(
        enhanced,
        rho=1,
        theta=np.pi / 180,
        threshold=100,
        minLineLength=image.shape[1] // 3 if orientation == "horizontal" else image.shape[0] // 3,
        maxLineGap=20,
    )

    if lines is None:
        return []

    # Extract line positions
    positions = []
    for line in lines:
        x1, y1, x2, y2 = line[0]

        if orientation == "horizontal":
            # Check if line is mostly horizontal
            if abs(y2 - y1) < abs(x2 - x1) * 0.1:
                positions.append((y1 + y2) // 2)
        else:  # vertical
            # Check if line is mostly vertical
            if abs(x2 - x1) < abs(y2 - y1) * 0.1:
                positions.append((x1 + x2) // 2)

    # Cluster nearby lines
    positions = cluster_lines(positions, threshold=5)

    return sorted(positions)


def cluster_lines(positions: list[int], threshold: int = 5) -> list[int]:
    """
    Cluster nearby line positions.

    Args:
        positions: List of line positions
        threshold: Maximum distance for clustering

    Returns:
        List of clustered line positions
    """
    if not positions:
        return []

    positions = sorted(positions)
    clusters = []
    current_cluster = [positions[0]]

    for pos in positions[1:]:
        if pos - current_cluster[-1] <= threshold:
            current_cluster.append(pos)
        else:
            # Finish current cluster
            clusters.append(int(np.mean(current_cluster)))
            current_cluster = [pos]

    # Add last cluster
    if current_cluster:
        clusters.append(int(np.mean(current_cluster)))

    return clusters


def compute_spacing(positions: list[int]) -> float:
    """
    Compute median spacing between grid lines.

    Args:
        positions: List of line positions

    Returns:
        Median spacing
    """
    if len(positions) < 2:
        return 0.0

    spacings = np.diff(positions)
    return float(np.median(spacings))


def estimate_grid_angle(gray: np.ndarray, h_lines: list[int], v_lines: list[int]) -> float:
    """
    Estimate grid rotation angle.

    Args:
        gray: Grayscale image
        h_lines: Horizontal line positions
        v_lines: Vertical line positions

    Returns:
        Angle in degrees
    """
    # Use Hough Transform to detect dominant angles
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)

    if lines is None:
        return 0.0

    # Collect angles
    angles = []
    for line in lines:
        rho, theta = line[0]
        angle = np.degrees(theta)

        # Normalize to -45 to 45 degrees
        if angle > 135:
            angle -= 180
        elif angle > 45:
            angle -= 90

        if abs(angle) < 10:  # Only consider small angles
            angles.append(angle)

    if not angles:
        return 0.0

    return float(np.median(angles))


def compute_grid_confidence(
    h_lines: list[int], v_lines: list[int], spacing_x: float | None, spacing_y: float | None
) -> float:
    """
    Compute confidence score for grid detection.

    Args:
        h_lines: Horizontal line positions
        v_lines: Vertical line positions
        spacing_x: Horizontal spacing
        spacing_y: Vertical spacing

    Returns:
        Confidence score (0-1)
    """
    score = 0.0

    # Number of lines
    score += min(len(h_lines) / 20.0, 1.0) * 0.3
    score += min(len(v_lines) / 20.0, 1.0) * 0.3

    # Spacing regularity
    if spacing_x and len(v_lines) > 2:
        spacings = np.diff(v_lines)
        regularity = 1.0 - (np.std(spacings) / (spacing_x + 1e-6))
        score += max(0, min(regularity, 1.0)) * 0.2

    if spacing_y and len(h_lines) > 2:
        spacings = np.diff(h_lines)
        regularity = 1.0 - (np.std(spacings) / (spacing_y + 1e-6))
        score += max(0, min(regularity, 1.0)) * 0.2

    return min(score, 1.0)


def remove_grid(image: np.ndarray, grid_info: GridInfo) -> np.ndarray:
    """
    Remove grid lines from image.

    Args:
        image: Input image with grid
        grid_info: Detected grid information

    Returns:
        Image with grid removed
    """
    if not grid_info.has_grid:
        return image

    result = image.copy()

    # Create mask of grid lines
    mask = np.zeros(image.shape[:2], dtype=np.uint8)

    # Draw horizontal lines
    for y in grid_info.horizontal_lines:
        cv2.line(mask, (0, y), (image.shape[1], y), 255, thickness=2)

    # Draw vertical lines
    for x in grid_info.vertical_lines:
        cv2.line(mask, (x, 0), (x, image.shape[0]), 255, thickness=2)

    # Inpaint grid lines
    if len(image.shape) == 3:
        for c in range(3):
            result[:, :, c] = cv2.inpaint(image[:, :, c], mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    else:
        result = cv2.inpaint(image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

    logger.info("Removed grid lines from image")
    return result


def extract_grid_mask(image: np.ndarray, grid_info: GridInfo) -> np.ndarray:
    """
    Extract binary mask of grid lines.

    Args:
        image: Input image
        grid_info: Detected grid information

    Returns:
        Binary mask (255 = grid, 0 = background)
    """
    mask = np.zeros(image.shape[:2], dtype=np.uint8)

    if not grid_info.has_grid:
        return mask

    # Draw horizontal lines
    for y in grid_info.horizontal_lines:
        cv2.line(mask, (0, y), (image.shape[1], y), 255, thickness=1)

    # Draw vertical lines
    for x in grid_info.vertical_lines:
        cv2.line(mask, (x, 0), (x, image.shape[0]), 255, thickness=1)

    return mask
