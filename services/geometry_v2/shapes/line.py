"""
Line Class - Đường thẳng

Biểu diễn đường thẳng trong không gian 3D.
"""

from .point import Point
from .vector import Vector


class Line:
    """
    Lớp biểu diễn đường thẳng.
    
    Phương trình tham số: (x,y,z) = (a,b,c) + t(u,v,w)
    
    Attributes:
        point: Điểm thuộc đường thẳng
        direction: Vecto chỉ phương
    """
    
    def __init__(self, point: Point, direction: Vector):
        """
        Khởi tạo đường thẳng.
        
        Args:
            point: Điểm thuộc đường thẳng
            direction: Vecto chỉ phương
        """
        self.point = point
        self.direction = direction
        self.dimension = point.dimension
    
    def get_parametric_equation(self) -> str:
        """Trả về phương trình tham số."""
        if self.dimension == 2:
            return f"(x,y) = ({self.point.x},{self.point.y}) + t({self.direction.x},{self.direction.y})"
        return f"(x,y,z) = ({self.point.x},{self.point.y},{self.point.z}) + t({self.direction.x},{self.direction.y},{self.direction.z})"
    
    def __repr__(self) -> str:
        return f"Line(point={self.point}, direction={self.direction})"
    
    @classmethod
    def from_two_points(cls, p1: Point, p2: Point) -> 'Line':
        """
        Tạo đường thẳng từ 2 điểm.
        
        Args:
            p1: Điểm thứ nhất
            p2: Điểm thứ hai
            
        Returns:
            Line object
        """
        direction = Vector(
            p2.x - p1.x,
            p2.y - p1.y,
            p2.z - p1.z if p1.dimension == 3 else None
        )
        return cls(p1, direction)
