"""Abstract base converter class."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseConverter(ABC):
    """Abstract base class for all converters."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    @abstractmethod
    def convert(self, input_data: Any) -> Any:
        """Convert input data to output format."""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data format."""
        pass
