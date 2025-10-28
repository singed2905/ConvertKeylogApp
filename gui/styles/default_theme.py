"""Default application theme."""

from typing import Dict, Any

# Default theme configuration
DEFAULT_THEME = {
    "colors": {
        "primary": "#2E86AB",
        "secondary": "#A23B72", 
        "success": "#4CAF50",
        "warning": "#FF9800",
        "error": "#F44336",
        "background": "#F8F9FA",
        "surface": "#FFFFFF",
        "text_primary": "#1B5299",
        "text_secondary": "#666666"
    },
    "fonts": {
        "default": ("Arial", 10),
        "header": ("Arial", 14, "bold"),
        "title": ("Arial", 18, "bold"),
        "button": ("Arial", 9, "bold")
    },
    "spacing": {
        "small": 5,
        "medium": 10,
        "large": 20
    }
}


def get_default_theme() -> Dict[str, Any]:
    """Get default theme configuration."""
    return DEFAULT_THEME.copy()
