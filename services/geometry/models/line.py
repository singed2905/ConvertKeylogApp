from dataclasses import dataclass
from typing import Dict, Any
from .base import BaseGeometry

@dataclass
class Line3D(BaseGeometry):
    """3D Line representation - matching TL structure
    
    Represents a line using point + direction vector:
    Line: Point(A,B,C) + t*Vector(X,Y,Z)
    """
    A: str  # Point coordinate X
    B: str  # Point coordinate Y
    C: str  # Point coordinate Z
    X: str  # Direction vector X
    Y: str  # Direction vector Y
    Z: str  # Direction vector Z
    
    def __post_init__(self):
        super().__init__()
    
    def validate(self) -> bool:
        """Validate line parameters"""
        try:
            # Check if coordinates are valid numbers (or empty)
            coords = [self.A, self.B, self.C, self.X, self.Y, self.Z]
            for coord in coords:
                if coord:  # Only validate non-empty values
                    float(coord)
            return True
        except ValueError:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'point': {'A': self.A, 'B': self.B, 'C': self.C},
            'direction': {'X': self.X, 'Y': self.Y, 'Z': self.Z},
            'type': '3D_line'
        }
    
    def get_type_code(self) -> str:
        return "21"  # Matching TL convention
    
    def get_point_coordinates(self):
        """Get point coordinates as list"""
        return [self.A, self.B, self.C]
    
    def get_direction_vector(self):
        """Get direction vector as list"""
        return [self.X, self.Y, self.Z]
    
    def get_all_parameters(self):
        """Get all parameters as list for encoding"""
        return [self.A, self.B, self.C, self.X, self.Y, self.Z]
