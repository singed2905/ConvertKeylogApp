"""
Area Calculator - Diện tích

Tính diện tích các hình học.
"""

import numpy as np


class AreaCalculator:
    """
    Calculator cho phép tính diện tích.
    
    Hỗ trợ:
    - Tam giác
    - Đường tròn
    - Mặt cầu (diện tích bề mặt)
    """
    
    @staticmethod
    def calculate(shape):
        """
        Tính diện tích của hình.
        
        Args:
            shape: Hình cần tính
            
        Returns:
            Diện tích
        """
        # TODO: Implement area logic
        return {"status": "not_implemented"}
    
    @staticmethod
    def triangle_area(triangle) -> float:
        """Tính diện tích tam giác."""
        return triangle.area()
    
    @staticmethod
    def circle_area(circle) -> float:
        """Tính diện tích hình tròn."""
        return circle.area()
    
    @staticmethod
    def sphere_surface_area(sphere) -> float:
        """Tính diện tích bề mặt mặt cầu."""
        return sphere.surface_area()
