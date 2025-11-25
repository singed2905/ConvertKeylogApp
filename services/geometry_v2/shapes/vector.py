"""
Vector Class - Vecto

Biểu diễn vecto trong không gian 2D/3D.
"""

from typing import Tuple
import numpy as np


class Vector:
    """
    Lớp biểu diễn vecto.
    
    Attributes:
        x: Thành phần x
        y: Thành phần y
        z: Thành phần z (None nếu 2D)
        dimension: Kích thước
    """
    
    def __init__(self, x: float, y: float, z: float = None):
        self.x = x
        self.y = y
        self.z = z
        self.dimension = 2 if z is None else 3
    
    def to_array(self) -> np.ndarray:
        """Chuyển đổi thành numpy array."""
        if self.dimension == 2:
            return np.array([self.x, self.y])
        return np.array([self.x, self.y, self.z])
    
    def magnitude(self) -> float:
        """Tính độ dài vecto."""
        return np.linalg.norm(self.to_array())
    
    def normalize(self) -> 'Vector':
        """Chuẩn hóa vecto (vecto đơn vị)."""
        mag = self.magnitude()
        if mag == 0:
            raise ValueError("Cannot normalize zero vector")
        
        if self.dimension == 2:
            return Vector(self.x / mag, self.y / mag)
        return Vector(self.x / mag, self.y / mag, self.z / mag)
    
    def dot(self, other: 'Vector') -> float:
        """Tích vô hướng."""
        if self.dimension != other.dimension:
            raise ValueError("Vectors must have same dimension")
        return np.dot(self.to_array(), other.to_array())
    
    def cross(self, other: 'Vector') -> 'Vector':
        """Tích có hướng (chỉ cho 3D)."""
        if self.dimension != 3 or other.dimension != 3:
            raise ValueError("Cross product only for 3D vectors")
        
        result = np.cross(self.to_array(), other.to_array())
        return Vector(result[0], result[1], result[2])
    
    def __repr__(self) -> str:
        if self.dimension == 2:
            return f"Vector({self.x}, {self.y})"
        return f"Vector({self.x}, {self.y}, {self.z})"
    
    @classmethod
    def from_string(cls, vector_str: str) -> 'Vector':
        """Tạo Vector từ chuỗi."""
        coords = [float(x.strip()) for x in vector_str.split(',')]
        if len(coords) == 2:
            return cls(coords[0], coords[1])
        elif len(coords) == 3:
            return cls(coords[0], coords[1], coords[2])
        else:
            raise ValueError(f"Invalid vector string: {vector_str}")
