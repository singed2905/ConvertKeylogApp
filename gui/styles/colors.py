"""Color constants and utilities."""

from typing import Dict, Tuple

# Color constants
COLORS = {
    # Primary colors
    "BLUE_PRIMARY": "#2E86AB",
    "BLUE_SECONDARY": "#1B5299",
    "PURPLE_PRIMARY": "#A23B72",
    
    # Status colors
    "GREEN_SUCCESS": "#4CAF50",
    "ORANGE_WARNING": "#FF9800",
    "RED_ERROR": "#F44336",
    
    # Neutral colors
    "WHITE": "#FFFFFF",
    "LIGHT_GRAY": "#F8F9FA",
    "GRAY": "#E0E0E0",
    "DARK_GRAY": "#666666",
    "BLACK": "#000000"
}


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb_color: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color."""
    return f"#{''.join(f'{c:02x}' for c in rgb_color)}"
