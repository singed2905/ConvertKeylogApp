"""Mathematical utilities."""

import math
from typing import List, Tuple, Optional, Union


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division with default value for zero denominator."""
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ValueError):
        return default


def round_to_precision(value: float, precision: int = 2) -> float:
    """Round value to specified precision."""
    return round(value, precision)


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp value between min and max."""
    return max(min_value, min(value, max_value))


def calculate_distance_2d(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two 2D points."""
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)


def calculate_distance_3d(point1: Tuple[float, float, float], point2: Tuple[float, float, float]) -> float:
    """Calculate Euclidean distance between two 3D points."""
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2 + (point2[2] - point1[2])**2)


def parse_coordinates(coord_string: str) -> List[float]:
    """Parse coordinate string into list of floats."""
    # TODO: Implement coordinate parsing logic
    return []


def is_valid_number(value: str) -> bool:
    """Check if string represents a valid number."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False
