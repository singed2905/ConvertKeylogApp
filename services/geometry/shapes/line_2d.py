"""
Line 2D renderer for coordinate plotting
Renderer cho đường thẳng trong hệ tọa độ 2D
"""

from .base_shape import BaseShapeRenderer
from typing import Dict
import numpy as np

class Line2DRenderer(BaseShapeRenderer):
    """Renderer for 2D lines"""
    
    def get_shape_name(self) -> str:
        return "Đường thẳng"
    
    def can_render(self, data: Dict) -> bool:
        """Check if line data is valid for 2D rendering"""
        point = self.parse_coordinates(data.get('line_A1', '') or data.get('line_A2', ''), 2)
        vector = self.parse_coordinates(data.get('line_X1', '') or data.get('line_X2', ''), 2)
        return len(point) == 2 and len(vector) == 2
    
    def render(self, ax, data: Dict) -> bool:
        """Render 2D line on matplotlib axis"""
        if not self.can_render(data):
            return False
        
        try:
            # Parse point and direction vector
            point = self.parse_coordinates(data.get('line_A1', '') or data.get('line_A2', ''), 2)
            vector = self.parse_coordinates(data.get('line_X1', '') or data.get('line_X2', ''), 2)
            
            px, py = point[0], point[1]
            vx, vy = vector[0], vector[1]
            
            # Generate line segment
            t_range = np.linspace(-8, 8, 200)  # Extended range for better visibility
            x_line = px + t_range * vx
            y_line = py + t_range * vy
            
            # Draw line
            ax.plot(x_line, y_line, color=self.color, linewidth=2.5, label=self.label, alpha=0.8)
            
            # Mark the given point on line
            ax.scatter(px, py, c=self.color, s=80, marker='s', 
                      edgecolors='white', linewidth=2)
            
            # Add point label
            ax.annotate(
                f'{self.group_name}({px}, {py})',
                (px, py), xytext=(8, 8), textcoords='offset points',
                fontsize=9, color=self.color, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7, edgecolor=self.color)
            )
            
            return True
            
        except Exception as e:
            print(f'Error rendering 2D line {self.group_name}: {e}')
            return False
