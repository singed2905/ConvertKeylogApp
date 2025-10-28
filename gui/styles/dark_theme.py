"""Dark mode theme."""

from typing import Dict, Any

# Dark theme configuration
DARK_THEME = {
    "colors": {
        "primary": "#4FC3F7",
        "secondary": "#E91E63",
        "success": "#66BB6A", 
        "warning": "#FFB74D",
        "error": "#EF5350",
        "background": "#121212",
        "surface": "#1E1E1E",
        "text_primary": "#E0E0E0",
        "text_secondary": "#B0B0B0"
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


def get_dark_theme() -> Dict[str, Any]:
    """Get dark theme configuration."""
    return DARK_THEME.copy()
