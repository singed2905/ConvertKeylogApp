"""
Point 3D renderer for coordinate plotting
Renderer cho điểm trong hệ tọa độ 3D
"""

from .base_shape import BaseShapeRenderer
from typing import Dict

class Point3DRenderer(BaseShapeRenderer):
    """Renderer for 3D points"""
    
    def get_shape_name(self) -> str:
        return "Điểm"
    
    def can_render(self, data: Dict) -> bool:
        """Check if point data is valid for 3D rendering"""
        coords = self.parse_coordinates(data.get('point_input', ''), 3)
        return len(coords) == 3
    
    def render(self, ax, data: Dict) -> bool:
        """Render 3D point on matplotlib axis"""
        if not self.can_render(data):
            return False
        
        try:
            coords = self.parse_coordinates(data.get('point_input', ''), 3)
            x, y, z = coords[0], coords[1], coords[2]
            
            # Draw 3D point
            ax.scatter(x, y, z, c=self.color, s=100, alpha=0.8,
                      label=self.label, edgecolors='white', linewidth=2)
            
            # Add 3D coordinate label
            self.add_coordinate_label(ax, coords, is_3d=True)
            
            return True
            
        except Exception as e:
            print(f'Error rendering 3D point {self.group_name}: {e}')
            return False
