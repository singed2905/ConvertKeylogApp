"""Derivative Encoding Service - Mã hóa LaTeX đạo hàm sang keylog

Format mới (simplified):
  qv[n]{expression},{variable=value})
  
Ví dụ:
  qv{2K3[^2)p5K2[p7K4},{[=3K2})     # Đạo hàm bậc 1
  qv2{[^3)p2[},{[=1})               # Đạo hàm bậc 2
  qv{[^2)p1})                      # Không có evaluation
"""
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

    def _extract_components_from_pattern(self, latex_expr: str) -> Dict[str, Any]:
        """
        Extract components from new pattern: \\frac{d}{dx}{expression}{x=value}
        
        Returns:
            {
                'order': 1,
                'variable': 'x',
                'expression': '2\\cdot10^{3}x^{2} + ...',
                'eval_var': 'x',
                'eval_value': '3\\cdot10^{2}'
            }
        """
        # Extract derivative operator: \frac{d^n}{dx^n}
        deriv_match = re.search(
            r'\\frac\{d(?:\^(\d+))?\}\{d([a-z])(?:\^\d+)?\}',
            latex_expr
        )
        
        if deriv_match:
            order = int(deriv_match.group(1)) if deriv_match.group(1) else 1
            variable = deriv_match.group(2)
        else:
            order = 1
            variable = 'x'
        
        # Extract expression from {expression} pattern
        expr_match = re.search(r'\}\{([^}]+)\}\{', latex_expr)
        if expr_match:
            expression = expr_match.group(1)
        else:
            # Fallback: try to get content between first } and last {
            parts = latex_expr.split('}')
            if len(parts) > 2:
                expression = parts[1].strip('{').strip()
            else:
                expression = ""
        
        # Extract evaluation: {x=value}
        eval_match = re.search(r'\}\{([a-z])=([^}]+)\}', latex_expr)
        if eval_match:
            eval_var = eval_match.group(1)
            eval_value = eval_match.group(2)
        else:
            eval_var = None
            eval_value = None
        
        return {
            'order': order,
            'variable': variable,
            'expression': expression,
            'eval_var': eval_var,
            'eval_value': eval_value
        }

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
        result = re.sub(
            r'([a-zA-Z]+)\'\(([a-z])\)',
            r'\\frac{d\1}{d\2}',
            result
        )
        
        # Convert f''(x) → \frac{d^2f}{dx^2}
        result = re.sub(
            r'([a-zA-Z]+)\'\'\'\(([a-z])\)',
            r'\\frac{d^3\1}{d\2^3}',
            result
        )
        result = re.sub(
            r'([a-zA-Z]+)\'\'\(([a-z])\)',
            r'\\frac{d^2\1}{d\2^2}',
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
        Encode derivative LaTeX to simplified keylog format.
        
        New Format: qv[n]{expression},{variable=value})
        
        Args:
            latex_expr: LaTeX derivative expression
                Pattern: \\frac{d}{dx}{f(x)}{x=a}
            mode: Encoding mode (currently only "1" uses qv prefix)
            
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

            # Preprocess: Convert other notations to Leibniz
            processed_latex = self._preprocess_derivative_latex(latex_expr)
            
            # Extract components using new pattern
            components = self._extract_components_from_pattern(processed_latex)
            
            derivative_order = components['order']
            variable = components['variable']
            expression = components['expression']
            eval_var = components['eval_var']
            eval_value = components['eval_value']

            # Encode expression using LatexToKeylogEncoder
            if expression:
                expr_encoded = self.encoder.encode(expression)
            else:
                expr_encoded = ""
            
            # Encode evaluation value if present
            if eval_value:
                eval_encoded = self.encoder.encode(eval_value)
                # Replace variable with encoded variable
                eval_var_encoded = variable.replace('x', '[').replace('t', '[')
            else:
                eval_encoded = None
                eval_var_encoded = None

            # Build keylog in new format: qv[n]{expression},{variable=value})
            # Determine prefix based on order
            if derivative_order == 1:
                prefix = "qv"  # First derivative
            else:
                prefix = f"qv{derivative_order}"  # nth derivative
            
            # Assemble keylog
            if eval_encoded:
                keylog = f"{prefix}{{{expr_encoded}}},{{{eval_var_encoded}={eval_encoded}}})"
            else:
                keylog = f"{prefix}{{{expr_encoded}}})"

            return {
                'success': True,
                'keylog': keylog,
                'latex_input': latex_expr,
                'processed_latex': processed_latex,
                'derivative_order': derivative_order,
                'function': expression,
                'variable': variable,
                'mode': mode,
                'format': 'simplified',
                'pattern': f"qv[{derivative_order}]{{expr}},{{var=val}})"
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
                components = self._extract_components_from_pattern(processed)
                order = components['order']
                func = components['expression']
                var = components['variable']
            else:
                order = 0
                func = ''
                var = ''

            return {
                'valid': is_derivative,
                'is_derivative': is_derivative,
                'derivative_order': order,
                'function': func,
                'variable': var,
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
    print("DERIVATIVE ENCODING SERVICE - TEST (Simplified Format)")
    print("=" * 80)
    print()

    service = DerivativeEncodingService()

    if not service.is_available():
        print("❌ Service not available")
        exit(1)

    print("✅ Service initialized successfully")
    print(f"  - Mapping rules: {len(service.encoder.mappings)}")
    print(f"  - New format: qv[n]{{expr}},{{x=val}})")
    print()

    test_cases = [
        (r"\frac{d}{dx}{x^2}{x=3}", "Simple polynomial"),
        (r"\frac{d}{dx}{2\cdot10^{3}x^{2} + 5\cdot10^{2}x + 7\cdot10^{4}}{x=3\cdot10^{2}}", 
         "Scientific notation"),
        (r"\frac{d^2}{dx^2}{x^3}{x=2}", "Second derivative"),
        (r"\frac{d}{dx}{e^{2x}}{x=0}", "Exponential"),
        (r"\frac{d}{dx}{\sin(x)}{x=\frac{\pi}{4}}", "Trigonometric"),
        (r"\frac{d}{dx}{x^2 + 1}{}", "No evaluation"),
    ]

    for latex, desc in test_cases:
        print(f"--- {desc} ---")
        print(f"LaTeX: {latex}")

        result = service.encode_derivative(latex, "1")
        if result['success']:
            print(f"Order: {result['derivative_order']}")
            print(f"Keylog: {result['keylog']}")
            print(f"Pattern: {result['pattern']}")
        else:
            print(f"ERROR: {result['error']}")

        print()

    print("=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
