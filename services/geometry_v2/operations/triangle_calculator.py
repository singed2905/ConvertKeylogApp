"""
Triangle Calculator - Phép tính tam giác

Các phép tính liên quan đến tam giác.
"""

import numpy as np


class TriangleCalculator:
    """
    Calculator cho các phép tính tam giác.
    
    Hỗ trợ:
    - Diện tích
    - Chu vi
    - Trọng tâm
    - Trực tâm
    - Tâm đường tròn ngoại tiếp
    - Tâm đường tròn nội tiếp
    - Các góc
    """
    
    @staticmethod
    def calculate_area(triangle) -> float:
        """Tính diện tích."""
        return triangle.area()
    
    @staticmethod
    def calculate_perimeter(triangle) -> float:
        """Tính chu vi."""
        return triangle.perimeter()
    
    @staticmethod
    def calculate_centroid(triangle):
        """Tính trọng tâm."""
        return triangle.centroid()
    
    @staticmethod
    def calculate_angles(triangle) -> tuple:
        """Tính các góc."""
        return triangle.angles()
    
    @staticmethod
    def calculate_circumcenter(triangle):
        """Tính tâm đường tròn ngoại tiếp."""
        # TODO: Implement
        pass
    
    @staticmethod
    def calculate_incenter(triangle):
        """Tính tâm đường tròn nội tiếp."""
        # TODO: Implement
        pass
    
    @staticmethod
    def calculate_orthocenter(triangle):
        """Tính trực tâm."""
        # TODO: Implement
        pass
