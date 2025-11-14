import json
import os
import re
from typing import List, Dict, Any, Tuple, Optional


class LatexToKeylogEncoder:
    """Utility to encode LaTeX math expressions to calculator keylog format.
    Hỗ trợ: phân số, căn, hàm lượng giác, tích phân (kể cả cận có phân số).
    ĐẶC BIỆT: Xử lý đệ quy tích phân lồng nhau - không còn \\int_ trong kết quả.
    """

    def __init__(self, mapping_file: str = "config/equation_mode/mapping.json"):
        self.mapping_file = mapping_file
        self.mappings = self._load_mappings()

    def _load_mappings(self) -> List[Dict[str, Any]]:
        """Load mappings from JSON file"""
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
        """Encode LaTeX to keylog - XỬ LÝ ĐỆ QUY TÍCH PHÂN"""
        if not latex_expr or not latex_expr.strip():
            return "0"

        result = latex_expr.strip()

        # Loại bỏ spaces để dễ xử lý
        result = result.replace(" ", "")

        # ✅ BƯỚC 1: Xử lý tích phân đệ quy (từ trong ra ngoài)
        # Pattern phải match chính xác: \int_{...}^{...} ... dx
        # Sử dụng non-greedy để match tích phân trong cùng trước

        max_iterations = 20
        for iteration in range(max_iterations):
            # Pattern: \int_{lower}^{upper}function dx/dt/du...
            # Chú ý: cận có thể chứa \frac{}{} nên cần pattern phức tạp
            pattern = r'\\int_\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\^\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}(.*?)d([a-z])'

            match = re.search(pattern, result)
            if not match:
                break

            lower = match.group(1)
            upper = match.group(2)
            function = match.group(3)
            var = match.group(4)

            # Xử lý các thành phần
            lower_clean = self._clean_bounds(lower)
            upper_clean = self._clean_bounds(upper)
            function_clean = self._clean_function(function)

            # Tạo keylog: y function),lower,upper)
            replacement = f"y{function_clean}),{lower_clean},{upper_clean})"

            # Thay thế vào kết quả
            result = result[:match.start()] + replacement + result[match.end():]

        # ✅ BƯỚC 2: Xử lý phân số còn lại
        result = self._process_fractions(result)

        # ✅ BƯỚC 3: Apply các mappings còn lại
        result = self._apply_mappings(result)

        return result

    def _clean_bounds(self, bound: str) -> str:
        """Xử lý cận (có thể chứa phân số)"""
        result = bound

        # Xử lý \frac trong cận
        result = self._process_fractions(result)

        return result

    def _clean_function(self, func: str) -> str:
        """Xử lý hàm số"""
        result = func

        # Xử lý phân số trong hàm
        result = self._process_fractions(result)

        return result

    def _process_fractions(self, text: str) -> str:
        """Xử lý tất cả phân số: \frac{a}{b} -> aab"""
        result = text

        # Lặp để xử lý phân số lồng nhau
        for _ in range(15):
            # Pattern: \frac{numerator}{denominator}
            pattern = r'\\frac\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
            match = re.search(pattern, result)

            if not match:
                break

            num = match.group(1)
            den = match.group(2)

            # Thay thế
            replacement = f"{num}a{den}"
            result = result[:match.start()] + replacement + result[match.end():]

        return result

    def _apply_mappings(self, text: str) -> str:
        """Apply các mapping rules từ JSON"""
        result = text

        for mapping in self.mappings:
            find_pat = mapping.get("find", "")
            repl_pat = mapping.get("replace", "")
            typ = mapping.get("type", "literal")
            desc = mapping.get("description", "").lower()

            # Skip các pattern đã xử lý
            if "frac" in desc or "tích phân" in desc or "\\int" in find_pat.lower():
                continue

            if typ == "regex":
                try:
                    result = re.sub(find_pat, repl_pat, result)
                except:
                    pass
            else:
                result = result.replace(find_pat, repl_pat)

        return result

    def encode_batch(self, latex_exprs: List[str]) -> List[str]:
        """Encode multiple expressions"""
        return [self.encode(expr) for expr in latex_exprs]

    def validate_latex(self, latex_expr: str) -> Tuple[bool, Optional[str]]:
        """Validate LaTeX syntax"""
        if not latex_expr or not latex_expr.strip():
            return False, "Rỗng"
        if latex_expr.count("{") != latex_expr.count("}"):
            return False, "Dấu { } không khớp"
        return True, None


# TEST
if __name__ == "__main__":
    encoder = LatexToKeylogEncoder()

    print("=" * 80)
    print("LATEX TO KEYLOG ENCODER - COMPLETE FIX")
    print("=" * 80)
    print()

    tests = [
        (r"\int_{\frac{1-2}{2*4}}^{1/2} x^2 dx", "Tích phân đơn, cận phân số", "yx^2,1a2,1)"),
        (r"\int_{\frac{1}{2}}^{1} \int_{\frac{1}{2}}^{1} x^2 dx dx", "Tích phân kép", "y(yx^2,1a2,1),1a2,1)"),
        (r"\int_{0}^{1} \int_{0}^{1} \int_{0}^{1} x dx dx dx", "Tích phân bội 3", "y(y(yx,0,1),0,1),0,1)"),
        (r"\frac{1}{2}", "Phân số", "1a2"),
        (r"\int_{1}^{2} x^2 dx", "Tích phân đơn giản", "yx^2,1,2)"),
    ]

    for latex, desc, expected in tests:
        result = encoder.encode(latex)
        status = "✅" if result == expected else "❌"
        has_int = "❌ CÒN \\int_" if "\\int" in result else "✅ OK"

        print(f"{desc:40}")
        print(f"  LaTeX:    {latex}")
        print(f"  Keylog:   {result}")
        print(f"  Expected: {expected}")
        print(f"  Match: {status} | {has_int}")
        print()
