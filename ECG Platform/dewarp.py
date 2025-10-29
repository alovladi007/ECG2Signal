"""
Image dewarping and perspective correction for ECG images.
"""

import cv2
import numpy as np
from loguru import logger


def dewarp_image(image: np.ndarray, auto_detect: bool = True) -> np.ndarray:
    """
    Correct perspective distortion in ECG images.

    Args:
        image: Input image with potential perspective distortion
        auto_detect: If True, automatically detect corners

    Returns:
        Dewarped image
    """
    if not auto_detect:
        # No warping detected/requested
        return image

    # Detect corners
    corners = detect_document_corners(image)

    if corners is None:
        logger.info("No perspective distortion detected")
        return image

    # Apply perspective transform
    dewarped = apply_perspective_transform(image, corners)

    logger.info("Applied perspective correction")
    return dewarped


def detect_document_corners(image: np.ndarray) -> np.ndarray | None:
    """
    Detect four corners of a document in an image.

    Args:
        image: Input image

    Returns:
        Array of 4 corner points [[x, y], ...] or None if detection fails
    """
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image.copy()

    # Apply bilateral filter to preserve edges while reducing noise
    filtered = cv2.bilateralFilter(gray, 9, 75, 75)

    # Edge detection
    edges = cv2.Canny(filtered, 50, 150, apertureSize=3)

    # Dilate edges to close gaps
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilated = cv2.dilate(edges, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # Find largest contour
    largest_contour = max(contours, key=cv2.contourArea)

    # Approximate contour to polygon
    epsilon = 0.02 * cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, epsilon, True)

    # Check if we have a quadrilateral
    if len(approx) == 4:
        corners = approx.reshape(4, 2)
        return order_corners(corners)

    # Fallback: use convex hull and find 4 extreme points
    hull = cv2.convexHull(largest_contour)
    if len(hull) >= 4:
        # Find 4 corners using extreme points
        corners = find_extreme_corners(hull)
        return order_corners(corners)

    return None


def order_corners(corners: np.ndarray) -> np.ndarray:
    """
    Order corners in consistent order: [top-left, top-right, bottom-right, bottom-left].

    Args:
        corners: Array of 4 corner points

    Returns:
        Ordered corner points
    """
    # Sort by y-coordinate
    sorted_by_y = corners[np.argsort(corners[:, 1])]

    # Top two points
    top = sorted_by_y[:2]
    top = top[np.argsort(top[:, 0])]  # Sort by x

    # Bottom two points
    bottom = sorted_by_y[2:]
    bottom = bottom[np.argsort(bottom[:, 0])]  # Sort by x

    return np.array([top[0], top[1], bottom[1], bottom[0]], dtype=np.float32)


def find_extreme_corners(hull: np.ndarray) -> np.ndarray:
    """
    Find 4 extreme corner points from convex hull.

    Args:
        hull: Convex hull points

    Returns:
        4 corner points
    """
    hull = hull.reshape(-1, 2)

    # Find extreme points
    top_left = hull[np.argmin(hull[:, 0] + hull[:, 1])]
    top_right = hull[np.argmin(hull[:, 1] - hull[:, 0])]
    bottom_right = hull[np.argmax(hull[:, 0] + hull[:, 1])]
    bottom_left = hull[np.argmax(hull[:, 1] - hull[:, 0])]

    return np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.float32)


def apply_perspective_transform(
    image: np.ndarray, corners: np.ndarray, target_size: tuple[int, int] | None = None
) -> np.ndarray:
    """
    Apply perspective transform to correct distortion.

    Args:
        image: Input image
        corners: Source corners [top-left, top-right, bottom-right, bottom-left]
        target_size: Target size (width, height), or None to auto-compute

    Returns:
        Transformed image
    """
    # Compute target dimensions if not provided
    if target_size is None:
        width_top = np.linalg.norm(corners[1] - corners[0])
        width_bottom = np.linalg.norm(corners[2] - corners[3])
        width = int(max(width_top, width_bottom))

        height_left = np.linalg.norm(corners[3] - corners[0])
        height_right = np.linalg.norm(corners[2] - corners[1])
        height = int(max(height_left, height_right))

        target_size = (width, height)

    # Define target corners (rectangle)
    target_corners = np.array(
        [[0, 0], [target_size[0] - 1, 0], [target_size[0] - 1, target_size[1] - 1], [0, target_size[1] - 1]],
        dtype=np.float32,
    )

    # Compute perspective transform matrix
    M = cv2.getPerspectiveTransform(corners, target_corners)

    # Apply transform
    warped = cv2.warpPerspective(image, M, target_size, flags=cv2.INTER_LINEAR)

    return warped


def estimate_homography_from_grid(image: np.ndarray, grid_lines: dict) -> np.ndarray | None:
    """
    Estimate homography matrix from detected grid lines.

    Args:
        image: Input image
        grid_lines: Dictionary with 'horizontal' and 'vertical' line coordinates

    Returns:
        Homography matrix or None
    """
    h_lines = grid_lines.get("horizontal", [])
    v_lines = grid_lines.get("vertical", [])

    if len(h_lines) < 2 or len(v_lines) < 2:
        return None

    # Find grid intersections
    intersections = []
    for h in h_lines[:10]:  # Use up to 10 lines
        for v in v_lines[:10]:
            intersections.append([v, h])

    if len(intersections) < 4:
        return None

    intersections = np.array(intersections, dtype=np.float32)

    # Create ideal grid points (assuming square grid)
    spacing_h = np.median(np.diff(sorted(h_lines))) if len(h_lines) > 1 else 50
    spacing_v = np.median(np.diff(sorted(v_lines))) if len(v_lines) > 1 else 50

    ideal_points = []
    for i, h in enumerate(h_lines[:10]):
        for j, v in enumerate(v_lines[:10]):
            ideal_points.append([j * spacing_v, i * spacing_h])

    ideal_points = np.array(ideal_points, dtype=np.float32)[: len(intersections)]

    # Estimate homography
    if len(intersections) >= 4:
        H, mask = cv2.findHomography(intersections, ideal_points, cv2.RANSAC, 5.0)
        return H

    return None


def dewarp_with_homography(image: np.ndarray, H: np.ndarray) -> np.ndarray:
    """
    Apply homography transformation to dewarp image.

    Args:
        image: Input image
        H: Homography matrix

    Returns:
        Dewarped image
    """
    h, w = image.shape[:2]
    dewarped = cv2.warpPerspective(image, H, (w, h), flags=cv2.INTER_LINEAR)
    return dewarped
