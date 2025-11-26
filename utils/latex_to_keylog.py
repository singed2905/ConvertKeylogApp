import json
import os
import re
from typing import List, Dict, Any, Tuple, Optional


class LatexToKeylogEncoder:
    """Utility to encode LaTeX math expressions to calculator keylog format."""

    def __init__(self, mapping_file: str = "config/equation_mode/mapping.json"):
        self.mapping_file = mapping_file
        self.mappings = self._load_mappings()

    def _load_mappings(self) -> List[Dict[str, Any]]:
        try:
            possible_paths = [
                self.mapping_file,
                os.path.join("..", self.mapping_file),
                os.path.join("..", "..", self.mapping_file),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        return data.get("mappings", [])
            return []
        except Exception as e:
            print(f"Error loading mappings: {e}")
            return []

    def encode(self, latex_expr: str) -> str:
        """
        Encode LaTeX expression to keylog format.

        Pipeline order (critical for nested structures):
        1. Normalize (spaces, \\left, \\right)
        2. Process fractions (recursive, handles nested e^x inside)
        3. Process remaining e^x (outside fractions)
        4. Process sqrt normalization
        5. Process absolute values
        6. Process scientific notation
        7. Process log bases
        8. Process special functions (sin, cos, ln, sqrt, cdot)
        9. Process integrals
        10. Process general exponents
        11. Convert braces to parens
        12. Apply custom mappings
        13. Finalize separators
        """
        if not latex_expr or not latex_expr.strip():
            return "0"

        result = latex_expr.strip()
        result = result.replace(" ", "")
        result = result.replace(r'\left', '').replace(r'\right', '')

        # ==== CRITICAL: Process fractions FIRST (with recursive e^x handling) ====
        result = self._process_fractions(result)

        # ==== E^ (Euler number): e^{anything} → qh... ) ====
        result = self._process_e_power(result)

        # ==== SQRT normalization: sqrt{...} / sqrt(...) without backslash ====
        result = re.sub(r'(?<!\\)sqrt\{', r'\\sqrt{', result)
        result = re.sub(r'(?<!\\)sqrt\(', r'\\sqrt(', result)

        # ==== Absolute value: |a|, \\left|a\\right|, \\lvert a \\rvert ====
        result = re.sub(r'\\left\|([^|]+)\\right\|', r'q(\1)', result)
        result = re.sub(r'\|([^|]+)\|', r'q(\1)', result)
        result = re.sub(r'\\lvert([^|]+)\\rvert', r'q(\1)', result)

        # ==== Scientific notation: \\times 10^{n} → Kn ====
        result = re.sub(r'\\times10\^\{(-?\d+)\}', r'K\1', result)
        result = re.sub(r'\\times10\^(-?\d+)', r'K\1', result)

        # ==== Special log bases ====
        result = re.sub(r'\\log_(\d+)\{\((.*?)\)\}', r'i\1,(\2))', result)
        result = re.sub(r'\\log_\{([^}]*)\}\s*\{\s*([^}]*)\}', r'i((\2),\1)', result)
        result = re.sub(r'\\log_\{([^}]*)\}\s*\(([^)]*)\)', r'i(\2,\1)', result)
        result = re.sub(r'\\log_\{([^}]*)\}\s*([a-zA-Z0-9])', r'i(\2,\1)', result)
        result = re.sub(r'\\log_(\d+)\s*\(([^)]*)\)', r'i(\2__SEP__\1)', result)
        result = re.sub(r'\\log_(\d+)\s*([a-zA-Z0-9])', r'i(\2__SEP__\1)', result)

        # ==== Special functions (sin, cos, ln, sqrt, cdot) ====
        result = self._process_special_functions(result)

        # ==== Integrals: \\int_{lower}^{upper}function d(var) → y(function,lower,upper) ====
        max_iterations = 20
        for iteration in range(max_iterations):
            pattern = r'\\int_\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\^\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}(.*?)d([a-z])'
            match = re.search(pattern, result)
            if not match:
                break
            lower = match.group(1)
            upper = match.group(2)
            function = match.group(3)
            var = match.group(4)
            lower_clean = self._clean_bounds(lower)
            upper_clean = self._clean_bounds(upper)
            function_clean = self._clean_function(function)
            replacement = f"y({function_clean},{lower_clean},{upper_clean})"
            result = result[:match.start()] + replacement + result[match.end():]

        # ==== General exponents (x^n) ====
        result = self._process_exponents(result)

        # ==== Convert braces to parentheses ====
        result = result.replace("{", "(")
        result = result.replace("}", ")")

        # ==== Apply custom mappings from config ====
        result = self._apply_mappings(result)

        # ==== Finalize separators ====
        result = result.replace('__SEP__', 'q)')

        return result

    def _process_fractions(self, text: str) -> str:


        def find_matching_brace(s, start):
            """Find closing brace matching opening brace at position start"""
            count = 1
            i = start + 1
            while i < len(s) and count > 0:
                if s[i] == '{':
                    count += 1
                elif s[i] == '}':
                    count -= 1
                i += 1
            return i - 1 if count == 0 else -1

        result = text
        max_iterations = 20

        for iteration in range(max_iterations):
            # Find \frac{
            frac_pos = result.find(r'\frac{')
            if frac_pos == -1:
                break

            # Find numerator (between first { and matching })
            num_start = frac_pos + 6  # len('\frac{') = 6
            num_end = find_matching_brace(result, num_start - 1)

            if num_end == -1:
                break  # No matching brace found

            numerator = result[num_start:num_end]

            # Check for }{ pattern (denominator starts here)
            if num_end >= len(result) - 1 or result[num_end:num_end + 2] != '}{':
                break  # No denominator found

            den_start = num_end + 2
            den_end = find_matching_brace(result, den_start - 1)

            if den_end == -1:
                break  # No matching brace found

            denominator = result[den_start:den_end]

            # Recursive: process nested fractions
            if r'\frac' in numerator:
                numerator = self._process_fractions(numerator)
            if r'\frac' in denominator:
                denominator = self._process_fractions(denominator)

            # Process e^x patterns
            numerator = self._process_e_power(numerator)
            denominator = self._process_e_power(denominator)

            # Replace with (num)a(den)
            replacement = f"({numerator})a({denominator})"
            result = result[:frac_pos] + replacement + result[den_end + 1:]

        return result

    def _process_e_power(self, text: str) -> str:
        """
        Process Euler's number e^x patterns.

        Examples:
            e^{2} → qh2)
            e^{x+1} → qhxp1)
            e^{(1)a(2)} → qh(1)a(2))  [after fraction processing]
        """
        result = text
        result = re.sub(r'e\^\{([^}]+)\}', r'qh\1)', result)
        result = re.sub(r'e\^([0-9]+)', r'qh\1)', result)
        return result

    def _clean_bounds(self, bound: str) -> str:
        """Clean integral bounds (lower/upper limits)."""
        result = bound
        result = result.replace(r'\left', '').replace(r'\right', '')
        result = self._process_special_functions(result)
        result = self._process_exponents(result)
        result = self._process_fractions(result)
        result = result.replace("{", "(")
        result = result.replace("}", ")")
        return result

    def _clean_function(self, func: str) -> str:
        """Clean integral function expression."""
        result = func
        result = result.replace(r'\left', '').replace(r'\right', '')
        result = self._process_special_functions(result)
        result = self._process_exponents(result)
        result = self._process_fractions(result)
        result = result.replace("{", "(")
        result = result.replace("}", ")")
        return result

    def _process_special_functions(self, text: str) -> str:

        result = text

        # Process functions with BRACES first (before converting to parens)
        func_map_braces = {
            r'\sqrt{': 's',
            r'\sin{': 'j',
            r'\cos{': 'k',
            r'\tan{': 'l',
            r'\ln{': 'h',
            r'\log{': 'i',
        }

        # Also handle functions with parens (backup)
        func_map_parens = {
            r'\sqrt(': 's',
            r'\sin(': 'j',
            r'\cos(': 'k',
            r'\tan(': 'l',
            r'\ln(': 'h',
            r'\log(': 'i',
        }

        # Apply braces mappings first
        for latex_func, keylog_char in func_map_braces.items():
            result = result.replace(latex_func, keylog_char)

        # Then parens mappings (backup)
        for latex_func, keylog_char in func_map_parens.items():
            result = result.replace(latex_func, keylog_char)

        # Other mappings (no braces/parens)
        result = result.replace(r'\cdot', 'O')
        result = result.replace(r'\pi', 'qK')  # ← THÊM PI Ở ĐÂY!

        return result

    def _process_exponents(self, text: str) -> str:
        """
        Process general exponents (not e^x, which is handled separately).

        Examples:
            x^{2} → x^2)
            x^2 → x^2)
            (x+1)^{3} → (x+1)^3)
        """
        result = text
        result = re.sub(r'\^\{([^}]+)\}', r'^\1)', result)
        result = re.sub(r'\^([a-zA-Z0-9])(?![0-9\)])', r'^\1)', result)
        return result

    def _apply_mappings(self, text: str) -> str:
        """
        Apply custom character mappings from config file.
        Skips patterns that might conflict with LaTeX structures already processed.
        """
        result = text
        skip_keywords = ["frac", "tích phân", "ngoặc", "{", "}",
                         "sqrt", "sin", "cos", "tan", "ln", "\\"]

        for mapping in self.mappings:
            find_pat = mapping.get("find", "")
            repl_pat = mapping.get("replace", "")
            typ = mapping.get("type", "literal")
            desc = mapping.get("description", "").lower()

            # Skip if mapping might conflict with processed structures
            if any(kw in desc or kw in find_pat.lower() for kw in skip_keywords):
                continue

            if typ == "regex":
                try:
                    result = re.sub(find_pat, repl_pat, result)
                except:
                    pass  # Ignore regex errors
            else:
                result = result.replace(find_pat, repl_pat)

        return result

    def encode_batch(self, latex_exprs: List[str]) -> List[str]:
        """
        Encode multiple LaTeX expressions at once.

        Args:
            latex_exprs: List of LaTeX expression strings

        Returns:
            List of encoded keylog strings
        """
        return [self.encode(expr) for expr in latex_exprs]

    def validate_latex(self, latex_expr: str) -> Tuple[bool, Optional[str]]:
        """
        Validate LaTeX expression syntax.

        Args:
            latex_expr: LaTeX expression string

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not latex_expr or not latex_expr.strip():
            return False, "Rỗng"

        if latex_expr.count("{") != latex_expr.count("}"):
            return False, "Dấu { } không khớp"

        return True, None


# ============================================================================
# TEST CASES
# ============================================================================
if __name__ == "__main__":
    encoder = LatexToKeylogEncoder()

    print("=" * 70)
    print("LATEX TO KEYLOG ENCODER - COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    test_suites = {
        "Basic Operations": [
            (r"\sin(x)", "2p3"),
            (r"2\cdot3", "2O3"),
            (r"\frac{6\pi}{3}", "aOb"),
        ],

        "Euler's Number": [
            ("e^{2}", "qh2)"),
            ("e^2", "qh2)"),
            ("e^{x+1}", "qh[p1)"),
            ("e^{-x}", "qhm[)"),
        ],

        "Fractions": [
            (r"\frac{\sqrt(5)}{2}", "(1)a(2)"),
            (r"\frac{x+1}{x-1}", "([p1)a([m1)"),
            (r"\frac{\sqrt{2}}{3}", "(s(2))a(3)"),
        ],

        "e^x in Fractions": [
            (r"\frac{e^2}{3}", "(qh2))a(3)"),
            (r"\frac{1}{e^2}", "(1)a(qh2))"),
            (r"\frac{e^x}{e^y}", "(qh[))a(qh]))"),
        ],

        "Fractions in e^x (Critical)": [
            (r"e^{\frac{1}{2}}", "qh(1)a(2))"),
            (r"e^{\frac{x+1}{x-1}}", "qh([p1)a([m1))"),
        ],

        "Nested Fractions + e^x": [
            (r"\frac{e^{\frac{1}{2}}}{3}", "(qh(1)a(2)))a(3)"),
            (r"\frac{2}{e^{\frac{3}{4}}}", "(2)a(qh(3)a(4)))"),
            (r"e^{\frac{e^2}{3}}", "qh(qh2))a(3))"),
        ],

        "Square Roots": [
            (r"\sqrt{4}", "s(4)"),
            ("sqrt{4}", "s(4)"),
            (r"e^{\sqrt{x}}", "qhs([))"),
        ],

        "Absolute Values": [
            ("|x|", "q([)0"),
            (r"\left|x\right|", "q([)0"),
            ("e^{-|y|}", "qhmq([)0)"),
        ],

        "Scientific Notation": [
            (r"3.5\times10^{-5}", "3.5Kp5"),
            (r"2\times10^{-2}", "2Km2"),
        ],

        "Trigonometric Functions": [
            (r"\sin(30)", "j(30)"),
            (r"\cos(x)", "k([)"),
            (r"\tan(\frac{\pi}{4})", "l((π)a(4))"),
            (r"\sin(x)\cdot\cos(x)", "j([)Ok([)"),
        ],

        "Logarithms": [
            (r"\ln(x)", "h([)"),
            (r"\log(100)", "i(100)"),
            (r"\log_2(8)", "i(8q)2)"),
            (r"\log_{10}(100)", "i(100q)10)"),
        ],

        "Complex Expressions": [
            (r"\frac{\sin(\frac{\pi}{4})}{\cos(x)}", "(j((π)a(4)))a(k([))"),
            (r"e^{2} + e^{\frac{1}{2}}", "qh2)pqh(1)a(2))"),
            (r" - \left(\frac{x}{2} + \frac{13}{4}\right) \sqrt{x^{2} + 13 x + 36} + \left(\frac{x}{2} + \frac{15}{4}\right) \sqrt{13 x + \left(x + 1\right)^{2} + 49} - \frac{25 \log{\left(2 x + 2 \sqrt{13 x + \left(x + 1\right)^{2} + 49} + 15 \right)}}{8} + \frac{25 \log{\left(2 x + 2 \sqrt{x^{2} + 13 x + 36} + 13 \right)}}{8}", "(1)a(2)ps(4)ph([)"),
        ],
    }

    total_tests = 0
    passed_tests = 0

    for suite_name, tests in test_suites.items():
        print(f"\n{suite_name}:")
        print("-" * 70)

        for latex, expected in tests:
            result = encoder.encode(latex)
            status = "✅" if result == expected else "❌"
            total_tests += 1
            if result == expected:
                passed_tests += 1

            print(f"{status} {latex:35} → {result:25}")
            if result != expected:
                print(f"   Expected: {expected}")

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed_tests}/{total_tests} tests passed "
          f"({100 * passed_tests // total_tests}%)")
    print("=" * 70)
