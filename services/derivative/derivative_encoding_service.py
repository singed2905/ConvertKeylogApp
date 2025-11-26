"""Derivative Encoding Service - Mã hóa LaTeX đạo hàm sang keylog

Format mới (simplified - no curly braces):
  qv(expression),(value)

Ví dụ:
  qv(2K3[^2)p5K2[p7K4),(3K2)     # Đạo hàm bậc 1 với eval (không có x=)
  qv([^2)p1)                     # Không có evaluation
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
        leibniz_match = re.search(r'd\^(\d+)', latex_expr)
        if leibniz_match:
            return int(leibniz_match.group(1))
        prime_count = latex_expr.count("'")
        if prime_count > 0:
            return prime_count
        return 1

    def _extract_components_from_pattern(self, latex_expr: str) -> Dict[str, Any]:
        deriv_match = re.search(
            r'\\frac\{d(?:\^(\d+))?\}\{d([a-z])(?:\^\d+)?\}',
            latex_expr
        )
        if deriv_match:
            order = int(deriv_match.group(1)) if deriv_match.group(1) else 1
            variable = deriv_match.group(2)
            deriv_end = deriv_match.end()
        else:
            order = 1
            variable = 'x'
            deriv_end = 0

        expression = ""
        eval_var = None
        eval_value = None
        if deriv_end > 0:
            rest = latex_expr[deriv_end:]
            if rest.startswith('{'):
                brace_count = 0
                start_idx = 1
                end_idx = start_idx
                for i, char in enumerate(rest[start_idx:], start=start_idx):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        if brace_count == 0:
                            end_idx = i
                            break
                        brace_count -= 1
                expression = rest[start_idx:end_idx]
                remaining = rest[end_idx+1:]
                eval_match = re.match(r'^\{([a-zA-Z])=([^}]+)\}', remaining)
                if eval_match:
                    eval_var = eval_match.group(1)
                    eval_value = eval_match.group(2)
                else:
                    eval_value_match = re.match(r'^\{([^}]+)\}', remaining)
                    if eval_value_match:
                        eval_var = None
                        eval_value = eval_value_match.group(1)
        return {
            'order': order,
            'variable': variable,
            'expression': expression,
            'eval_var': eval_var,
            'eval_value': eval_value
        }

    def _preprocess_derivative_latex(self, latex_expr: str) -> str:
        result = latex_expr
        result = result.strip()
        if result.startswith('$') and result.endswith('$'):
            result = result[1:-1]
        result = re.sub(
            r'([a-zA-Z]+)\'\(([a-z])\)',
            r'\\frac{d\1}{d\2}',
            result
        )
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
        result = re.sub(
            r'([a-zA-Z])\'(?![a-zA-Z])',
            r'\\frac{d\1}{dx}',
            result
        )
        return result

    def encode_derivative(self, latex_expr: str, mode: str = "1") -> Dict[str, Any]:
        try:
            # Xử lý dạng sách giáo khoa \frac{d}{dx}(...) \big|_{x=...}
            ltx = latex_expr.replace(" ", "")
            pattern = re.compile(
                r'^(\\frac\{d\}\{d[a-zA-Z]+\})\((.*)\)\\big\|_\{([a-zA-Z]=.*)\}\}?$'
            )
            m = pattern.match(ltx)
            if m:
                deriv_part = m.group(1)
                expression = m.group(2)
                eval_part = m.group(3)
                latex_expr = f"{deriv_part}{{{expression}}}{{{eval_part}}}"

            if not self.encoder:
                return {
                    'success': False,
                    'error': 'Missing encoder',
                    'keylog': ""
                }
            valid, error = self.encoder.validate_latex(latex_expr)
            if not valid:
                return {
                    'success': False,
                    'error': f'Invalid LaTeX: {error}',
                    'keylog': "",
                    'latex_input': latex_expr
                }

            processed_latex = self._preprocess_derivative_latex(latex_expr)
            components = self._extract_components_from_pattern(processed_latex)

            derivative_order = components['order']
            variable = components['variable']
            expression = components['expression']
            eval_var = components['eval_var']
            eval_value = components['eval_value']

            expr_encoded = self.encoder.encode(expression) if expression else ""
            prefix = "qy"

            if eval_value:
                eval_value = eval_value.replace(' ', '')
                eval_value = eval_value.replace(r'\times', r'\cdot')
                eval_value_encoded = self.encoder.encode(eval_value)
                # BỎ eval_var, chỉ giữ giá trị mã hóa
                keylog = f"{prefix}({expr_encoded}),({eval_value_encoded}))"+"="+" "
            else:
                keylog = f"{prefix}({expr_encoded})"

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
                'pattern': "qv(expr),(val)"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'keylog': "",
                'latex_input': latex_expr
            }

    def encode_batch(self, latex_exprs: List[str], mode: str = "1") -> List[Dict[str, Any]]:
        return [self.encode_derivative(expr, mode) for expr in latex_exprs]

    def validate_derivative_latex(self, latex_expr: str) -> Dict[str, Any]:
        try:
            valid, error = self.encoder.validate_latex(latex_expr)
            if not valid:
                return {
                    'valid': False,
                    'error': error,
                    'is_derivative': False
                }
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
        return self.encoder is not None


if __name__ == "__main__":
    print("=" * 80)
    print("DERIVATIVE ENCODING SERVICE - TEST (simplified without variable eval)")
    print("=" * 80)
    service = DerivativeEncodingService()

    if not service.is_available():
        print("❌ Service not available")
        exit(1)

    test_cases = [
        (r"\frac{d}{dx}{x^2}{x=6.85\times10^{18}}", "Eval with variable (x=...)"),
        (r"\frac{d}{dx}{x^2}{6.85\times10^{18}}", "Eval without variable"),
        (r"\frac{d}{dx}{x^2}{}", "No eval"),
        (r"\frac{d}{dx}(3.4598 \cdot 10^{58} x^{4} + 2.6937 \cdot 10^{29} x^{3} + 7.9109 \cdot 10^{39} x^{2} - 1.6893 \cdot 10^{17} x + 9.4305 \cdot 10^{95})\big|_{x=6.85 \times 10^{18}}",
         "Textbook style input"),
    ]

    for latex, desc in test_cases:
        print(f"\n--- {desc} ---")
        print(f"LaTeX: {latex}")
        res = service.encode_derivative(latex)
        if res['success']:
            print(f"Keylog: {res['keylog']}")
        else:
            print("Error:", res['error'])
