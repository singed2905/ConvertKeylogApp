"""
Circle Class - Đường tròn

Biểu diễn đường tròn trong mặt phẳng 2D.
"""

import numpy as np
from .point import Point


class Circle:
    """
    Lớp biểu diễn đường tròn.
    
    Phương trình: (x - a)^2 + (y - b)^2 = r^2
    
    Attributes:
        center: Tâm đường tròn
        radius: Bán kính
    """
    
    def __init__(self, center: Point, radius: float):
        """
        Khởi tạo đường tròn.
        
        Args:
            center: Tâm đường tròn (2D)
            radius: Bán kính
        """
        if center.dimension != 2:
            raise ValueError("Circle center must be 2D")
        self.center = center
        self.radius = radius
    
    def area(self) -> float:
        """Tính diện tích."""
        return np.pi * self.radius ** 2
    
    def circumference(self) -> float:
        """Tính chu vi."""
        return 2 * np.pi * self.radius
    
    def get_equation(self) -> str:
        """Trả về phương trình."""
        return f"(x - {self.center.x})^2 + (y - {self.center.y})^2 = {self.radius**2}"
    
    def __repr__(self) -> str:
        return f"Circle(center={self.center}, radius={self.radius})"
