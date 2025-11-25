"""
Plane Class - Mặt phẳng

Biểu diễn mặt phẳng trong không gian 3D.
"""

import numpy as np
from .vector import Vector


class Plane:
    """
    Lớp biểu diễn mặt phẳng.
    
    Phương trình tổng quát: ax + by + cz + d = 0
    
    Attributes:
        a, b, c: Hệ số của phương trình
        d: Hằng số tự do
    """
    
    def __init__(self, a: float, b: float, c: float, d: float):
        """
        Khởi tạo mặt phẳng.
        
        Args:
            a, b, c: Hệ số
            d: Hằng số
        """
        self.a = a
        self.b = b
        self.c = c
        self.d = d
    
    def get_normal_vector(self) -> Vector:
        """Lấy vecto pháp tuyến."""
        return Vector(self.a, self.b, self.c)
    
    def get_equation(self) -> str:
        """Trả về phương trình dạng chuỗi."""
        return f"{self.a}x + {self.b}y + {self.c}z + {self.d} = 0"
    
    def __repr__(self) -> str:
        return f"Plane({self.a}, {self.b}, {self.c}, {self.d})"
    
    @classmethod
    def from_string(cls, equation_str: str) -> 'Plane':
        """
        Tạo Plane từ chuỗi phương trình.
        
        Args:
            equation_str: Chuỗi dạng "a,b,c,d"
            
        Returns:
            Plane object
        """
        coeffs = [float(x.strip()) for x in equation_str.split(',')]
        if len(coeffs) != 4:
            raise ValueError(f"Invalid plane equation: {equation_str}")
        return cls(coeffs[0], coeffs[1], coeffs[2], coeffs[3])
