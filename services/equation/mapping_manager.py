"""Mapping Manager - Core keylog encoding engine ported from TL"""
import json
import re
import os
from typing import List, Dict, Any


class MappingManager:
    """Port từ TL models/mapping_manager.py - Core keylog encoding"""
    
    def __init__(self, mapping_file: str = "config/equation_mode/mapping.json"):
        self.mapping_file = mapping_file
        self.mappings = self._load_mappings()

    def _load_mappings(self) -> List[Dict[str, Any]]:
        """Load mappings from JSON file"""
        try:
            if not os.path.exists(self.mapping_file):
                print(f"Warning: Mapping file not found: {self.mapping_file}")
                return self._get_default_mappings()

            with open(self.mapping_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("mappings", [])
        except Exception as e:
            print(f"Error loading mappings: {e}")
            return self._get_default_mappings()

    def _get_default_mappings(self) -> List[Dict[str, Any]]:
        """Fallback mappings giống TL"""
        return [
            {
                "find": "\\\\frac\\{([^{}]+)\\}\\{([^{}]+)\\}",
                "replace": "$1a$2",
                "type": "regex",
                "description": "Chuyển phân số \\frac{x}{y} thành dạng x a y"
            },
            {
                "find": "\\-",
                "replace": "p",
                "type": "regex", 
                "description": "Dấu âm (trừ) ở đầu chuỗi thành 'p'"
            },
            {
                "find": "\\*",
                "replace": "O",
                "type": "regex",
                "description": "Dấu nhân (*) thành 'O'"
            },
            {
                "find": "\\/",
                "replace": "P",
                "type": "regex",
                "description": "Dấu chia (/) thành 'P'"
            },
            {
                "find": "\\\\sqrt\\{",
                "replace": "s",
                "type": "regex",
                "description": "Hàm sqrt{ có dấu \\ → s"
            },
            {
                "find": "sqrt\\{",
                "replace": "s",
                "type": "regex",
                "description": "Hàm sqrt{ không dấu \\ → s"
            },
            {
                "find": "\\\\sqrt\\(",
                "replace": "s",
                "type": "regex",
                "description": "Hàm sqrt( có dấu \\ → s"
            },
            {
                "find": "sqrt\\(",
                "replace": "s",
                "type": "regex",
                "description": "Hàm sqrt( không dấu \\ → s"
            },
            {
                "find": "\\\\sin\\(",
                "replace": "j(",
                "type": "regex",
                "description": "Hàm sin(x) có dấu \\ → j(x)"
            },
            {
                "find": "sin\\(",
                "replace": "j(",
                "type": "regex",
                "description": "Hàm sin(x) không dấu \\ → j(x)"
            },
            {
                "find": "\\\\cos\\(",
                "replace": "k(",
                "type": "regex",
                "description": "Hàm cos(x) có dấu \\ → k(x)"
            },
            {
                "find": "cos\\(",
                "replace": "k(",
                "type": "regex",
                "description": "Hàm cos(x) không dấu \\ → k(x)"
            },
            {
                "find": "\\\\tan\\(",
                "replace": "l(",
                "type": "regex",
                "description": "Hàm tan(x) có dấu \\ → l(x)"
            },
            {
                "find": "tan\\(",
                "replace": "l(",
                "type": "regex",
                "description": "Hàm tan(x) không dấu \\ → l(x)"
            },
            {
                "find": "\\\\ln\\(",
                "replace": "h(",
                "type": "regex",
                "description": "Hàm ln(x) có dấu \\ → h(x)"
            },
            {
                "find": "ln\\(",
                "replace": "h(",
                "type": "regex",
                "description": "Hàm ln(x) không dấu \\ → h("
            },
            {
                "find": "\\}",
                "replace": ")",
                "type": "regex",
                "description": "Ngoặc nhọn đóng } thành )"
            },
            {
                "find": "\\{",
                "replace": "(",
                "type": "regex",
                "description": "Ngoặc nhọn mở { thành ("
            },
            {
                "find": "\\^",
                "replace": "^",
                "type": "regex",
                "description": "Dấu mũ ^ giữ nguyên"
            },
            {
                "find": "_",
                "replace": "_",
                "type": "regex",
                "description": "Dấu chỉ số dưới _ giữ nguyên"
            }
        ]

    def encode_string(self, input_string: str) -> str:
        """Encode a string using the mapping rules - GIỐNG TL"""
        input_string = input_string.replace(" ", "")
        if not input_string:
            return ""

        result = input_string
        complex_fraction_pattern = r"\\frac\{((?:\{.*?\}|[^{}])+)\}\{((?:\{.*?\}|[^{}])+)\}"

        def process_complex_fraction(match):
            num = match.group(1)
            den = match.group(2)
            num_processed = self._process_nested_content(num)
            den_processed = self._process_nested_content(den)
            return f"{num_processed}a{den_processed}"

        # Process complex fractions - Logic y hệt TL
        changed = True
        max_iterations = 20
        while changed and max_iterations > 0:
            new_result = re.sub(complex_fraction_pattern, process_complex_fraction, result)
            changed = new_result != result
            result = new_result
            max_iterations -= 1

        # Apply other mappings - Đúng thứ tự như TL
        for rule in self.mappings:
            find = rule.get("find", "")
            replace = rule.get("replace", "")
            rule_type = rule.get("type", "literal")
            description = rule.get("description", "")

            if "frac" in description:
                continue

            if rule_type == "regex":
                try:
                    result = re.sub(find, replace, result)
                except Exception as e:
                    print(f"Regex error with pattern '{find}': {e}")
                    continue
            else:
                result = result.replace(find, replace)

        return result

    def _process_nested_content(self, content: str) -> str:
        """Process nested content with mappings - GIỐNG TL"""
        result = content
        for rule in self.mappings:
            find = rule.get("find", "")
            replace = rule.get("replace", "")
            rule_type = rule.get("type", "literal")
            description = rule.get("description", "")

            if "frac" in description:
                continue

            if rule_type == "regex":
                try:
                    result = re.sub(find, replace, result)
                except Exception:
                    continue
            else:
                result = result.replace(find, replace)

        return result
    
    def reload_mappings(self):
        """Reload mappings (useful for development)"""
        try:
            self.mappings = self._load_mappings()
            return True
        except Exception as e:
            print(f"Error reloading mappings: {e}")
            return False