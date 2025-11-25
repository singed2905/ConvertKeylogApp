"""
Triangle Class - Tam giác

Biểu diễn tam giác trong không gian 2D/3D.
"""

import numpy as np
from .point import Point
from .vector import Vector


class Triangle:
    """
    Lớp biểu diễn tam giác.
    
    Attributes:
        a, b, c: 3 đỉnh
        dimension: Kích thước
    """
    
    def __init__(self, a: Point, b: Point, c: Point):
        """
        Khởi tạo tam giác.
        
        Args:
            a, b, c: 3 đỉnh của tam giác
        """
        if not (a.dimension == b.dimension == c.dimension):
            raise ValueError("All vertices must have same dimension")
        self.a = a
        self.b = b
        self.c = c
        self.dimension = a.dimension
    
    def side_lengths(self) -> tuple:
        """Tính độ dài 3 cạnh."""
        ab = np.linalg.norm(self.b.to_array() - self.a.to_array())
        bc = np.linalg.norm(self.c.to_array() - self.b.to_array())
        ca = np.linalg.norm(self.a.to_array() - self.c.to_array())
        return (ab, bc, ca)
    
    def perimeter(self) -> float:
        """Tính chu vi."""
        return sum(self.side_lengths())
    
    def area(self) -> float:
        """Tính diện tích (dùng công thức Heron)."""
        a, b, c = self.side_lengths()
        s = (a + b + c) / 2  # Nửa chu vi
        area = np.sqrt(s * (s - a) * (s - b) * (s - c))
        return area
    
    def centroid(self) -> Point:
        """Tính trọng tâm."""
        if self.dimension == 2:
            cx = (self.a.x + self.b.x + self.c.x) / 3
            cy = (self.a.y + self.b.y + self.c.y) / 3
            return Point(cx, cy)
        else:
            cx = (self.a.x + self.b.x + self.c.x) / 3
            cy = (self.a.y + self.b.y + self.c.y) / 3
            cz = (self.a.z + self.b.z + self.c.z) / 3
            return Point(cx, cy, cz)
    
    def angles(self) -> tuple:
        """Tính 3 góc (rad)."""
        a, b, c = self.side_lengths()
        
        # Công thức cosine
        angle_A = np.arccos((b**2 + c**2 - a**2) / (2 * b * c))
        angle_B = np.arccos((a**2 + c**2 - b**2) / (2 * a * c))
        angle_C = np.arccos((a**2 + b**2 - c**2) / (2 * a * b))
        
        return (angle_A, angle_B, angle_C)
    
    def __repr__(self) -> str:
        return f"Triangle(a={self.a}, b={self.b}, c={self.c})"
