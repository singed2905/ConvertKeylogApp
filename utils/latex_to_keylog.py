import json
import os
import re
from typing import List, Dict, Any, Tuple, Optional


class LatexToKeylogEncoder:


    def __init__(self, mapping_file: str = "config/equation_mode/mapping.json"):
        self.mapping_file = mapping_file
        self.mappings = self._load_mappings()

    def _load_mappings(self) -> List[Dict[str, Any]]:
        """Load mappings from JSON file"""
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
        """Encode a single LaTeX expression to calculator keylog."""
        if not latex_expr or not latex_expr.strip():
            return "0"

        result = latex_expr.strip().replace(" ", "")

        # Handle complex/nested \frac (20 iterations max)
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

        # Apply remaining mappings
        for mapping in self.mappings:
            find_pat = mapping.get("find", "")
            repl_pat = mapping.get("replace", "")
            typ = mapping.get("type", "literal")

            if "frac" in mapping.get("description", "").lower():
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
        """Process mapping in numerator/denominator"""
        result = expr

        for mapping in self.mappings:
            find_pat = mapping.get("find", "")
            repl_pat = mapping.get("replace", "")
            typ = mapping.get("type", "literal")

            if "frac" in mapping.get("description", "").lower():
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

        if latex_expr.count("{") != latex_expr.count("}"):
            return False, "Dấu { } không khớp"

        return True, None


# EXAMPLE USAGE
if __name__ == "__main__":
    encoder = LatexToKeylogEncoder()

    print("=" * 60)
    print("LATEX TO KEYLOG ENCODER - TEST")
    print("=" * 60)
    print(f"Loaded {len(encoder.mappings)} mapping rules")
    print()

    tests = [
        ("-5", "Số âm"),
        ("\\frac{9}{4}", "Phân số"),
        ("sqrt(4)", "Căn bậc hai"),
        ("sin(x)", "Hàm sin"),
    ]

    for latex, desc in tests:
        keylog = encoder.encode(latex)
        print(f"{desc:20} | {latex:25} → {keylog}")
