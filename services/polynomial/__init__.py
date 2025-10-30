"""Polynomial Services Package
Contains all polynomial-related services and utilities
"""

from .polynomial_solver import PolynomialSolver, PolynomialValidationError, PolynomialSolvingError
from .polynomial_service import PolynomialService, PolynomialServiceError
from .polynomial_template_generator import PolynomialTemplateGenerator
from .polynomial_prefix_resolver import PolynomialPrefixResolver

__all__ = [
    'PolynomialSolver',
    'PolynomialService', 
    'PolynomialTemplateGenerator',
    'PolynomialPrefixResolver',
    'PolynomialValidationError',
    'PolynomialSolvingError',
    'PolynomialServiceError'
]

__version__ = '2.1.0'
__author__ = 'ConvertKeylogApp Team'
