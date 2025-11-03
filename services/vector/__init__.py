"""Vector Services Package
Provides vector calculation and keylog encoding services
"""

from .vector_service import VectorService, VectorServiceError, VectorValidationError
from .vector_mapping_adapter import VectorMappingAdapter

__all__ = [
    'VectorService',
    'VectorMappingAdapter', 
    'VectorServiceError',
    'VectorValidationError'
]

# Package metadata
__version__ = '1.0.0'
__author__ = 'ConvertKeylogApp Team'
__description__ = 'Vector calculation and encoding services for calculator keylog generation'