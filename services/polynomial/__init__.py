"""Polynomial Services Package
Contains all polynomial-related services and utilities
"""

from .polynomial_solver import PolynomialSolver, PolynomialValidationError, PolynomialSolvingError
from .polynomial_service import PolynomialService, PolynomialServiceError

__all__ = [
    'PolynomialSolver',
    'PolynomialService', 
    'PolynomialValidationError',
    'PolynomialSolvingError',
    'PolynomialServiceError'
]

__version__ = '2.0.0'
__author__ = 'ConvertKeylogApp Team'
