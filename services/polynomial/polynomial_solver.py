"""Polynomial Solver - Enhanced engine for solving polynomial equations of degree 2, 3, 4
Supports both numerical (NumPy) and analytical methods with expression parsing and repeated roots detection
"""
import math
import numpy as np
from typing import List, Tuple, Union, Optional, Dict
import cmath
from collections import Counter
import re  # <-- ADD

class PolynomialSolver:
    def __init__(self):
        self.precision = 6  # Decimal places for display
        self.zero_threshold = 1e-12  # Consider as zero
        self.duplicate_threshold = 1e-8  # Consider as duplicate/repeated root
        self.method = "numpy"  # "numpy" or "analytical"
        
    def set_method(self, method: str):
        """Set solving method: 'numpy' or 'analytical'"""
        if method in ["numpy", "analytical"]:
            self.method = method
        else:
            raise ValueError("Method must be 'numpy' or 'analytical'")
    
    def set_precision(self, precision: int):
        """Set decimal precision for results"""
        self.precision = max(1, min(15, precision))
    
    def set_duplicate_threshold(self, threshold: float):
        """Set threshold for detecting repeated roots"""
        self.duplicate_threshold = max(1e-15, threshold)
    
    # ========== EXPRESSION PARSING ==========
    def parse_expression(self, expr: str) -> float:
        """Parse mathematical expression to float, similar to equation mode. Now supports LaTeX fractions \frac{a}{b}."""
        if not expr or not expr.strip():
            return 0.0
        
        expr = str(expr).strip()
        
        # Handle LaTeX fractions: convert \frac{a}{b} to (a)/(b)
        def replace_frac(match):
            return f"({match.group(1)})/({match.group(2)})"
        expr = re.sub(r"\\\frac\s*\{([^{}]+)\}\{([^{}]+)\}", replace_frac, expr)
        
        # Handle simple numbers first
        try:
            return float(expr)
        except ValueError:
            pass
        
        # Replace mathematical expressions
        replacements = {
            'pi': 'math.pi',
            'e': 'math.e', 
            'sqrt': 'math.sqrt',
            'sin': 'math.sin',
            'cos': 'math.cos', 
            'tan': 'math.tan',
            'log': 'math.log10',  # log = log10
            'ln': 'math.log',     # ln = natural log
            '^': '**',            # power operator
        }
        
        # Apply replacements (word boundaries to avoid partial matches)
        for old, new in replacements.items():
            if old in ['^']:  # Special handling for operators
                expr = expr.replace(old, new)
            else:  # Functions need word boundary
                expr = re.sub(r'\b' + re.escape(old) + r'\b', new, expr)
        
        # Safe evaluation
        try:
            # Restricted environment for security
            safe_dict = {"__builtins__": {}, "math": math}
            result = eval(expr, safe_dict)
            return float(result)
        except Exception:
            try:
                # Fallback: try direct float conversion
                return float(expr)
            except Exception:
                # Ultimate fallback
                return 0.0
    
    def parse_coefficients(self, raw_coeffs: List[str]) -> Tuple[List[float], bool]:
        """Parse list of coefficient expressions to floats"""
        try:
            parsed = [self.parse_expression(coeff) for coeff in raw_coeffs]
            return parsed, True
        except Exception as e:
            print(f"Error parsing coefficients: {e}")
            return [0.0] * len(raw_coeffs), False
    
    # ========== REPEATED ROOTS DETECTION ==========
    def _group_repeated_roots(self, roots: List[complex]) -> List[Tuple[complex, int]]:
        """Group roots by value and return (root, multiplicity) pairs"""
        if not roots:
            return []
        
        # Group roots that are very close to each other
        grouped = []
        remaining = roots.copy()
        
        while remaining:
            current = remaining.pop(0)
            multiplicity = 1
            
            # Find all roots close to current
            i = 0
            while i < len(remaining):
                if abs(remaining[i] - current) < self.duplicate_threshold:
                    multiplicity += 1
                    remaining.pop(i)
                else:
                    i += 1
            
            grouped.append((current, multiplicity))
        
        # Sort by real part, then by imaginary part
        grouped.sort(key=lambda x: (x[0].real, x[0].imag))
        return grouped
    
    def _detect_discriminant_case(self, coeffs: List[float], degree: int) -> Optional[str]:
        """Detect special cases based on discriminant analysis"""
        if degree == 2:
            a, b, c = coeffs[0], coeffs[1], coeffs[2]
            discriminant = b*b - 4*a*c
            
            if abs(discriminant) < self.zero_threshold:
                return "repeated_root"  # Perfect square
            elif discriminant > 0:
                return "two_distinct_real"
            else:
                return "complex_conjugate"
        
        # For higher degrees, discriminant is more complex
        # Can be implemented later if needed
        return None
    
    # ========== VALIDATION ==========
    def validate_polynomial(self, coeffs: List[float], degree: int) -> Tuple[bool, str]:
        """Validate polynomial coefficients"""
        if len(coeffs) != degree + 1:
            return False, f"Need exactly {degree + 1} coefficients for degree {degree} polynomial"
        
        # Leading coefficient cannot be zero
        if abs(coeffs[0]) < self.zero_threshold:
            return False, f"Leading coefficient 'a' cannot be zero for degree {degree} polynomial"
        
        # Check if all coefficients are zero (degenerate case)
        if all(abs(c) < self.zero_threshold for c in coeffs):
            return False, "All coefficients are zero - invalid polynomial"
        
        return True, "Valid polynomial"
    
    # ========== MAIN SOLVING INTERFACE ==========
    def solve_polynomial(self, raw_coeffs: List[str], degree: int) -> Tuple[bool, str, List[complex], str]:
        """
        Main interface to solve polynomial with repeated roots detection
        Returns: (success, status_msg, roots, formatted_display)
        """
        try:
            # Parse coefficients
            coeffs, parse_ok = self.parse_coefficients(raw_coeffs)
            if not parse_ok:
                return False, "Cannot parse coefficients", [], ""
            
            # Validate
            valid, msg = self.validate_polynomial(coeffs, degree)
            if not valid:
                return False, msg, [], ""
            
            # Solve based on method
            if self.method == "analytical":
                roots = self._solve_analytical(coeffs, degree)
            else:  # numpy method (default)
                roots = self._solve_numpy(coeffs)
            
            # Format display with repeated roots handling
            display = self._format_roots_display_enhanced(roots, coeffs, degree)
            
            return True, "Success", roots, display
            
        except Exception as e:
            return False, f"Solving error: {str(e)}", [], ""

    # ... To be continued ...
