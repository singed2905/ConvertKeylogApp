from dataclasses import dataclass
from typing import Dict, Any
from .base import BaseGeometry

@dataclass
class Point2D(BaseGeometry):
    """2D Point representation - matching TL structure"""
    x: str
    y: str
    
    def __post_init__(self):
        super().__init__()
    
    def validate(self) -> bool:
        """Validate point coordinates"""
        try:
            float(self.x) if self.x else True
            float(self.y) if self.y else True
            return True
        except ValueError:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {'x': self.x, 'y': self.y, 'type': '2D_point'}
    
    def get_type_code(self) -> str:
        return "112"  # Matching TL convention
    
    def get_coordinates(self):
        """Get coordinates as list for processing"""
        return [self.x, self.y]

@dataclass 
class Point3D(BaseGeometry):
    """3D Point representation - matching TL structure"""
    x: str
    y: str
    z: str
    
    def __post_init__(self):
        super().__init__()
    
    def validate(self) -> bool:
        """Validate point coordinates"""
        try:
            float(self.x) if self.x else True
            float(self.y) if self.y else True
            float(self.z) if self.z else True
            return True
        except ValueError:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {'x': self.x, 'y': self.y, 'z': self.z, 'type': '3D_point'}
    
    def get_type_code(self) -> str:
        return "113"  # Matching TL convention
    
    def get_coordinates(self):
        """Get coordinates as list for processing"""
        return [self.x, self.y, self.z]
