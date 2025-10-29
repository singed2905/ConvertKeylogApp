from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseGeometry(ABC):
    """Base class for all geometric entities"""
    
    def __init__(self):
        self.encoded_values = []
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate the geometric entity"""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        pass
    
    @abstractmethod
    def get_type_code(self) -> str:
        """Get the type code for encoding"""
        pass
