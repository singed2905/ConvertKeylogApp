"""Conversion result model."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ConversionStatus(Enum):
    """Conversion status enumeration."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    PENDING = "pending"


@dataclass
class ConversionResult:
    """Conversion result data structure."""
    status: ConversionStatus
    input_data: Any
    output_data: Any
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
    processing_time: float
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        # TODO: Implement serialization
        return {}
    
    def is_successful(self) -> bool:
        """Check if conversion was successful."""
        return self.status == ConversionStatus.SUCCESS
