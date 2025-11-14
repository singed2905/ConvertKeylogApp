import json
import os
import re
from typing import List, Dict, Any, Tuple, Optional


class LatexToKeylogEncoder:
    """Utility to encode LaTeX math expressions to calculator keylog format.
    Supports version-based mapping (e.g. fx799, fx991, ...) via mapping JSON.
    Hỗ trợ: phân số, căn, hàm lượng giác, tích phân.
    """

    def __init__(self, mapping_file: str = "config/equation_mode/mapping.json"):
        self.mapping_file = mapping_file
        self.mappings = self._load_mappings()

    def _load_mappings(self) -> List[Dict[str, Any]]:
        """Load mappings from JSON file - thử nhiều relative paths"""
        try:
            # ✅ Thử nhiều đường dẫn relative khác nhau
            possible_paths = [
                self.mapping_file,  # config/equation_mode/mapping.json
                os.path.join("..", self.mapping_file),  # ../config/equation_mode/mapping.json
                os.path.join("..", "..", self.mapping_file),  # ../../config/equation_mode/mapping.json
            ]

            mapping_file_found = None
            for path in possible_paths:
                if os.path.exists(path):
                    mapping_file_found = path
                    break

            if mapping_file_found is None:
                print(f"Warning: Mapping file not found in any location")
                print(f"Tried paths: {possible_paths}")
                return []

            # Load file
            with open(mapping_file_found, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("mappings", [])

        except Exception as e:
            print(f"Error loading mappings: {e}")
            return []

    def _default_mappings(self) -> List[Dict[str, Any]]:
        """Return empty list as default"""
        return []

    def encode(self, latex_expr: str) -> str:
        """Encode a single LaTeX expression to calculator keylog.

        Hỗ trợ:
        - Tích phân: \\int_{a}^{b} f(x) dx → yf(x)),a,b)
        - Phân số: \\frac{a}{b} → aab
        - Hàm: sqrt, sin, cos, tan, ln
        - Dấu: -, *, /, ^
        """
        if not latex_expr or not latex_expr.strip():
            return "0"

        result = latex_expr.strip().replace(" ", "")

        # ✅ STEP 1: Process integrals FIRST (trước khi xử lý fraction)
        # Pattern cho tích phân với ngoặc nhọn: \int_{lower}^{upper} function dx
        integral_pattern = r"\\int_\{([^}]+)\}\^\{([^}]+)\}([^d]+)d[a-z]"

        def process_integral(match):
            lower = match.group(1)  # Cận dưới
            upper = match.group(2)  # Cận trên
            function = match.group(3)  # Hàm số

            # ✅ Process nested content (bao gồm cả fractions)
            function_processed = self._process_nested(function)
            lower_processed = self._process_nested(lower)
            upper_processed = self._process_nested(upper)

            return f"y{function_processed}),{lower_processed},{upper_processed})"

        # Apply integral transformation
        result = re.sub(integral_pattern, process_integral, result)

        # ✅ STEP 2: Handle complex/nested fractions (20 iterations max)
        frac_pattern = r"\\frac\{((?:\{.*?\}|[^{}])+?)\}\{((?:\{.*?\}|[^{}])+?)\}"

        def process_frac(m):
            num = m.group(1)
            den = m.group(2)
            return f"{self._process_nested(num)}a{self._process_nested(den)}"

        changed = True
        max_iter = 20
        while changed and max_iter > 0:
            n_result = re.sub(frac_pattern, process_frac, result)
            changed = (n_result != result)
            result = n_result
            max_iter -= 1

        # ✅ STEP 3: Apply remaining mappings (sqrt, sin, cos, etc.)
        for mapping in self.mappings:
            find_pat = mapping.get("find", "")
            repl_pat = mapping.get("replace", "")
            typ = mapping.get("type", "literal")
            desc = mapping.get("description", "")

            # Skip patterns already handled
            if "frac" in desc.lower() or "tích phân" in desc.lower() or "int" in desc.lower():
                continue

            if typ == "regex":
                try:
                    result = re.sub(find_pat, repl_pat, result)
                except Exception:
                    pass
            else:
                result = result.replace(find_pat, repl_pat)

        return result

    def encode_batch(self, latex_exprs: List[str]) -> List[str]:
        """Encode multiple LaTeX expressions"""
        return [self.encode(expr) for expr in latex_exprs]

    def _process_nested(self, expr: str) -> str:
        """Process mapping in numerator/denominator/integral parts

        ✅ FIX: Xử lý cả fractions trong nested content
        """
        result = expr

        # ✅ STEP 1: Process fractions in nested content FIRST
        frac_pattern = r"\\frac\{((?:\{.*?\}|[^{}])+?)\}\{((?:\{.*?\}|[^{}])+?)\}"

        def process_nested_frac(m):
            num = m.group(1)
            den = m.group(2)
            # Recursive processing for deeply nested fractions
            num_processed = self._process_other_mappings(num)
            den_processed = self._process_other_mappings(den)
            return f"{num_processed}a{den_processed}"

        # Process fractions iteratively (max 10 iterations for nested content)
        changed = True
        max_iter = 10
        while changed and max_iter > 0:
            new_result = re.sub(frac_pattern, process_nested_frac, result)
            changed = (new_result != result)
            result = new_result
            max_iter -= 1

        # ✅ STEP 2: Apply other mappings (sqrt, sin, cos, etc.)
        result = self._process_other_mappings(result)

        return result

    def _process_other_mappings(self, expr: str) -> str:
        """Apply non-fraction, non-integral mappings"""
        result = expr

        for mapping in self.mappings:
            find_pat = mapping.get("find", "")
            repl_pat = mapping.get("replace", "")
            typ = mapping.get("type", "literal")
            desc = mapping.get("description", "")

            # Skip patterns that should not be applied here
            if "frac" in desc.lower() or "tích phân" in desc.lower() or "int" in desc.lower():
                continue

            if typ == "regex":
                try:
                    result = re.sub(find_pat, repl_pat, result)
                except Exception:
                    pass
            else:
                result = result.replace(find_pat, repl_pat)

        return result

    def validate_latex(self, latex_expr: str) -> Tuple[bool, Optional[str]]:
        """Validate LaTeX expression syntax"""
        if not latex_expr or not latex_expr.strip():
            return False, "Rỗng"

        # Check bracket matching
        if latex_expr.count("{") != latex_expr.count("}"):
            return False, "Dấu { } không khớp"

        return True, None


# EXAMPLE USAGE (unit test):
if __name__ == "__main__":
    encoder = LatexToKeylogEncoder()

    print("=" * 70)
    print("LATEX TO KEYLOG ENCODER - TEST (FIXED INTEGRAL WITH FRACTION)")
    print("=" * 70)
    print(f"Loaded {len(encoder.mappings)} mapping rules")
    print()

    # ✅ Test cases bao gồm tích phân có phân số
    tests = [
        # Tích phân có phân số (CRITICAL TEST)
        ("\\int_{0}^{1} \\frac{1}{x} dx", "Tích phân 1/x"),
        ("\\int_{a}^{b} \\frac{x^2}{2} dx", "Tích phân x²/2"),
        ("\\int_{0}^{pi} \\frac{sin(x)}{2} dx", "Tích phân sin(x)/2"),

        # Tích phân đơn giản
        ("\\int_{0}^{1} x^3 dx", "Tích phân x^3 từ 0 đến 1"),
        ("\\int_{1}^{5} sin(x) dx", "Tích phân sin(x) từ 1 đến 5"),
        ("\\int_{a}^{b} 2x dx", "Tích phân 2x từ a đến b"),
        ("\\int_{0}^{pi} cos(x) dx", "Tích phân cos(x) từ 0 đến pi"),

        # Phân số
        ("\\frac{9}{4}", "Phân số đơn giản"),
        ("\\frac{\\sqrt{2}}{3}", "Phân số có căn"),
        ("-\\frac{1}{2}", "Phân số âm"),

        # Hàm số
        ("-5", "Số âm"),
        ("sqrt(4)", "Căn bậc hai"),
        ("sin(x)", "Hàm sin"),
        ("cos(x)", "Hàm cos"),
        ("tan(x)", "Hàm tan"),
        ("ln(x)", "Hàm logarit tự nhiên"),

        # Phân số lồng nhau
        ("\\frac{\\frac{1}{2}}{3}", "Phân số lồng nhau"),
        ("\\int_{-1}^{1} x^2 dx", "Tích phân x^2 với cận âm"),
    ]

    for latex, description in tests:
        keylog = encoder.encode(latex)
        print(f"{description:40} | {latex:35} → {keylog}")

    print()
    print("=" * 70)
    print("CRITICAL TESTS - INTEGRAL WITH FRACTION")
    print("=" * 70)

    critical_tests = [
        ("\\int_{0}^{1} \\frac{1}{x} dx", "y1ax),0,1)"),
        ("\\int_{a}^{b} \\frac{x^2}{2} dx", "yx^2a2),a,b)"),
        ("\\int_{0}^{1} \\frac{sin(x)}{cos(x)} dx", "yj(x)ak(x)),0,1)"),
    ]

    print("\nVerifying fraction encoding inside integrals:\n")
    for latex, expected in critical_tests:
        actual = encoder.encode(latex)
        match = "✓" if actual == expected else "✗"
        print(f"{match} Input:    {latex}")
        print(f"  Expected: {expected}")
        print(f"  Actual:   {actual}")
        print()

    print("=" * 70)
    print("VALIDATION TEST")
    print("=" * 70)

    validation_tests = [
        ("\\int_{0}^{1} x dx", "Valid integral"),
        ("\\frac{1}{2}", "Valid fraction"),
        ("\\frac{1{2}", "Missing closing brace"),
        ("", "Empty string"),
    ]

    for expr, desc in validation_tests:
        valid, error = encoder.validate_latex(expr)
        status = "✓ Valid" if valid else f"✗ Invalid: {error}"
        print(f"{desc:40} | {expr:30} → {status}")
