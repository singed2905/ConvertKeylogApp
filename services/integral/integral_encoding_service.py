"""Integral Encoding Service - Mã hóa LaTeX tích phân sang keylog"""
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


class IntegralEncodingService:

    def __init__(self, mapping_file: str = None):
        try:
            if LatexToKeylogEncoder:
                self.encoder = LatexToKeylogEncoder(
                    mapping_file or "config/equation_mode/mapping.json"
                )
            else:
                raise Exception("LatexToKeylogEncoder not available")

        except Exception as e:
            print(f"Warning: IntegralEncodingService init failed: {e}")
            self.encoder = None

    def _count_nested_integrals(self, latex_expr: str) -> int:
        return latex_expr.count(r"\int")

    def _extract_nested_bounds_and_function(self, latex_expr: str) -> Dict[str, Any]:
        """Extract bounds từ tất cả integrals và extract hàm cuối cùng"""
        integral_pattern = r'\\int\s*_\{([^}]*)\}\s*\^\{([^}]*)\}'
        matches = list(re.finditer(integral_pattern, latex_expr))

        bounds = []
        for match in matches:
            bounds.append({
                'lower': match.group(1),
                'upper': match.group(2)
            })

        last_integral_pos = latex_expr.rfind('\\int')
        if last_integral_pos != -1:
            after_integral = latex_expr[last_integral_pos:]
            func_match = re.search(r'\\int\s*_\{[^}]*\}\s*\^\{[^}]*\}\s*([^\d]*)\s*d', after_integral)
            if func_match:
                function = func_match.group(1).strip()
            else:
                function = ""
        else:
            function = ""

        return {
            'bounds': bounds,
            'function': function
        }

    def _encode_nested_integrals(self, latex_expr: str, mode: str) -> Dict[str, Any]:
        """Xử lý tích phân lồng nhau (nested integrals)"""
        try:
            integral_count = self._count_nested_integrals(latex_expr)

            if integral_count < 2:
                return None

            nested_info = self._extract_nested_bounds_and_function(latex_expr)
            bounds_list = nested_info['bounds']
            function_latex = nested_info['function']

            if not function_latex:
                return None

            function_latex = re.sub(r'\s*d[a-z]\s*', '', function_latex)

            encoded_function = self.encoder.encode(function_latex)

            keylog = f"y{encoded_function}"
            for bound in bounds_list:
                lower_clean = self.encoder._clean_bounds(bound['lower']) if hasattr(self.encoder, '_clean_bounds') else \
                bound['lower']
                upper_clean = self.encoder._clean_bounds(bound['upper']) if hasattr(self.encoder, '_clean_bounds') else \
                bound['upper']
                keylog += f")q){lower_clean}q){upper_clean}"
            keylog += ")"

            if mode in ["1", "2"]:
                keylog = keylog.replace("q)", "$")

            return {
                'success': True,
                'keylog': keylog,
                'is_nested': True,
                'integral_count': integral_count,
                'bounds': bounds_list,
                'mode': mode
            }

        except Exception as e:
            return None

    def encode_integral(self, latex_expr: str, mode: str = "1") -> Dict[str, Any]:
        try:
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

            integral_count = self._count_nested_integrals(latex_expr)

            # Pre-process: loại bỏ \left và \right
            latex_expr = latex_expr.replace(r'\left', '').replace(r'\right', '')

            nested_result = self._encode_nested_integrals(latex_expr, mode)
            if nested_result:
                return nested_result

            keylog = self.encoder.encode(latex_expr)
            keylog = re.sub(r'y\[([^)]*)\)\)([,q])', r'y[\1)\2', keylog)
            if mode in ["1", "2"]:
                keylog = keylog.replace("q)", "$")

            return {
                'success': True,
                'keylog': keylog,
                'latex_input': latex_expr,
                'is_nested': integral_count >= 2,
                'integral_count': integral_count,
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
        return [self.encode_integral(expr, mode) for expr in latex_exprs]

    def validate_integral_latex(self, latex_expr: str) -> Dict[str, Any]:
        try:
            valid, error = self.encoder.validate_latex(latex_expr)
            if not valid:
                return {
                    'valid': False,
                    'error': error,
                    'is_integral': False
                }

            is_integral = '\\int' in latex_expr
            has_bounds = '_{' in latex_expr and '^{' in latex_expr
            has_differential = any(f'd{var}' in latex_expr for var in 'xyztuvabc')
            integral_count = latex_expr.count('\\int')
            is_nested = integral_count >= 2

            return {
                'valid': is_integral,
                'is_integral': is_integral,
                'has_bounds': has_bounds,
                'has_differential': has_differential,
                'integral_count': integral_count,
                'is_nested': is_nested,
                'error': None if is_integral else 'Không phải biểu thức tích phân (thiếu \\int)'
            }

        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'is_integral': False
            }

    def get_encoding_info(self, latex_expr: str, mode: str = "1") -> Dict[str, Any]:
        result = self.encode_integral(latex_expr, mode)

        if result['success']:
            result['mapping_rules_count'] = len(self.encoder.mappings)
            result['encoder_type'] = 'LatexToKeylogEncoder'

        return result

    def is_available(self) -> bool:
        return self.encoder is not None


if __name__ == "__main__":
    print("=" * 80)
    print("INTEGRAL ENCODING SERVICE - TEST (Với Nested Integrals)")
    print("=" * 80)
    print()

    service = IntegralEncodingService()

    if not service.is_available():
        print("❌ Service not available")
        exit(1)

    print("✅ Service initialized successfully")
    print(f"  - Mapping rules: {len(service.encoder.mappings)}")
    print()

    test_cases = [
        (r"\int_{0}^{1} x dx", "Tích phân đơn 1"),
        (r"\int_{0}^{1} x^2 dx", "Tích phân đơn 2"),
        (r"\int_{0}^{1} \int_{0}^{x} xy dydx", "Tích phân kép"),
        (r"\int_{0}^{1} \int_{0}^{1} \int_{0}^{1} xyz dzdydx", "Tích phân bội ba"),
    ]

    for latex, desc in test_cases:
        print(f"--- {desc} ---")
        print(f"LaTeX: {latex}")

        validation = service.validate_integral_latex(latex)
        print(f"Integral count: {validation['integral_count']}, Is nested: {validation['is_nested']}")

        for mode in ["1", "2", "3", "4"]:
            result = service.encode_integral(latex, mode)
            if result['success']:
                nested_info = " [NESTED]" if result.get('is_nested') else ""
                print(f"  Mode {mode}: {result['keylog']}{nested_info}")

        print()

    print("=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
