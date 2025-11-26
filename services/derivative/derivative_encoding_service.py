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
        """
        Extract derivative components from LaTeX expression.
        FIXED: Now handles nested braces in eval_value (e.g., x=\frac{a}{b})
        """
        # Find derivative notation: \frac{d^n}{dx^n} or \frac{d}{dx}
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

            # ===== FIXED: Extract expression (first {...}) with brace counting =====
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

                # ===== FIXED: Extract eval part (second {...}) with brace counting =====
                if remaining.startswith('{'):
                    brace_count = 0
                    start_idx = 1
                    end_idx = start_idx

                    # Count braces to find the matching closing brace
                    for i, char in enumerate(remaining[start_idx:], start=start_idx):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            if brace_count == 0:
                                end_idx = i
                                break
                            brace_count -= 1

                    eval_content = remaining[start_idx:end_idx]

                    # Check if format is "variable=value" (e.g., x=\frac{a}{b})
                    eval_match = re.match(r'^([a-zA-Z])=(.+)$', eval_content)
                    if eval_match:
                        eval_var = eval_match.group(1)
                        eval_value = eval_match.group(2)
                    else:
                        # No variable prefix, just value (e.g., {\frac{a}{b}})
                        eval_var = None
                        eval_value = eval_content

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

    def encode_derivative(self, latex_expr: str, mode: str = "1", debug: bool = False) -> Dict[str, Any]:

        try:
            if debug:
                print("\n" + "="*80)
                print("🔍 DEBUG: Starting encode_derivative()")
                print("="*80)
                print(f"📥 INPUT LaTeX: {latex_expr}")
                print(f"📋 Mode: {mode}")

            # Xử lý dạng sách giáo khoa \frac{d}{dx}(...) \big|_{x=...}
            ltx = latex_expr.replace(" ", "")
            if debug:
                print(f"\n1️⃣ After removing spaces: {ltx}")

            pattern = re.compile(
                r'^(\\frac\{d\}\{d[a-zA-Z]+\})\((.*)\)\\big\|_\{([a-zA-Z]=.*)\}\}?$'
            )
            m = pattern.match(ltx)
            if m:
                deriv_part = m.group(1)
                expression = m.group(2)
                eval_part = m.group(3)
                latex_expr = f"{deriv_part}{{{expression}}}{{{eval_part}}}"
                if debug:
                    print(f"📖 Detected textbook format!")
                    print(f"   Derivative part: {deriv_part}")
                    print(f"   Expression: {expression}")
                    print(f"   Eval part: {eval_part}")
                    print(f"   Converted to: {latex_expr}")

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
            if debug:
                print(f"✅ LaTeX validation passed")

            # Preprocessing
            if debug:
                print(f"\n2️⃣ Preprocessing LaTeX...")
            processed_latex = self._preprocess_derivative_latex(latex_expr)
            if debug:
                print(f"   Before: {latex_expr}")
                print(f"   After:  {processed_latex}")

            # Extract components
            if debug:
                print(f"\n3️⃣ Extracting components...")
            components = self._extract_components_from_pattern(processed_latex)

            if debug:
                print(f"   📊 Components extracted:")
                print(f"      - Order: {components['order']}")
                print(f"      - Variable: {components['variable']}")
                print(f"      - Expression: '{components['expression']}'")
                print(f"      - Eval var: {components['eval_var']}")
                print(f"      - Eval value: '{components['eval_value']}'")

            derivative_order = components['order']
            variable = components['variable']
            expression = components['expression']
            eval_var = components['eval_var']
            eval_value = components['eval_value']

            # Encode expression
            if debug:
                print(f"\n4️⃣ Encoding expression...")
                print(f"   📝 Expression (raw): '{expression}'")

            if expression:
                expr_encoded = self.encoder.encode(expression)
                if debug:
                    print(f"   🔐 Expression (encoded): '{expr_encoded}'")
            else:
                expr_encoded = ""
                if debug:
                    print(f"   ⚠️  No expression to encode")

            # Build keylog
            prefix = "qw13qy"
            if debug:
                print(f"\n5️⃣ Building keylog...")
                print(f"   🏷️  Prefix: {prefix}")

            if eval_value:
                if debug:
                    print(f"   📊 Processing evaluation value...")
                    print(f"      Raw eval_value: '{eval_value}'")

                # Cleanup
                eval_value = eval_value.replace(' ', '')
                if debug:
                    print(f"      After space removal: '{eval_value}'")

                eval_value = eval_value.replace(r'\times', r'\cdot')
                if debug:
                    print(f"      After \\times → \\cdot: '{eval_value}'")

                # Encode eval_value
                if debug:
                    print(f"   🔐 Encoding eval_value...")
                eval_value_encoded = self.encoder.encode(eval_value)
                if debug:
                    print(f"      Eval value (encoded): '{eval_value_encoded}'")

                # Build keylog with evaluation
                keylog = f"{prefix}({expr_encoded})q)({eval_value_encoded}))"+"="+" "
                if debug:
                    print(f"   ✅ Keylog format: PREFIX(expr)q)(eval))= ")

            else:
                if debug:
                    print(f"   ⚠️  No evaluation value")
                keylog = f"{prefix}({expr_encoded})"
                if debug:
                    print(f"   ✅ Keylog format: PREFIX(expr)")

            # Final output
            if debug:
                print(f"\n6️⃣ FINAL KEYLOG:")
                print(f"   📤 {keylog}")
                print("="*80)

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
            if debug:
                print(f"\n❌ EXCEPTION CAUGHT: {type(e).__name__}")
                print(f"   Message: {str(e)}")
                import traceback
                print(f"   Traceback:")
                traceback.print_exc()

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
    print("DERIVATIVE ENCODING SERVICE - DEBUG TEST")
    print("=" * 80)

    service = DerivativeEncodingService()

    if not service.is_available():
        print("❌ Service not available")
        exit(1)

    # Test case bị lỗi
    print("\n\n🔴 TEST CASE: LaTeX with fraction in eval_value")
    latex = r"\frac{d}{dx}{x^2}{x=\frac{a}{b}}"
    print(f"Expected keylog: qw13qy([^2))q)((a)a(b)))= ")
    print(f"Actual output:")

    result = service.encode_derivative(latex, debug=True)

    if result['success']:
        print(f"\n✅ Success!")
        print(f"Keylog: {result['keylog']}")

        # Compare
        expected = "qw13qy([^2))q)((a)a(b)))="
        actual = result['keylog'].strip()

        if actual == expected:
            print(f"🎉 MATCH! Output is correct!")
        else:
            print(f"❌ MISMATCH!")
            print(f"Expected: {expected}")
            print(f"Actual:   {actual}")
    else:
        print(f"❌ Error: {result['error']}")
