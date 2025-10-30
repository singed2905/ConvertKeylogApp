"""Services package for ConvertKeylogApp v2.0

Contains business logic for different modes:
- Geometry: Complete geometry processing with Excel integration
- Equation: Linear equation system solving with keylog encoding  
- Excel: Common Excel processing utilities
"""

# Import services
try:
    from .geometry.geometry_service import GeometryService
except ImportError:
    print("Warning: GeometryService not available")
    GeometryService = None

try:
    from .equation.equation_service import EquationService
except ImportError:
    print("Warning: EquationService not available")
    EquationService = None

try:
    from .excel.excel_processor import ExcelProcessor
except ImportError:
    print("Warning: ExcelProcessor not available")
    ExcelProcessor = None

__all__ = [
    'GeometryService',
    'EquationService', 
    'ExcelProcessor'
]

__version__ = '2.0.0'
__description__ = 'Business logic services for ConvertKeylogApp'