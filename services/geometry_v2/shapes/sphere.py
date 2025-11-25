"""
Sphere Class - Mặt cầu

Biểu diễn mặt cầu trong không gian 3D.
"""

import numpy as np
from .point import Point


class Sphere:
    """
    Lớp biểu diễn mặt cầu.
    
    Phương trình: (x - a)^2 + (y - b)^2 + (z - c)^2 = r^2
    
    Attributes:
        center: Tâm mặt cầu
        radius: Bán kính
    """
    
    def __init__(self, center: Point, radius: float):
        """
        Khởi tạo mặt cầu.
        
        Args:
            center: Tâm mặt cầu (3D)
            radius: Bán kính
        """
        if center.dimension != 3:
            raise ValueError("Sphere center must be 3D")
        self.center = center
        self.radius = radius
    
    def surface_area(self) -> float:
        """Tính diện tích bề mặt."""
        return 4 * np.pi * self.radius ** 2
    
    def volume(self) -> float:
        """Tính thể tích."""
        return (4/3) * np.pi * self.radius ** 3
    
    def get_equation(self) -> str:
        """Trả về phương trình."""
        return f"(x - {self.center.x})^2 + (y - {self.center.y})^2 + (z - {self.center.z})^2 = {self.radius**2}"
    
    def __repr__(self) -> str:
        return f"Sphere(center={self.center}, radius={self.radius})"
