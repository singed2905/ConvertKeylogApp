import json
import os
import re
from typing import List, Dict, Any, Tuple, Optional

class LatexToKeylogEncoder:
    """Utility to encode LaTeX math expressions to calculator keylog format.
    Supports version-based mapping (e.g. fx799, fx991, ...) via mapping JSON.
    """

    def __init__(self, mapping_file: str = "config/equation_mode/mapping.json"):
        self.mapping_file = mapping_file
        self.mappings = self._load_mappings()

    def _load_mappings(self) -> List[Dict[str, Any]]:
        """Load mappings from JSON file"""
        try:
            if not os.path.exists(self.mapping_file):
                print(f"Warning: Mapping file not found: {self.mapping_file}")
                return self._default_mappings()

            with open(self.mapping_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("mappings", [])
        except Exception as e:
            print(f"Error loading mappings: {e}")
            return self._default_mappings()

    def _default_mappings(self) -> Dict[str, Any]:
        # Sample minimal mapping
        return {

        }

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
        # Remaining mappings
        for mapping in self.mappings.get("latex_to_calculator_mappings", []):
            find_pat = mapping.get("find", "")
            repl_pat = mapping.get("replace", "")
            typ = mapping.get("type", "literal")
            if "frac" in mapping.get("description", "").lower():
                continue # skip already handled fraction
            if typ == "regex":
                try: result = re.sub(find_pat, repl_pat, result)
                except Exception: pass
            else:
                result = result.replace(find_pat, repl_pat)
        return result
    
    def encode_batch(self, latex_exprs: List[str]) -> List[str]:
        return [self.encode(expr) for expr in latex_exprs]

    def _process_nested(self, expr: str) -> str:
        # Process mapping in numerator/denominator
        result = expr
        for mapping in self.mappings.get("latex_to_calculator_mappings", []):
            find_pat = mapping.get("find", "")
            repl_pat = mapping.get("replace", "")
            typ = mapping.get("type", "literal")
            if "frac" in mapping.get("description", "").lower(): continue
            if typ == "regex":
                try: result = re.sub(find_pat, repl_pat, result)
                except Exception: pass
            else:
                result = result.replace(find_pat, repl_pat)
        return result

    def validate_latex(self, latex_expr: str) -> Tuple[bool, Optional[str]]:
        if not latex_expr or not latex_expr.strip():
            return False, "Rỗng"
        # Very minimal validation: no unclosed brackets
        if latex_expr.count("{") != latex_expr.count("}"):
            return False, "Dấu { } không khớp"
        # Could extend with sympy/parsing in future
        return True, None

# EXAMPLE USAGE (unit test):
if __name__ == "__main__":
    encoder = LatexToKeylogEncoder()
    tests = [
        "-5",
        "\\frac{9}{4}",
        "sqrt(4)",
        "\\frac{\\sqrt{2}}{3}",
        "1",
        "-\\frac{1}{2}",
    ]
    for latex in tests:
        keylog = encoder.encode(latex)
        print(f"{latex}  →  {keylog}")
