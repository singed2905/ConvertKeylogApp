"""
Base shape renderer class - Abstract base for all geometric shape renderers
Class cơ sở cho tất cả các renderer hình học
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
import numpy as np

class BaseShapeRenderer(ABC):
    """Abstract base class for all shape renderers"""
    
    def __init__(self, color: str = "blue", group_name: str = "A"):
        self.color = color
        self.group_name = group_name
        self.label = f"{self.get_shape_name()} {group_name}"
    
    @abstractmethod
    def get_shape_name(self) -> str:
        """Return Vietnamese name of the shape"""
        pass
    
    @abstractmethod
    def can_render(self, data: Dict) -> bool:
        """Check if data is valid for rendering this shape"""
        pass
    
    @abstractmethod
    def render(self, ax, data: Dict) -> bool:
        """Render shape on matplotlib axis, return True if successful"""
        pass
    
    def parse_coordinates(self, coord_str: str, expected_dims: int) -> List[float]:
        """Parse coordinate string like '1,2,3' to [1.0, 2.0, 3.0]"""
        if not coord_str or not coord_str.strip():
            return []
        
        try:
            # Handle Vietnamese decimal comma format
            coord_str = str(coord_str).strip()
            parts = coord_str.split(',')
            
            coords = []
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                # Convert Vietnamese comma decimal to dot
                if part.count('.') == 0 and part.count(',') == 1:
                    # This might be decimal comma like "3,5" -> "3.5"
                    pass  # Keep as is, will be handled below
                part = part.replace(',', '.')
                coords.append(float(part))
            
            # Return only expected dimensions
            if len(coords) >= expected_dims:
                return coords[:expected_dims]
            else:
                return []
                
        except (ValueError, IndexError) as e:
            print(f"Warning: Could not parse coordinates '{coord_str}': {e}")
            return []
    
    def parse_single_value(self, value_str: str) -> Optional[float]:
        """Parse single numeric value (for radius, coefficients, etc.)"""
        if not value_str or not str(value_str).strip():
            return None
        
        try:
            # Handle Vietnamese decimal comma
            value_str = str(value_str).strip().replace(',', '.')
            return float(value_str)
        except ValueError as e:
            print(f"Warning: Could not parse value '{value_str}': {e}")
            return None
    
    def validate_positive_value(self, value_str: str) -> bool:
        """Check if value is a positive number"""
        value = self.parse_single_value(value_str)
        return value is not None and value > 0
    
    def safe_set_axis_limits(self, ax, center: List[float], radius: float, is_3d: bool = False):
        """Safely set axis limits to include shape with padding"""
        try:
            pad = max(1.0, radius * 0.2)
            
            if is_3d and len(center) >= 3:
                # 3D limits
                cx, cy, cz = center[:3]
                ax.set_xlim(cx - radius - pad, cx + radius + pad)
                ax.set_ylim(cy - radius - pad, cy + radius + pad)
                ax.set_zlim(cz - radius - pad, cz + radius + pad)
            elif len(center) >= 2:
                # 2D limits
                cx, cy = center[:2]
                current_xlim = ax.get_xlim()
                current_ylim = ax.get_ylim()
                
                new_xlim = [min(current_xlim[0], cx - radius - pad),
                           max(current_xlim[1], cx + radius + pad)]
                new_ylim = [min(current_ylim[0], cy - radius - pad),
                           max(current_ylim[1], cy + radius + pad)]
                
                ax.set_xlim(new_xlim)
                ax.set_ylim(new_ylim)
                ax.set_aspect('equal', adjustable='box')
                
        except Exception as e:
            print(f"Warning: Could not set axis limits: {e}")
    
    def add_coordinate_label(self, ax, coords: List[float], offset: Tuple[int, int] = (5, 5), is_3d: bool = False):
        """Add coordinate label at specified position"""
        try:
            if is_3d and len(coords) >= 3:
                coord_text = f"  {self.group_name}({coords[0]}, {coords[1]}, {coords[2]})"
                ax.text(coords[0], coords[1], coords[2], coord_text,
                       fontsize=9, color=self.color, fontweight='bold')
            elif len(coords) >= 2:
                coord_text = f"{self.group_name}({coords[0]}, {coords[1]})"
                ax.annotate(coord_text, (coords[0], coords[1]),
                           xytext=offset, textcoords='offset points',
                           fontsize=9, color=self.color, fontweight='bold')
        except Exception as e:
            print(f"Warning: Could not add coordinate label: {e}")
