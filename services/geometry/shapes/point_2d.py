"""
Point 2D renderer for coordinate plotting
Renderer cho điểm trong hệ tọa độ 2D
"""

from .base_shape import BaseShapeRenderer
from typing import Dict

class Point2DRenderer(BaseShapeRenderer):
    """Renderer for 2D points"""
    
    def get_shape_name(self) -> str:
        return "Điểm"
    
    def can_render(self, data: Dict) -> bool:
        """Check if point data is valid for 2D rendering"""
        coords = self.parse_coordinates(data.get('point_input', ''), 2)
        return len(coords) == 2
    
    def render(self, ax, data: Dict) -> bool:
        """Render 2D point on matplotlib axis"""
        if not self.can_render(data):
            return False
        
        try:
            coords = self.parse_coordinates(data.get('point_input', ''), 2)
            x, y = coords[0], coords[1]
            
            # Draw point
            ax.scatter(x, y, c=self.color, s=100, alpha=0.8, 
                      label=self.label, edgecolors='white', linewidth=2)
            
            # Add coordinate label
            self.add_coordinate_label(ax, coords, offset=(8, 8), is_3d=False)
            
            return True
            
        except Exception as e:
            print(f'Error rendering 2D point {self.group_name}: {e}')
            return False
