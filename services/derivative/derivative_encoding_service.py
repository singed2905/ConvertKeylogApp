"""Derivative Encoding Service - Mã hóa LaTeX đạo hàm sang keylog"""
import sys
import os
import re
from typing import Dict, Any, List

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from utils.latex_to_keylog import LatexToKeylogEncoder
except ImportError:
    LatexToKeylogEncoder = None


class DerivativeEncodingService:
    """Service for encoding derivative LaTeX to calculator keylog format"""

    def __init__(self, mapping_file: str = None):
        try:
            if LatexToKeylogEncoder:
                self.encoder = LatexToKeylogEncoder(
                    mapping_file or "config/equation_mode/mapping.json"
                )
            else:
                raise Exception("LatexToKeylogEncoder not available")

        except Exception as e:
            print(f"Warning: DerivativeEncodingService init failed: {e}")
            self.encoder = None

    def _count_derivative_order(self, latex_expr: str) -> int:
        """
        Count derivative order from LaTeX expression.
        
        Examples:
            dy/dx → 1
            d^2y/dx^2 → 2
            f'(x) → 1
            f''(x) → 2
            f'''(x) → 3
        """
        # Check Leibniz notation: d^n
        leibniz_match = re.search(r'd\^(\d+)', latex_expr)
        if leibniz_match:
            return int(leibniz_match.group(1))
        
        # Check Lagrange notation: count primes
        prime_count = latex_expr.count("'")
        if prime_count > 0:
            return prime_count
        
        # Default: first order
        return 1

    def _extract_function_and_variable(self, latex_expr: str) -> Dict[str, str]:
        """
        Extract function and variable from derivative expression.
        
        Examples:
            \\frac{dy}{dx} → {function: 'y', variable: 'x'}
            \\frac{d(x^2)}{dx} → {function: 'x^2', variable: 'x'}
            f'(x) → {function: 'f', variable: 'x'}
        """
        # Leibniz notation: \frac{d(...)}{dx}
        leibniz_match = re.search(r'\\frac\{d(?:\^\d+)?\(?([^}\)]+)\)?\}\{d([a-z])(?:\^\d+)?\}', latex_expr)
        if leibniz_match:
            return {
                'function': leibniz_match.group(1),
                'variable': leibniz_match.group(2)
            }
        
        # Lagrange notation: f'(x)
        lagrange_match = re.search(r'([a-zA-Z]+)\'*\(([a-z])\)', latex_expr)
        if lagrange_match:
            return {
                'function': lagrange_match.group(1),
                'variable': lagrange_match.group(2)
            }
        
        # Default fallback
        return {'function': 'y', 'variable': 'x'}

    def _preprocess_derivative_latex(self, latex_expr: str) -> str:
        """
        Preprocess derivative LaTeX for encoding.
        
        Converts various derivative notations to standardized form:
        - Leibniz: \\frac{dy}{dx} → keep as is
        - Lagrange: f'(x) → \\frac{df}{dx}
        - Prime: y' → \\frac{dy}{dx}
        """
        result = latex_expr
        
        # Remove $ delimiters
        result = result.strip()
        if result.startswith('$') and result.endswith('$'):
            result = result[1:-1]
        
        # Convert Lagrange f'(x) to Leibniz notation
        # f'(x) → \frac{df}{dx}
        result = re.sub(
            r'([a-zA-Z]+)\'\(([a-z])\)',
            r'\\frac{d\1}{d\2}',
            result
        )
        
        # Convert f''(x) → \frac{d^2f}{dx^2}
        result = re.sub(
            r'([a-zA-Z]+)\'\'\(([a-z])\)',
            r'\\frac{d^2\1}{d\2^2}',
            result
        )
        
        # Convert f'''(x) → \frac{d^3f}{dx^3}
        result = re.sub(
            r'([a-zA-Z]+)\'\'\'\(([a-z])\)',
            r'\\frac{d^3\1}{d\2^3}',
            result
        )
        
        # Convert simple y' → \frac{dy}{dx}
        result = re.sub(
            r'([a-zA-Z])\'(?![a-zA-Z])',
            r'\\frac{d\1}{dx}',
            result
        )
        
        return result

    def encode_derivative(self, latex_expr: str, mode: str = "1") -> Dict[str, Any]:
        """
        Encode derivative LaTeX to keylog format.
        
        Args:
            latex_expr: LaTeX derivative expression
            mode: Encoding mode ("1", "2", "3", "4")
            
        Returns:
            Dict with success, keylog, and metadata
        """
        try:
            if not self.encoder:
                return {
                    'success': False,
                    'error': 'Missing encoder',
                    'keylog': ""
                }

            # Validate LaTeX
            valid, error = self.encoder.validate_latex(latex_expr)
            if not valid:
                return {
                    'success': False,
                    'error': f'Invalid LaTeX: {error}',
                    'keylog': "",
                    'latex_input': latex_expr
                }

            # Preprocess: Convert to standardized Leibniz notation
            processed_latex = self._preprocess_derivative_latex(latex_expr)
            
            # Extract metadata
            derivative_order = self._count_derivative_order(processed_latex)
            func_var_info = self._extract_function_and_variable(processed_latex)

            # Remove \left and \right
            processed_latex = processed_latex.replace(r'\left', '').replace(r'\right', '')

            # Main encoding using LatexToKeylogEncoder
            keylog = self.encoder.encode(processed_latex)
            
            # Post-processing: Mode-specific adjustments
            if mode in ["1", "2"]:
                keylog = keylog.replace("q)", "$")

            # Add mode prefix
            mode_prefixes = {
                "1": "qw21",  # Mode 1: Derivative prefix
                "2": "qw22",  # Mode 2: Alternative format
                "3": "qw23",  # Mode 3: Advanced
                "4": "qw24"   # Mode 4: Extended
            }
            prefix = mode_prefixes.get(mode, "")
            if prefix:
                keylog = prefix + keylog

            return {
                'success': True,
                'keylog': keylog,
                'latex_input': latex_expr,
                'processed_latex': processed_latex,
                'derivative_order': derivative_order,
                'function': func_var_info['function'],
                'variable': func_var_info['variable'],
                'mode': mode
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'keylog': "",
                'latex_input': latex_expr
            }

    def encode_batch(self, latex_exprs: List[str], mode: str = "1") -> List[Dict[str, Any]]:
        """Encode multiple derivative expressions"""
        return [self.encode_derivative(expr, mode) for expr in latex_exprs]

    def validate_derivative_latex(self, latex_expr: str) -> Dict[str, Any]:
        """
        Validate derivative LaTeX expression.
        
        Returns dict with validation status and metadata.
        """
        try:
            valid, error = self.encoder.validate_latex(latex_expr)
            if not valid:
                return {
                    'valid': False,
                    'error': error,
                    'is_derivative': False
                }

            # Check if expression is a derivative
            is_derivative = any([
                r'\frac{d' in latex_expr,
                "f'" in latex_expr,
                "y'" in latex_expr,
            ])
            
            if is_derivative:
                processed = self._preprocess_derivative_latex(latex_expr)
                order = self._count_derivative_order(processed)
                func_var = self._extract_function_and_variable(processed)
            else:
                order = 0
                func_var = {'function': '', 'variable': ''}

            return {
                'valid': is_derivative,
                'is_derivative': is_derivative,
                'derivative_order': order,
                'function': func_var['function'],
                'variable': func_var['variable'],
                'error': None if is_derivative else 'Không phải biểu thức đạo hàm (thiếu \\frac{d}{dx} hoặc f\')'
            }

        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'is_derivative': False
            }

    def is_available(self) -> bool:
        """Check if service is available"""
        return self.encoder is not None


if __name__ == "__main__":
    print("=" * 80)
    print("DERIVATIVE ENCODING SERVICE - TEST")
    print("=" * 80)
    print()

    service = DerivativeEncodingService()

    if not service.is_available():
        print("❌ Service not available")
        exit(1)

    print("✅ Service initialized successfully")
    print(f"  - Mapping rules: {len(service.encoder.mappings)}")
    print()

    test_cases = [
        (r"\frac{dy}{dx}", "First order - Leibniz"),
        (r"\frac{d^2y}{dx^2}", "Second order - Leibniz"),
        (r"\frac{d(x^2)}{dx}", "Function x^2"),
        (r"f'(x)", "Lagrange notation"),
        (r"f''(x)", "Second derivative - Lagrange"),
        (r"y'", "Simple prime notation"),
        (r"\frac{d(\sin(x))}{dx}", "Trigonometric function"),
        (r"\frac{d(e^x)}{dx}", "Exponential function"),
    ]

    for latex, desc in test_cases:
        print(f"--- {desc} ---")
        print(f"LaTeX: {latex}")

        validation = service.validate_derivative_latex(latex)
        print(f"Valid: {validation['valid']}, Order: {validation.get('derivative_order', 0)}")

        for mode in ["1", "2", "3", "4"]:
            result = service.encode_derivative(latex, mode)
            if result['success']:
                print(f"  Mode {mode}: {result['keylog']}")
            else:
                print(f"  Mode {mode}: ERROR - {result['error']}")

        print()

    print("=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
