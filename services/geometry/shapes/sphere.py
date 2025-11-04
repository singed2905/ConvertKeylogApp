"""
Sphere renderer for 3D coordinate plotting
Renderer cho mặt cầu trong hệ tọa độ 3D
"""

from .base_shape import BaseShapeRenderer
from typing import Dict, List
import numpy as np

class SphereRenderer(BaseShapeRenderer):
    """Renderer for spheres in 3D coordinate system"""
    
    def get_shape_name(self) -> str:
        return "Mặt cầu"
    
    def can_render(self, data: Dict) -> bool:
        """Check if sphere data is valid for rendering"""
        # Check center coordinates
        center = self.parse_coordinates(data.get('sphere_center', ''), 3)
        if len(center) != 3:
            return False
        
        # Check radius
        radius_str = data.get('sphere_radius', '')
        return self.validate_positive_value(radius_str)
    
    def render(self, ax, data: Dict) -> bool:
        """Render sphere on 3D matplotlib axis"""
        if not self.can_render(data):
            return False
        
        try:
            # Parse data
            center = self.parse_coordinates(data.get('sphere_center', ''), 3)
            radius = self.parse_single_value(data.get('sphere_radius', ''))
            
            if not center or radius is None or radius <= 0:
                return False
            
            cx, cy, cz = center[0], center[1], center[2]
            
            # Create sphere wireframe
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi, 20)
            
            x_sphere = cx + radius * np.outer(np.cos(u), np.sin(v))
            y_sphere = cy + radius * np.outer(np.sin(u), np.sin(v))
            z_sphere = cz + radius * np.outer(np.ones(np.size(u)), np.cos(v))
            
            # Draw wireframe sphere
            ax.plot_wireframe(x_sphere, y_sphere, z_sphere, 
                             color=self.color, alpha=0.4, linewidth=1.5,
                             label=self.label)
            
            # Mark center
            ax.scatter(cx, cy, cz, c=self.color, s=80, marker='+', linewidths=4)
            
            # Add center label
            ax.text(cx, cy, cz, 
                   f'  Tâm {self.group_name}({cx}, {cy}, {cz})\n  R={radius}',
                   fontsize=8, color=self.color, fontweight='bold')
            
            # Adjust 3D axis limits
            self.safe_set_axis_limits(ax, center, radius, is_3d=True)
            
            return True
            
        except Exception as e:
            print(f'Error rendering sphere {self.group_name}: {e}')
            return False
    
    def get_bounding_box(self, data: Dict) -> List[float]:
        """Get bounding box [xmin, xmax, ymin, ymax, zmin, zmax] for the sphere"""
        if not self.can_render(data):
            return []
        
        try:
            center = self.parse_coordinates(data.get('sphere_center', ''), 3)
            radius = self.parse_single_value(data.get('sphere_radius', ''))
            
            if center and radius:
                cx, cy, cz = center[0], center[1], center[2]
                return [cx - radius, cx + radius, cy - radius, cy + radius, cz - radius, cz + radius]
        except:
            pass
        
        return []
