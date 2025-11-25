"""
Point Class - Điểm

Biểu diễn điểm trong không gian 2D/3D.
"""

from typing import Tuple, Union
import numpy as np


class Point:
    """
    Lớp biểu diễn điểm trong không gian.
    
    Attributes:
        x: Toạ độ x
        y: Toạ độ y
        z: Toạ độ z (None nếu 2D)
        dimension: Kích thước (2 hoặc 3)
    """
    
    def __init__(self, x: float, y: float, z: float = None):
        """
        Khởi tạo điểm.
        
        Args:
            x: Toạ độ x
            y: Toạ độ y
            z: Toạ độ z (optional cho 3D)
        """
        self.x = x
        self.y = y
        self.z = z
        self.dimension = 2 if z is None else 3
    
    def to_array(self) -> np.ndarray:
        """Chuyển đổi thành numpy array."""
        if self.dimension == 2:
            return np.array([self.x, self.y])
        return np.array([self.x, self.y, self.z])
    
    def to_tuple(self) -> Tuple[float, ...]:
        """Chuyển đổi thành tuple."""
        if self.dimension == 2:
            return (self.x, self.y)
        return (self.x, self.y, self.z)
    
    def __repr__(self) -> str:
        if self.dimension == 2:
            return f"Point({self.x}, {self.y})"
        return f"Point({self.x}, {self.y}, {self.z})"
    
    def __str__(self) -> str:
        return self.__repr__()
    
    @classmethod
    def from_string(cls, point_str: str) -> 'Point':
        """
        Tạo Point từ chuỗi.
        
        Args:
            point_str: Chuỗi dạng "x,y" hoặc "x,y,z"
            
        Returns:
            Point object
        """
        coords = [float(x.strip()) for x in point_str.split(',')]
        if len(coords) == 2:
            return cls(coords[0], coords[1])
        elif len(coords) == 3:
            return cls(coords[0], coords[1], coords[2])
        else:
            raise ValueError(f"Invalid point string: {point_str}")
