"""
Circle renderer for 2D coordinate plotting
Renderer cho đường tròn trong hệ tọa độ 2D
"""

from .base_shape import BaseShapeRenderer
from typing import Dict, List
import matplotlib.pyplot as plt

class CircleRenderer(BaseShapeRenderer):
    """Renderer for circles in 2D coordinate system"""
    
    def get_shape_name(self) -> str:
        return "Đường tròn"
    
    def can_render(self, data: Dict) -> bool:
        """Check if circle data is valid for rendering"""
        # Check center coordinates
        center = self.parse_coordinates(data.get('circle_center', ''), 2)
        if len(center) != 2:
            return False
        
        # Check radius
        radius_str = data.get('circle_radius', '')
        return self.validate_positive_value(radius_str)
    
    def render(self, ax, data: Dict) -> bool:
        """Render circle on 2D matplotlib axis"""
        if not self.can_render(data):
            return False
        
        try:
            # Parse data
            center = self.parse_coordinates(data.get('circle_center', ''), 2)
            radius = self.parse_single_value(data.get('circle_radius', ''))
            
            if not center or radius is None or radius <= 0:
                return False
            
            cx, cy = center[0], center[1]
            
            # Create and add circle
            circle = plt.Circle(
                (cx, cy), radius,
                fill=False, color=self.color, linewidth=2,
                label=self.label
            )
            ax.add_patch(circle)
            
            # Mark center with cross
            ax.scatter(cx, cy, c=self.color, s=60, marker='+', linewidths=3)
            
            # Add coordinate label for center
            ax.annotate(
                f'Tâm {self.group_name}({cx}, {cy})\nR={radius}',
                (cx, cy), xytext=(8, 8), textcoords='offset points',
                fontsize=8, color=self.color, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7, edgecolor=self.color)
            )
            
            # Adjust axis limits to include circle
            self.safe_set_axis_limits(ax, center, radius, is_3d=False)
            
            return True
            
        except Exception as e:
            print(f'Error rendering circle {self.group_name}: {e}')
            return False
    
    def get_bounding_box(self, data: Dict) -> List[float]:
        """Get bounding box [xmin, xmax, ymin, ymax] for the circle"""
        if not self.can_render(data):
            return []
        
        try:
            center = self.parse_coordinates(data.get('circle_center', ''), 2)
            radius = self.parse_single_value(data.get('circle_radius', ''))
            
            if center and radius:
                cx, cy = center[0], center[1]
                return [cx - radius, cx + radius, cy - radius, cy + radius]
        except:
            pass
        
        return []
