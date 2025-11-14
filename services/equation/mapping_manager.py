"""Mapping Manager - REFACTORED with fallback paths"""
import json
import re
import os
from typing import List, Dict, Any


class MappingManager:
    """
    DEPRECATED: Sử dụng LatexToKeylogEncoder thay thế
    Giữ lại để backwards compatibility
    """

    def __init__(self, mapping_file: str = "config/equation_mode/mapping.json"):
        self.mapping_file = mapping_file
        self.mappings = self._load_mappings()

    def _load_mappings(self) -> List[Dict[str, Any]]:
        """Load mappings from JSON file - ✅ ADDED fallback paths"""
        try:
            # ✅ THÊM: Thử nhiều đường dẫn relative
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
                return self._get_default_mappings()

            with open(mapping_file_found, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("mappings", [])

        except Exception as e:
            print(f"Error loading mappings: {e}")
            return self._get_default_mappings()

    def _get_default_mappings(self) -> List[Dict[str, Any]]:
        """Fallback mappings"""
        return []

    def encode_string(self, input_string: str) -> str:
        """Encode a string using the mapping rules"""
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

        # Process complex fractions
        changed = True
        max_iterations = 20
        while changed and max_iterations > 0:
            new_result = re.sub(complex_fraction_pattern, process_complex_fraction, result)
            changed = new_result != result
            result = new_result
            max_iterations -= 1

        # Apply other mappings
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
        """Process nested content with mappings"""
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
