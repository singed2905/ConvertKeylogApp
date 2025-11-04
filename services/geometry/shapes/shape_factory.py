"""
Shape renderer factory for creating appropriate renderers
Factory tạo renderer phù hợp cho từng loại hình học
"""

from typing import Optional
from .base_shape import BaseShapeRenderer
from .point_2d import Point2DRenderer
from .point_3d import Point3DRenderer
from .line_2d import Line2DRenderer
from .line_3d import Line3DRenderer
from .circle import CircleRenderer
from .sphere import SphereRenderer
from .plane import PlaneRenderer

class ShapeRendererFactory:
    """Factory for creating shape renderers based on type and dimensions"""
    
    @staticmethod
    def get_renderer(shape_type: str, is_3d: bool, color: str, group_name: str) -> Optional[BaseShapeRenderer]:
        """Get appropriate renderer for shape type and dimensions"""
        try:
            if shape_type == "Điểm":
                return Point3DRenderer(color, group_name) if is_3d else Point2DRenderer(color, group_name)
            
            elif shape_type == "Đường thẳng":
                return Line3DRenderer(color, group_name) if is_3d else Line2DRenderer(color, group_name)
            
            elif shape_type == "Mặt phẳng":
                # Planes are always 3D
                return PlaneRenderer(color, group_name)
            
            elif shape_type == "Đường tròn":
                # Circles are always 2D
                return CircleRenderer(color, group_name)
            
            elif shape_type == "Mặt cầu":
                # Spheres are always 3D
                return SphereRenderer(color, group_name)
            
            else:
                print(f"Warning: Unknown shape type '{shape_type}'")
                return None
                
        except Exception as e:
            print(f"Error creating renderer for {shape_type}: {e}")
            return None
    
    @staticmethod
    def get_supported_shapes() -> dict:
        """Get dictionary of supported shapes and their dimensionality"""
        return {
            "Điểm": ["2D", "3D"],
            "Đường thẳng": ["2D", "3D"],
            "Mặt phẳng": ["3D"],
            "Đường tròn": ["2D"],
            "Mặt cầu": ["3D"]
        }
    
    @staticmethod
    def is_shape_compatible_with_dimension(shape_type: str, is_3d: bool) -> bool:
        """Check if shape type is compatible with given dimension"""
        supported = ShapeRendererFactory.get_supported_shapes()
        if shape_type not in supported:
            return False
        
        dim_str = "3D" if is_3d else "2D"
        return dim_str in supported[shape_type]
    
    @staticmethod
    def get_all_renderer_classes():
        """Get all available renderer classes for testing/validation"""
        return {
            "Point2D": Point2DRenderer,
            "Point3D": Point3DRenderer,
            "Line2D": Line2DRenderer,
            "Line3D": Line3DRenderer,
            "Circle": CircleRenderer,
            "Sphere": SphereRenderer,
            "Plane": PlaneRenderer
        }
