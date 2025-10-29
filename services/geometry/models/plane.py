from dataclasses import dataclass
from typing import Dict, Any
from .base import BaseGeometry

@dataclass
class Plane(BaseGeometry):
    """Plane representation - matching TL structure
    
    Represents a plane using equation: ax + by + cz + d = 0
    """
    a: str  # Coefficient of x
    b: str  # Coefficient of y  
    c: str  # Coefficient of z
    d: str  # Constant term
    
    def __post_init__(self):
        super().__init__()
    
    def validate(self) -> bool:
        """Validate plane coefficients"""
        try:
            # Check if coefficients are valid numbers (or empty)
            coeffs = [self.a, self.b, self.c, self.d]
            for coeff in coeffs:
                if coeff:  # Only validate non-empty values
                    float(coeff)
            
            # Check that at least one of a, b, c is non-zero (valid plane)
            non_zero_coeffs = [c for c in [self.a, self.b, self.c] if c and float(c) != 0]
            return len(non_zero_coeffs) > 0
        except ValueError:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'coefficients': {'a': self.a, 'b': self.b, 'c': self.c, 'd': self.d},
            'equation': f"{self.a}x + {self.b}y + {self.c}z + {self.d} = 0",
            'type': 'plane'
        }
    
    def get_type_code(self) -> str:
        return "31"  # Matching TL convention
    
    def get_coefficients(self):
        """Get coefficients as list for processing"""
        return [self.a, self.b, self.c, self.d]
    
    def get_normal_vector(self):
        """Get normal vector (a, b, c)"""
        return [self.a, self.b, self.c]
