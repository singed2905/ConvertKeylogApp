import json
import re
import os
from typing import Dict, Any, List
from utils.config_loader import config_loader

class GeometryMappingAdapter:
    """Adapter to handle mapping from TL format to new config structure"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.mappings = self._load_polynomial_mappings()
        self.excel_mappings = self._load_excel_mappings()
    
    def _load_polynomial_mappings(self) -> List[Dict[str, Any]]:
        """Load polynomial mapping rules from new config structure"""
        try:
            if self.config and 'polynomial' in self.config:
                polynomial_config = self.config['polynomial']
                if 'mapping' in polynomial_config:
                    mapping_data = polynomial_config['mapping']
                    return mapping_data.get('latex_to_calculator_mappings', [])
            
            # Fallback: try to load directly from config_loader
            poly_config = config_loader.load_polynomial_config('polynomial_mapping')
            return poly_config.get('latex_to_calculator_mappings', [])
        except Exception as e:
            print(f"Warning: Could not load polynomial mappings: {e}")
            return self._get_default_mappings()
    
    def _load_excel_mappings(self) -> Dict[str, Any]:
        """Load Excel mapping configuration"""
        try:
            if self.config and 'geometry' in self.config:
                geometry_config = self.config['geometry']
                if 'excel_mapping' in geometry_config:
                    return geometry_config['excel_mapping']
            
            # Fallback: try to load directly from config_loader
            return config_loader.load_geometry_config('geometry_excel_mapping')
        except Exception as e:
            print(f"Warning: Could not load Excel mappings: {e}")
            return {}
    
    def _get_default_mappings(self) -> List[Dict[str, Any]]:
        """Fallback mappings matching TL behavior"""
        return [
            {"find": r"\\\\frac\\{([^{}]+)\\}\\{([^{}]+)\\}", "replace": r"\1a\2", "type": "regex", "description": "Fraction conversion"},
            {"find": r"\\-", "replace": "p", "type": "regex", "description": "Negative sign"},
            {"find": r"\\*", "replace": "O", "type": "regex", "description": "Multiplication"},
            {"find": r"\\/", "replace": "P", "type": "regex", "description": "Division"},
            {"find": r"\\\\sqrt\\{", "replace": "s", "type": "regex", "description": "Square root"},
            {"find": r"sqrt\\{", "replace": "s", "type": "regex", "description": "Square root no backslash"},
            {"find": r"\\\\sin\\(", "replace": "j(", "type": "regex", "description": "Sine function"},
            {"find": r"sin\\(", "replace": "j(", "type": "regex", "description": "Sine function no backslash"},
            {"find": r"\\\\cos\\(", "replace": "k(", "type": "regex", "description": "Cosine function"},
            {"find": r"cos\\(", "replace": "k(", "type": "regex", "description": "Cosine function no backslash"},
            {"find": r"\\\\tan\\(", "replace": "l(", "type": "regex", "description": "Tangent function"},
            {"find": r"tan\\(", "replace": "l(", "type": "regex", "description": "Tangent function no backslash"},
            {"find": r"\\\\ln\\(", "replace": "h(", "type": "regex", "description": "Natural log function"},
            {"find": r"ln\\(", "replace": "h(", "type": "regex", "description": "Natural log function no backslash"},
            {"find": r"\\}", "replace": ")", "type": "regex", "description": "Close brace to parenthesis"},
            {"find": r"\\{", "replace": "(", "type": "regex", "description": "Open brace to parenthesis"},
            {"find": r"\\^", "replace": "^", "type": "regex", "description": "Power operator"},
            {"find": "_", "replace": "_", "type": "regex", "description": "Subscript operator"}
        ]
    
    def encode_string(self, input_string: str) -> str:
        """Encode a string using the mapping rules (matching TL MappingManager behavior)"""
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

            if "frac" in description.lower():
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

            if "frac" in description.lower():
                continue

            if rule_type == "regex":
                try:
                    result = re.sub(find, replace, result)
                except Exception:
                    continue
            else:
                result = result.replace(find, replace)

        return result
    
    def get_excel_column_mapping(self, shape: str, group: str) -> Dict[str, str]:
        """Get Excel column mapping for a specific shape and group"""
        try:
            group_key = f"group_{group.lower()}_mapping"
            if group_key in self.excel_mappings and shape in self.excel_mappings[group_key]:
                shape_config = self.excel_mappings[group_key][shape]
                columns = shape_config.get('columns', {})
                return {key: col_info['excel_column'] for key, col_info in columns.items()}
        except Exception as e:
            print(f"Error getting Excel mapping for {shape} group {group}: {e}")
        
        return self._get_default_excel_mapping(shape, group)
    
    def _get_default_excel_mapping(self, shape: str, group: str) -> Dict[str, str]:
        """Fallback Excel mapping"""
        if shape == "Điểm":
            return {'point_input': f'data_{group}'}
        elif shape == "Đường thẳng":
            return {'line_A1': f'd_P_data_{group}', 'line_X1': f'd_V_data_{group}'}
        elif shape == "Mặt phẳng":
            base = 'P1' if group == 'A' else 'P2'
            return {
                'plane_a': f'{base}_a',
                'plane_b': f'{base}_b', 
                'plane_c': f'{base}_c',
                'plane_d': f'{base}_d'
            }
        elif shape == "Đường tròn":
            suffix = '1' if group == 'A' else '2'
            return {'circle_center': f'C_data_I{suffix}', 'circle_radius': f'C_data_R{suffix}'}
        elif shape == "Mặt cầu":
            suffix = '1' if group == 'A' else '2' 
            return {'sphere_center': f'S_data_I{suffix}', 'sphere_radius': f'S_data_R{suffix}'}
        
        return {}
