"""File operation utilities."""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import hashlib


class FileUtils:
    """File utility class - giống TL FileUtils."""
    
    @staticmethod
    def load_modes_from_json(file_path: str) -> List[str]:
        """Load modes from JSON file - giống TL."""
        try:
            if not os.path.exists(file_path):
                # Tạo file mặc định nếu không tồn tại
                default_modes = {
                    "modes": ["Geometry Mode", "Equation Mode", "Polynomial Equation Mode"]
                }
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_modes, f, ensure_ascii=False, indent=2)
                return default_modes["modes"]
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("modes", ["Geometry Mode"])
                
        except Exception as e:
            print(f"Lỗi load modes: {e}")
            return ["Geometry Mode", "Equation Mode", "Polynomial Equation Mode"]
    
    @staticmethod
    def ensure_directory_exists(directory_path: Path) -> None:
        """Ensure directory exists, create if not."""
        directory_path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_file_hash(file_path: Path, algorithm: str = "md5") -> str:
        """Calculate file hash."""
        # TODO: Implement file hashing logic
        return ""
    
    @staticmethod
    def get_file_size(file_path: Path) -> int:
        """Get file size in bytes."""
        # TODO: Implement file size calculation
        return 0
    
    @staticmethod
    def load_json_file(file_path: Path) -> Dict[str, Any]:
        """Load JSON file safely."""
        # TODO: Implement JSON loading with error handling
        return {}
    
    @staticmethod
    def save_json_file(data: Dict[str, Any], file_path: Path) -> None:
        """Save data to JSON file."""
        # TODO: Implement JSON saving with error handling
        pass
    
    @staticmethod
    def get_file_extension(file_path: Path) -> str:
        """Get file extension in lowercase."""
        return file_path.suffix.lower()
    
    @staticmethod
    def is_valid_file_type(file_path: Path, allowed_extensions: List[str]) -> bool:
        """Check if file type is in allowed list."""
        extension = FileUtils.get_file_extension(file_path)
        return extension in [ext.lower() for ext in allowed_extensions]


# Legacy functions for compatibility
def ensure_directory_exists(directory_path: Path) -> None:
    """Ensure directory exists, create if not."""
    directory_path.mkdir(parents=True, exist_ok=True)


def get_file_hash(file_path: Path, algorithm: str = "md5") -> str:
    """Calculate file hash."""
    # TODO: Implement file hashing logic
    return ""


def get_file_size(file_path: Path) -> int:
    """Get file size in bytes."""
    # TODO: Implement file size calculation
    return 0


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load JSON file safely."""
    # TODO: Implement JSON loading with error handling
    return {}


def save_json_file(data: Dict[str, Any], file_path: Path) -> None:
    """Save data to JSON file."""
    # TODO: Implement JSON saving with error handling
    pass


def get_file_extension(file_path: Path) -> str:
    """Get file extension in lowercase."""
    return file_path.suffix.lower()


def is_valid_file_type(file_path: Path, allowed_extensions: List[str]) -> bool:
    """Check if file type is in allowed list."""
    extension = get_file_extension(file_path)
    return extension in [ext.lower() for ext in allowed_extensions]
