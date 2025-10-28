"""String manipulation utilities."""

import re
from typing import List, Optional, Dict, Any


def clean_string(text: str) -> str:
    """Clean and normalize string."""
    # TODO: Implement string cleaning logic
    return text.strip()


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def parse_csv_line(line: str, delimiter: str = ',') -> List[str]:
    """Parse CSV line handling quoted fields."""
    # TODO: Implement CSV line parsing
    return line.split(delimiter)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for file system."""
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()


def truncate_string(text: str, max_length: int, suffix: str = '...') -> str:
    """Truncate string to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_numbers(text: str) -> List[float]:
    """Extract all numbers from text."""
    pattern = r'-?\d+(?:\.\d+)?'
    matches = re.findall(pattern, text)
    return [float(match) for match in matches]
