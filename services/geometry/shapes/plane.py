"""
Plane renderer for 3D coordinate plotting
Renderer cho mặt phẳng trong hệ tọa độ 3D
"""

from .base_shape import BaseShapeRenderer
from typing import Dict, List
import numpy as np

class PlaneRenderer(BaseShapeRenderer):
    """Renderer for planes in 3D coordinate system"""
    
    def get_shape_name(self) -> str:
        return "Mặt phẳng"
    
    def can_render(self, data: Dict) -> bool:
        """Check if plane data is valid for rendering"""
        # Check all coefficients are present and parseable
        coeffs = ['a', 'b', 'c', 'd']
        for coef in coeffs:
            value_str = data.get(f'plane_{coef}', '')
            if self.parse_single_value(value_str) is None:
                return False
        
        # Check that at least one of a, b, c is non-zero
        a = self.parse_single_value(data.get('plane_a', ''))
        b = self.parse_single_value(data.get('plane_b', ''))
        c = self.parse_single_value(data.get('plane_c', ''))
        
        return not (a == 0 and b == 0 and c == 0)
    
    def render(self, ax, data: Dict) -> bool:
        """Render plane on 3D matplotlib axis"""
        if not self.can_render(data):
            return False
        
        try:
            # Parse plane coefficients: ax + by + cz + d = 0
            a = self.parse_single_value(data.get('plane_a', ''))
            b = self.parse_single_value(data.get('plane_b', ''))
            c = self.parse_single_value(data.get('plane_c', ''))
            d = self.parse_single_value(data.get('plane_d', ''))
            
            # Create mesh grid
            range_size = 8
            xx, yy = np.meshgrid(np.linspace(-range_size, range_size, 15), 
                                np.linspace(-range_size, range_size, 15))
            
            # Calculate z values based on plane equation
            if abs(c) > 1e-10:  # c != 0
                zz = (-a * xx - b * yy - d) / c
            elif abs(b) > 1e-10:  # b != 0, c = 0
                zz = (-a * xx - c * yy - d) / b  # Actually should be yy calculation
                # For vertical plane parallel to z-axis
                xx, zz = np.meshgrid(np.linspace(-range_size, range_size, 15),
                                    np.linspace(-range_size, range_size, 15))
                yy = (-a * xx - c * zz - d) / b
            elif abs(a) > 1e-10:  # a != 0, b = c = 0
                # Plane parallel to yz-plane
                yy, zz = np.meshgrid(np.linspace(-range_size, range_size, 15),
                                    np.linspace(-range_size, range_size, 15))
                xx = (-b * yy - c * zz - d) / a
            else:
                return False
            
            # Draw plane surface
            ax.plot_surface(xx, yy, zz, alpha=0.3, color=self.color,
                           label=self.label, edgecolor=self.color, linewidth=0.5)
            
            # Add equation label at origin or center point
            try:
                center_x, center_y, center_z = 0, 0, 0
                if abs(c) > 1e-10:
                    center_z = (-a * center_x - b * center_y - d) / c
                
                ax.text(center_x, center_y, center_z,
                       f'  {self.group_name}: {a}x+{b}y+{c}z+{d}=0',
                       fontsize=8, color=self.color, fontweight='bold')
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f'Error rendering plane {self.group_name}: {e}')
            return False
