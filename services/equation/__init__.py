"""Equation Service Package - TL-Compatible"""

from .equation_service import EquationService
from .mapping_manager import MappingManager 
from .prefix_resolver import EquationPrefixResolver
from .equation_encoding_service import EquationEncodingService

__all__ = [
    'EquationService',
    'MappingManager',
    'EquationPrefixResolver', 
    'EquationEncodingService'
]

__version__ = '2.0.0'
__description__ = 'Linear equation system solving with TL-compatible keylog encoding'
__compatibility__ = 'TL-compatible prefixes and mapping system'