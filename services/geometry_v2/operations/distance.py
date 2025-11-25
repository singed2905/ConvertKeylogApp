"""
Distance Calculator - Khoảng cách

Tính khoảng cách giữa các hình học.
"""

import numpy as np


class DistanceCalculator:
    """
    Calculator cho phép tính khoảng cách.
    
    Hỗ trợ:
    - Điểm - Điểm
    - Điểm - Đường thẳng
    - Điểm - Mặt phẳng
    - Đường thẳng - Đường thẳng
    - v.v...
    """
    
    @staticmethod
    def calculate(shape_a, shape_b):
        """
        Tính khoảng cách giữa 2 hình.
        
        Args:
            shape_a: Hình thứ nhất
            shape_b: Hình thứ hai
            
        Returns:
            Khoảng cách
        """
        # TODO: Implement distance logic
        return {"status": "not_implemented"}
    
    @staticmethod
    def point_point_distance(p1, p2) -> float:
        """Khoảng cách giữa 2 điểm."""
        return np.linalg.norm(p2.to_array() - p1.to_array())
    
    @staticmethod
    def point_line_distance(point, line) -> float:
        """Khoảng cách từ điểm đến đường thẳng."""
        # TODO: Implement
        pass
    
    @staticmethod
    def point_plane_distance(point, plane) -> float:
        """Khoảng cách từ điểm đến mặt phẳng."""
        # TODO: Implement
        pass
