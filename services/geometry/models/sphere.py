from dataclasses import dataclass
from typing import Dict, Any
from .base import BaseGeometry

@dataclass
class Sphere(BaseGeometry):
    """Sphere representation - matching TL structure
    
    Represents a 3D sphere with center (x,y,z) and radius r
    """
    x: str  # Center X coordinate
    y: str  # Center Y coordinate
    z: str  # Center Z coordinate
    r: str  # Radius
    
    def __post_init__(self):
        super().__init__()
    
    def validate(self) -> bool:
        """Validate sphere parameters"""
        try:
            # Check coordinates and radius
            if self.x:
                float(self.x)
            if self.y:
                float(self.y) 
            if self.z:
                float(self.z)
            if self.r:
                radius_val = float(self.r)
                if radius_val <= 0:
                    return False
            return True
        except ValueError:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'center': {'x': self.x, 'y': self.y, 'z': self.z},
            'radius': self.r,
            'type': 'sphere'
        }
    
    def get_type_code(self) -> str:
        return "51"  # Matching TL convention
    
    def get_center(self):
        """Get center coordinates as list"""
        return [self.x, self.y, self.z]
    
    def get_parameters(self):
        """Get all parameters as list for encoding"""
        return [self.x, self.y, self.z, self.r]
