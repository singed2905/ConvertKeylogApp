"""Polynomial Solver - Core engine for solving polynomial equations of degree 2, 3, 4
Supports both numerical (NumPy) and analytical methods with expression parsing
"""
import math
import numpy as np
from typing import List, Tuple, Union, Optional
import cmath

class PolynomialSolver:
    def __init__(self):
        self.precision = 6  # Decimal places for display
        self.zero_threshold = 1e-12  # Consider as zero
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
    
    # ========== EXPRESSION PARSING ==========
    def parse_expression(self, expr: str) -> float:
        """Parse mathematical expression to float, similar to equation mode"""
        if not expr or not expr.strip():
            return 0.0
        
        expr = str(expr).strip()
        
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
        import re
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
        Main interface to solve polynomial
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
            
            # Format display
            display = self._format_roots_display(roots, degree)
            
            return True, "Success", roots, display
            
        except Exception as e:
            return False, f"Solving error: {str(e)}", [], ""
    
    # ========== NUMPY SOLVER ==========
    def _solve_numpy(self, coeffs: List[float]) -> List[complex]:
        """Solve using NumPy roots function - universal for all degrees"""
        try:
            # NumPy expects coefficients in descending degree order
            roots = np.roots(coeffs)
            
            # Clean up numerical noise  
            cleaned_roots = []
            for root in roots:
                # Clean real part
                real_part = root.real if abs(root.real) > self.zero_threshold else 0.0
                # Clean imaginary part
                imag_part = root.imag if abs(root.imag) > self.zero_threshold else 0.0
                
                cleaned_roots.append(complex(real_part, imag_part))
            
            return cleaned_roots
            
        except Exception as e:
            print(f"NumPy solver error: {e}")
            return []
    
    # ========== ANALYTICAL SOLVERS ==========
    def _solve_analytical(self, coeffs: List[float], degree: int) -> List[complex]:
        """Solve using analytical formulas"""
        if degree == 2:
            return self._solve_quadratic_analytical(coeffs)
        elif degree == 3:
            return self._solve_cubic_analytical(coeffs)
        elif degree == 4:
            return self._solve_quartic_analytical(coeffs)
        else:
            # Fallback to numpy for higher degrees
            return self._solve_numpy(coeffs)
    
    def _solve_quadratic_analytical(self, coeffs: List[float]) -> List[complex]:
        """Solve ax² + bx + c = 0 using quadratic formula"""
        a, b, c = coeffs[0], coeffs[1], coeffs[2]
        
        discriminant = b*b - 4*a*c
        
        if discriminant >= 0:
            # Real roots
            sqrt_d = math.sqrt(discriminant)
            root1 = (-b + sqrt_d) / (2*a)
            root2 = (-b - sqrt_d) / (2*a)
            return [complex(root1, 0), complex(root2, 0)]
        else:
            # Complex roots  
            sqrt_d = math.sqrt(-discriminant)
            real_part = -b / (2*a)
            imag_part = sqrt_d / (2*a)
            return [complex(real_part, imag_part), complex(real_part, -imag_part)]
    
    def _solve_cubic_analytical(self, coeffs: List[float]) -> List[complex]:
        """Solve ax³ + bx² + cx + d = 0 using Cardano's method"""
        a, b, c, d = coeffs[0], coeffs[1], coeffs[2], coeffs[3]
        
        # Convert to depressed cubic t³ + pt + q = 0
        p = (3*a*c - b*b) / (3*a*a)
        q = (2*b*b*b - 9*a*b*c + 27*a*a*d) / (27*a*a*a)
        
        # Cardano's discriminant
        discriminant = -(4*p*p*p + 27*q*q)
        
        if discriminant > 0:
            # Three distinct real roots (casus irreducibilis)
            m = 2 * math.sqrt(-p/3)
            theta = (1/3) * math.acos(3*q/p * math.sqrt(-3/p))
            
            t1 = m * math.cos(theta)
            t2 = m * math.cos(theta - 2*math.pi/3)
            t3 = m * math.cos(theta - 4*math.pi/3)
        elif discriminant == 0:
            # Multiple roots
            if abs(p) < self.zero_threshold:  # p = 0
                t1 = t2 = t3 = 0
            else:
                t1 = 3*q/p
                t2 = t3 = -3*q/(2*p)
        else:
            # One real root, two complex conjugates
            sqrt_disc = math.sqrt(-discriminant/108)
            u = (-q/2 + sqrt_disc)**(1/3) if (-q/2 + sqrt_disc) >= 0 else -(abs(-q/2 + sqrt_disc)**(1/3))
            v = (-q/2 - sqrt_disc)**(1/3) if (-q/2 - sqrt_disc) >= 0 else -(abs(-q/2 - sqrt_disc)**(1/3))
            
            t1 = u + v
            real_part = -(u + v)/2
            imag_part = (u - v) * math.sqrt(3)/2
            t2 = complex(real_part, imag_part)
            t3 = complex(real_part, -imag_part)
        
        # Convert back to original variable: x = t - b/(3a)
        offset = -b / (3*a)
        
        if discriminant >= 0:
            return [complex(t1 + offset, 0), complex(t2 + offset, 0), complex(t3 + offset, 0)]
        else:
            return [complex(t1 + offset, 0), t2 + offset, t3 + offset]
    
    def _solve_quartic_analytical(self, coeffs: List[float]) -> List[complex]:
        """Solve ax⁴ + bx³ + cx² + dx + e = 0 using Ferrari's method"""
        # Ferrari's method is very complex - for MVP, use NumPy
        # TODO: Implement analytical quartic solver if needed for precision
        return self._solve_numpy(coeffs)
    
    # ========== OUTPUT FORMATTING ==========
    def _format_roots_display(self, roots: List[complex], degree: int) -> str:
        """Format roots for display in UI"""
        if not roots:
            return "Không tìm thấy nghiệm"
        
        lines = []
        lines.append(f"Phương trình bậc {degree} có {len(roots)} nghiệm:")
        lines.append("=" * 50)
        
        for i, root in enumerate(roots, 1):
            formatted_root = self._format_single_root(root)
            lines.append(f"x_{i} = {formatted_root}")
        
        lines.append("=" * 50)
        
        # Statistics
        real_count = sum(1 for r in roots if abs(r.imag) < self.zero_threshold)
        complex_count = len(roots) - real_count
        
        if complex_count > 0:
            lines.append(f"Thống kê: {real_count} nghiệm thực, {complex_count} nghiệm phức")
        else:
            lines.append(f"Tất cả {real_count} nghiệm đều là số thực")
        
        return "\n".join(lines)
    
    def _format_single_root(self, root: complex) -> str:
        """Format a single complex number as root"""
        real = root.real
        imag = root.imag
        
        # Check if essentially real
        if abs(imag) < self.zero_threshold:
            # Real root
            if abs(real - round(real)) < self.zero_threshold:
                return str(int(round(real)))  # Integer
            else:
                return f"{real:.{self.precision}f}"
        
        # Complex root
        real_str = f"{real:.{self.precision}f}" if abs(real) > self.zero_threshold else "0"
        
        if abs(imag - round(imag)) < self.zero_threshold:
            imag_str = str(int(round(imag)))
        else:
            imag_str = f"{imag:.{self.precision}f}"
        
        if imag > 0:
            return f"{real_str} + {imag_str}i"
        else:
            return f"{real_str} - {abs(imag):.{self.precision}f}i"
    
    # ========== UTILITY METHODS ==========
    def get_real_roots_only(self, roots: List[complex]) -> List[float]:
        """Extract only real roots from solution"""
        real_roots = []
        for root in roots:
            if abs(root.imag) < self.zero_threshold:
                real_roots.append(root.real)
        return real_roots
    
    def get_polynomial_info(self, coeffs: List[float], degree: int) -> dict:
        """Get additional polynomial information"""
        info = {
            "degree": degree,
            "leading_coefficient": coeffs[0],
            "constant_term": coeffs[-1],
            "is_monic": abs(coeffs[0] - 1.0) < self.zero_threshold,
        }
        
        # Discriminant for degree 2
        if degree == 2:
            a, b, c = coeffs[0], coeffs[1], coeffs[2]
            discriminant = b*b - 4*a*c
            info["discriminant"] = discriminant
            if discriminant > 0:
                info["root_type"] = "two_distinct_real"
            elif discriminant == 0:
                info["root_type"] = "one_repeated_real" 
            else:
                info["root_type"] = "two_complex_conjugate"
        
        return info


class PolynomialValidationError(Exception):
    """Custom exception for polynomial validation errors"""
    pass


class PolynomialSolvingError(Exception):
    """Custom exception for polynomial solving errors"""
    pass


# ========== TESTING UTILITIES ==========
if __name__ == "__main__":
    solver = PolynomialSolver()
    
    # Test quadratic: x² - 5x + 6 = 0 (roots: 2, 3)
    print("=== TEST QUADRATIC ===")
    success, msg, roots, display = solver.solve_polynomial(["1", "-5", "6"], 2)
    print(f"Success: {success}")
    print(f"Message: {msg}")  
    print(f"Display:\n{display}")
    
    # Test with expressions: x² - sqrt(4)x + sin(pi/2) = 0
    print("\n=== TEST WITH EXPRESSIONS ===")
    success, msg, roots, display = solver.solve_polynomial(["1", "-sqrt(4)", "sin(pi/2)"], 2)
    print(f"Success: {success}")
    print(f"Display:\n{display}")
    
    # Test cubic: x³ - 6x² + 11x - 6 = 0 (roots: 1, 2, 3)
    print("\n=== TEST CUBIC ===")
    success, msg, roots, display = solver.solve_polynomial(["1", "-6", "11", "-6"], 3)
    print(f"Success: {success}")
    print(f"Display:\n{display}")
    
    # Test complex roots: x² + 1 = 0
    print("\n=== TEST COMPLEX ROOTS ===")
    success, msg, roots, display = solver.solve_polynomial(["1", "0", "1"], 2)
    print(f"Success: {success}")
    print(f"Display:\n{display}")