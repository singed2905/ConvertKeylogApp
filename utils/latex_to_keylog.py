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
        if not latex_expr or not latex_expr.strip():
            return "0"
        result = latex_expr.strip()
        result = result.replace(" ", "")
        result = result.replace(r'\left', '').replace(r'\right', '')
        
        # Xử lý log base đặc biệt
        result = re.sub(r'\\log_(\d+)\{\((.*?)\)\}', r'i\1,(\2))', result)
        result = re.sub(r'\\log_\{([^}]*)\}\s*\{\s*([^}]*)\}', r'i((\2),\1)', result)
        result = re.sub(r'\\log_\{([^}]*)\}\s*\(([^)]*)\)', r'i(\2,\1)', result)
        result = re.sub(r'\\log_\{([^}]*)\}\s*([a-zA-Z0-9])', r'i(\2,\1)', result)
        result = re.sub(r'\\log_(\d+)\s*\(([^)]*)\)', r'i(\2__SEP__\1)', result)
        result = re.sub(r'\\log_(\d+)\s*([a-zA-Z0-9])', r'i(\2__SEP__\1)', result)
        
        result = self._process_special_functions(result)
        
        # Xử lý tích phân - FIX: đổi pattern từ \\^ thành \^
        max_iterations = 20
        for iteration in range(max_iterations):
            # Pattern cũ: r'\\int_\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\\^\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}(.*?)d([a-z])'
            # Pattern mới: thay \\^ bằng \^
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
            replacement = f"y{function_clean}),{lower_clean},{upper_clean})"
            result = result[:match.start()] + replacement + result[match.end():]
        
        result = self._process_exponents(result)
        result = self._process_fractions(result)
        result = result.replace("{", "(")
        result = result.replace("}", ")")
        result = self._apply_mappings(result)
        result = result.replace('__SEP__', 'q)')
        return result

    def _clean_bounds(self, bound: str) -> str:
        result = bound
        result = result.replace(r'\left', '').replace(r'\right', '')
        result = self._process_special_functions(result)
        result = self._process_exponents(result)
        result = self._process_fractions(result)
        result = result.replace("{", "(")
        result = result.replace("}", ")")
        return result

    def _clean_function(self, func: str) -> str:
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
        func_map = {
            r'\sqrt': 's',
            r'\sin': 'j',
            r'\cos': 'k',
            r'\tan': 'l',
            r'\ln': 'h',
            r'\log': 'i',
        }
        for latex_func, keylog_char in func_map.items():
            result = result.replace(latex_func, keylog_char)
        return result

    def _process_fractions(self, text: str) -> str:
        result = text
        for _ in range(15):
            pattern = r'\\frac\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
            match = re.search(pattern, result)
            if not match:
                break
            num = match.group(1)
            den = match.group(2)
            replacement = f"({num})a({den})"
            result = result[:match.start()] + replacement + result[match.end():]
        return result

    def _process_exponents(self, text: str) -> str:
        result = text
        result = re.sub(r'\^\{([^}]+)\}', r'^\1)', result)
        result = re.sub(r'\^([a-zA-Z0-9])(?![0-9\)])', r'^\1)', result)
        return result

    def _apply_mappings(self, text: str) -> str:
        result = text
        skip_keywords = ["frac", "tích phân", "ngoặc", "{", "}", "sqrt", "sin", "cos", "tan", "ln", "\\"]
        for mapping in self.mappings:
            find_pat = mapping.get("find", "")
            repl_pat = mapping.get("replace", "")
            typ = mapping.get("type", "literal")
            desc = mapping.get("description", "").lower()
            if any(kw in desc or kw in find_pat.lower() for kw in skip_keywords):
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
        return [self.encode(expr) for expr in latex_exprs]

    def validate_latex(self, latex_expr: str) -> Tuple[bool, Optional[str]]:
        if not latex_expr or not latex_expr.strip():
            return False, "Rỗng"
        if latex_expr.count("{") != latex_expr.count("}"):
            return False, "Dấu { } không khớp"
        return True, None

# TEST
if __name__ == "__main__":
    encoder = LatexToKeylogEncoder()
    print("=" * 80)
    print("LATEX TO KEYLOG ENCODER - WITH LOG SUPPORT")
    print("=" * 80)
    print()
    tests = [
        (r"x^{10}", "Dấu mũ 2 chữ số"),
        (r"x^2", "Dấu mũ 1 chữ số"),
        (r"\frac{1}{x^3}", "Phân số với mũ"),
        (r"\int_{0}^{1} x^2 dx", "Tích phân x^2"),
        (r"\int_{1}^{e} \log_2(x) dx", "Tích phân với log [FIX]"),
        (r"\log_7{3x}", "Log base 7 của 3x"),
        (r"\log_2(x)", "Log base 2 của x"),
        (r"\int_{1}^{2} \sqrt{\frac{1}{x^3}+x^2} dx", "Tích phân phức tạp"),
        (r"\log_7{(3x)}", "Log base 7 của (3x) [new rule]"),
    ]
    for latex, desc in tests:
        result = encoder.encode(latex)
        print(f"{desc:40}")
        print(f"  LaTeX:  {latex}")
        print(f"  Keylog: {result}")
        print()
