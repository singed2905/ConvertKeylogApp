"""
Geometry V2 Service Package

Hỗ trợ 7 loại hình học:
- Điểm (Point)
- Vecto (Vector)
- Đường thẳng (Line)
- Mặt phẳng (Plane)
- Đường tròn (Circle)
- Mặt cầu (Sphere)
- Tam giác (Triangle)

Các phép tính:
- Tương giao
- Khoảng cách
- Diện tích
- Thể tích
- PT đường thẳng
- PT mặt phẳng
- Góc
- Tích vô hướng 2 vecto
- Vecto đơn vị
- Phép tính của tam giác
"""

from .geometry_v2_service import GeometryV2Service
from .shapes import (
    Point,
    Vector,
    Line,
    Plane,
    Circle,
    Sphere,
    Triangle
)
from .operations import (
    IntersectionCalculator,
    DistanceCalculator,
    AreaCalculator,
    VolumeCalculator,
    LineEquationCalculator,
    PlaneEquationCalculator,
    AngleCalculator,
    DotProductCalculator,
    UnitVectorCalculator,
    TriangleCalculator
)

__all__ = [
    'GeometryV2Service',
    # Shapes
    'Point',
    'Vector',
    'Line',
    'Plane',
    'Circle',
    'Sphere',
    'Triangle',
    # Operations
    'IntersectionCalculator',
    'DistanceCalculator',
    'AreaCalculator',
    'VolumeCalculator',
    'LineEquationCalculator',
    'PlaneEquationCalculator',
    'AngleCalculator',
    'DotProductCalculator',
    'UnitVectorCalculator',
    'TriangleCalculator'
]
