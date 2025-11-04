"""
Line 3D renderer for coordinate plotting
Renderer cho đường thẳng trong hệ tọa độ 3D
"""

from .base_shape import BaseShapeRenderer
from typing import Dict
import numpy as np

class Line3DRenderer(BaseShapeRenderer):
    """Renderer for 3D lines"""
    
    def get_shape_name(self) -> str:
        return "Đường thẳng"
    
    def can_render(self, data: Dict) -> bool:
        """Check if line data is valid for 3D rendering"""
        point = self.parse_coordinates(data.get('line_A1', '') or data.get('line_A2', ''), 3)
        vector = self.parse_coordinates(data.get('line_X1', '') or data.get('line_X2', ''), 3)
        return len(point) == 3 and len(vector) == 3
    
    def render(self, ax, data: Dict) -> bool:
        """Render 3D line on matplotlib axis"""
        if not self.can_render(data):
            return False
        
        try:
            # Parse point and direction vector
            point = self.parse_coordinates(data.get('line_A1', '') or data.get('line_A2', ''), 3)
            vector = self.parse_coordinates(data.get('line_X1', '') or data.get('line_X2', ''), 3)
            
            px, py, pz = point[0], point[1], point[2]
            vx, vy, vz = vector[0], vector[1], vector[2]
            
            # Generate 3D line segment
            t_range = np.linspace(-5, 5, 150)
            x_line = px + t_range * vx
            y_line = py + t_range * vy
            z_line = pz + t_range * vz
            
            # Draw 3D line
            ax.plot(x_line, y_line, z_line, 
                   color=self.color, linewidth=3, label=self.label, alpha=0.8)
            
            # Mark the given point on line
            ax.scatter(px, py, pz, c=self.color, s=100, marker='s',
                      edgecolors='white', linewidth=2)
            
            # Add 3D coordinate label
            self.add_coordinate_label(ax, point, is_3d=True)
            
            return True
            
        except Exception as e:
            print(f'Error rendering 3D line {self.group_name}: {e}')
            return False
