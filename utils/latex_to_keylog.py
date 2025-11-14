import json
import os
import re
from typing import List, Dict, Any, Tuple, Optional


class LatexToKeylogEncoder:
    """Utility to encode LaTeX math expressions to calculator keylog format.
    Supports version-based mapping (e.g. fx799, fx991, ...) via mapping JSON.
    Hỗ trợ: phân số, căn, hàm lượng giác, tích phân (kể cả cận có phân số).
    """

    def __init__(self, mapping_file: str = "config/equation_mode/mapping.json"):
        self.mapping_file = mapping_file
        self.mappings = self._load_mappings()

    def _load_mappings(self) -> List[Dict[str, Any]]:
        """Load mappings from JSON file - thử nhiều relative paths"""
        try:
            # Thử nhiều đường dẫn relative khác nhau
            possible_paths = [
                self.mapping_file,
                os.path.join("..", self.mapping_file),
                os.path.join("..", "..", self.mapping_file),
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
        - Tích phân với cận phức tạp: \\int_{\\frac{1}{2}}^{1} f(x) dx
        - Phân số: \\frac{a}{b} → aab
        - Hàm: sqrt, sin, cos, tan, ln
        - Dấu: -, *, /, ^
        """
        if not latex_expr or not latex_expr.strip():
            return "0"

        result = latex_expr.strip().replace(" ", "")

        # ✅ STEP 1: Process integrals FIRST
        # ✅ FIX: Pattern hỗ trợ nested braces trong cận
        integral_pattern = r"\\int_\{((?:\{[^}]*\}|[^{}])+)\}\^\{((?:\{[^}]*\}|[^{}])+)\}([^d]+)d[a-z]"

        def process_integral(match):
            lower = match.group(1)  # Cận dưới (có thể có \frac{})
            upper = match.group(2)  # Cận trên (có thể có \frac{})
            function = match.group(3)  # Hàm số

            # Process nested content (bao gồm fractions trong cận)
            function_processed = self._process_nested(function)
            lower_processed = self._process_nested(lower)
            upper_processed = self._process_nested(upper)

            return f"y{function_processed}),{lower_processed},{upper_processed})"

        # Apply integral transformation (max 5 iterations for nested integrals)
        changed = True
        max_iter = 5
        while changed and max_iter > 0:
            new_result = re.sub(integral_pattern, process_integral, result)
            changed = (new_result != result)
            result = new_result
            max_iter -= 1

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

        ✅ Xử lý cả fractions trong nested content
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

    print("=" * 80)
    print("LATEX TO KEYLOG ENCODER - TEST (COMPLEX INTEGRAL WITH FRACTION IN BOUNDS)")
    print("=" * 80)
    print(f"Loaded {len(encoder.mappings)} mapping rules")
    print()

    # ✅ Test case phức tạp: Phân số chứa tích phân có cận là phân số
    critical_tests = [
        # Tích phân có cận là phân số
        ("\\int_{\\frac{1}{2}}^{1} x dx", "Tích phân cận dưới là 1/2"),
        ("\\int_{0}^{\\frac{1}{2}} x^2 dx", "Tích phân cận trên là 1/2"),
        ("\\int_{\\frac{1}{2}}^{\\frac{3}{4}} x dx", "Tích phân 2 cận đều là phân số"),

        # Phân số chứa tích phân
        ("\\frac{\\int_{0}^{1} x dx}{2}", "Phân số tử là tích phân"),
        ("\\frac{\\int_{\\frac{1}{2}}^{1} \\frac{1}{2} dx}{y-2}", "Case của bạn"),

        # Tích phân có hàm là phân số, cận là phân số
        ("\\int_{\\frac{1}{2}}^{1} \\frac{1}{x} dx", "Cận và hàm đều có phân số"),

        # Test cases đơn giản
        ("\\int_{0}^{1} x^3 dx", "Tích phân đơn giản"),
        ("\\frac{1}{2}", "Phân số đơn giản"),
    ]

    for latex, desc in critical_tests:
        encoded = encoder.encode(latex)
        print(f"{desc:50} | {latex:45}")
        print(f"{'':50} → {encoded}")
        print()

    print("=" * 80)
    print("DETAILED ANALYSIS - YOUR CASE")
    print("=" * 80)

    your_case = "\\frac{\\int_{\\frac{1}{2}}^{1} \\frac{1}{2} dx}{y-2}"
    print(f"\nInput:  {your_case}")
    print(f"Output: {encoder.encode(your_case)}")

    print("\n\nStep-by-step breakdown:")
    print("1. Integral inside: \\int_{\\frac{1}{2}}^{1} \\frac{1}{2} dx")
    print("   → Lower bound: \\frac{1}{2} → 1a2")
    print("   → Upper bound: 1 → 1")
    print("   → Function: \\frac{1}{2} → 1a2")
    print("   → Result: y1a2),1a2,1)")
    print()
    print("2. Outer fraction: \\frac{y1a2),1a2,1)}{y-2}")
    print("   → Numerator: y1a2),1a2,1)")
    print("   → Denominator: y-2 → yp2")
    print("   → Result: y1a2),1a2,1)ayp2")

    print("\n" + "=" * 80)
    print("VALIDATION")
    print("=" * 80)

    test_validation = [
        ("\\int_{\\frac{1}{2}}^{1} x dx", "Valid complex integral"),
        ("\\frac{\\int_{0}^{1} x dx}{2}", "Valid fraction with integral"),
        ("\\frac{1{2}", "Invalid - missing brace"),
    ]

    for expr, desc in test_validation:
        valid, error = encoder.validate_latex(expr)
        status = "✓ Valid" if valid else f"✗ Invalid: {error}"
        print(f"{desc:40} → {status}")
