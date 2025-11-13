"""Polynomial Encoding Service - Converts mathematical expressions to calculator keylog format
Uses polynomial_mapping.json for LaTeX/mathematical expression to calculator encoding
ENHANCED: Now handles complex nested fractions like Equation Mode's MappingManager
"""
import json
import os
import re
from typing import List, Dict, Any, Tuple


class PolynomialEncodingService:
    """Service mã hóa biểu thức toán học thành keylog format cho máy tính Casio
    ENHANCED: Xử lý phân số phức tạp giống MappingManager trong Equation Mode
    """
    
    def __init__(self, mapping_file: str = "config/polynomial_mode/polynomial_mapping.json"):
        self.mapping_file = mapping_file
        self.mappings = self._load_mappings()
        
    def _load_mappings(self) -> Dict[str, Any]:
        """Load mappings từ JSON file"""
        try:
            if not os.path.exists(self.mapping_file):
                print(f"Warning: Mapping file not found: {self.mapping_file}")
                return self._get_default_mappings()
            
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "latex_to_calculator_mappings" not in data:
                print(f"Warning: Invalid mapping file structure")
                return self._get_default_mappings()
            
            return data
            
        except Exception as e:
            print(f"Error loading mapping file: {e}")
            return self._get_default_mappings()
    
    def _get_default_mappings(self) -> Dict[str, Any]:
        """Fallback mappings nếu không load được file"""
        return {
            "latex_to_calculator_mappings": [
                {
                    "find": "\\\\frac\\{([^{}]+)\\}\\{([^{}]+)\\}",
                    "replace": "$1a$2",
                    "type": "regex",
                    "description": "Chuyển phân số \\frac{x}{y} thành dạng x a y"
                },
                {"find": "-", "replace": "p", "type": "literal", "description": "Dấu âm"},
                {"find": "sqrt(", "replace": "s(", "type": "literal", "description": "sqrt"},
                {"find": "sin(", "replace": "j(", "type": "literal", "description": "sin"},
                {"find": "cos(", "replace": "k(", "type": "literal", "description": "cos"},
                {"find": "tan(", "replace": "l(", "type": "literal", "description": "tan"},
                {"find": "ln(", "replace": "h(", "type": "literal", "description": "ln"},
                {"find": "}", "replace": ")", "type": "literal", "description": "Close brace"},
                {"find": "{", "replace": "(", "type": "literal", "description": "Open brace"}
            ],
            "metadata": {"version": "fallback"}
        }
    
    def encode_coefficient(self, coefficient_str: str) -> str:
        """Mã hóa một hệ số từ biểu thức toán học sang calculator format
        ENHANCED: Xử lý complex fractions như MappingManager
        
        Args:
            coefficient_str: Chuỗi biểu thức hệ số (ví dụ: "\\frac{9}{4}", "sqrt(4)", "sin(pi/2)")
            
        Returns:
            Chuỗi đã mã hóa theo quy tắc calculator
        """
        if not coefficient_str or not coefficient_str.strip():
            return "0"
        
        # Remove spaces like MappingManager
        result = coefficient_str.strip().replace(" ", "")
        
        # === COMPLEX FRACTION PROCESSING (from MappingManager) ===
        # Pattern cho phân số phức tạp có thể chứa nested content
        complex_fraction_pattern = r"\\frac\{((?:\{.*?\}|[^{}])+)\}\{((?:\{.*?\}|[^{}])+)\}"
        
        def process_complex_fraction(match):
            """Process nested fraction content"""
            num = match.group(1)
            den = match.group(2)
            num_processed = self._process_nested_content(num)
            den_processed = self._process_nested_content(den)
            return f"{num_processed}a{den_processed}"
        
        # Iteratively process complex fractions (max 20 iterations to prevent infinite loop)
        changed = True
        max_iterations = 20
        while changed and max_iterations > 0:
            new_result = re.sub(complex_fraction_pattern, process_complex_fraction, result)
            changed = new_result != result
            result = new_result
            max_iterations -= 1
        
        # === APPLY OTHER MAPPINGS ===
        mappings_list = self.mappings.get("latex_to_calculator_mappings", [])
        
        for mapping in mappings_list:
            find_pattern = mapping.get("find", "")
            replace_pattern = mapping.get("replace", "")
            mapping_type = mapping.get("type", "literal")
            description = mapping.get("description", "")
            
            # Skip fraction rules as we already handled them above
            if "frac" in description.lower():
                continue
            
            if mapping_type == "regex":
                # Áp dụng regex replacement
                try:
                    result = re.sub(find_pattern, replace_pattern, result)
                except Exception as e:
                    print(f"Regex error for pattern '{find_pattern}': {e}")
            else:
                # Literal replacement
                result = result.replace(find_pattern, replace_pattern)
        
        # Try to simplify integer representation
        try:
            val = float(result)
            if val.is_integer():
                result = str(int(val))
        except:
            pass  # Không phải số, giữ nguyên
        
        return result
    
    def _process_nested_content(self, content: str) -> str:
        """Process nested content with mappings - GIỐNG MappingManager
        Used for processing numerator and denominator of fractions
        """
        result = content
        mappings_list = self.mappings.get("latex_to_calculator_mappings", [])
        
        for mapping in mappings_list:
            find_pattern = mapping.get("find", "")
            replace_pattern = mapping.get("replace", "")
            mapping_type = mapping.get("type", "literal")
            description = mapping.get("description", "")
            
            # Skip fraction rules in nested processing
            if "frac" in description.lower():
                continue
            
            if mapping_type == "regex":
                try:
                    result = re.sub(find_pattern, replace_pattern, result)
                except Exception:
                    continue
            else:
                result = result.replace(find_pattern, replace_pattern)
        
        return result
    
    def encode_coefficients(self, coefficients: List[str]) -> List[str]:
        """Mã hóa danh sách hệ số
        
        Args:
            coefficients: List các chuỗi hệ số
            
        Returns:
            List các chuỗi đã mã hóa
        """
        encoded = []
        for coeff in coefficients:
            encoded_coeff = self.encode_coefficient(coeff)
            encoded.append(encoded_coeff)
        return encoded
    
    def encode_with_validation(self, coefficient_str: str) -> Tuple[bool, str, str]:
        """Mã hóa kèm validation
        
        Returns:
            (success, encoded_result, error_message)
        """
        try:
            if not coefficient_str or not coefficient_str.strip():
                return True, "0", ""
            
            encoded = self.encode_coefficient(coefficient_str)
            return True, encoded, ""
            
        except Exception as e:
            return False, coefficient_str, f"Encoding error: {str(e)}"
    
    def get_mapping_info(self) -> Dict[str, Any]:
        """Lấy thông tin về các mapping rules đang được sử dụng"""
        mappings_list = self.mappings.get("latex_to_calculator_mappings", [])
        metadata = self.mappings.get("metadata", {})
        
        return {
            "total_mappings": len(mappings_list),
            "mappings": mappings_list,
            "metadata": metadata,
            "source_file": self.mapping_file,
            "complex_fraction_support": True  # NEW feature flag
        }
    
    def test_encoding(self, test_input: str) -> Dict[str, Any]:
        """Test encoding với một input và trả về các bước chi tiết
        ENHANCED: Shows complex fraction processing steps
        """
        result = test_input.replace(" ", "")
        steps = [{"step": 0, "input": test_input, "output": result, "rule": "Remove spaces"}]
        
        # Step 1: Complex fraction processing
        complex_fraction_pattern = r"\\frac\{((?:\{.*?\}|[^{}])+)\}\{((?:\{.*?\}|[^{}])+)\}"
        
        def process_complex_fraction(match):
            num = match.group(1)
            den = match.group(2)
            num_processed = self._process_nested_content(num)
            den_processed = self._process_nested_content(den)
            return f"{num_processed}a{den_processed}"
        
        changed = True
        iteration = 0
        while changed and iteration < 20:
            before = result
            result = re.sub(complex_fraction_pattern, process_complex_fraction, result)
            changed = result != before
            if changed:
                steps.append({
                    "step": len(steps),
                    "input": before,
                    "output": result,
                    "rule": f"Complex fraction iteration {iteration + 1}",
                    "description": "Process \\frac{{num}}{{den}} → numa den"
                })
            iteration += 1
        
        # Step 2: Other mappings
        mappings_list = self.mappings.get("latex_to_calculator_mappings", [])
        
        for idx, mapping in enumerate(mappings_list):
            find_pattern = mapping.get("find", "")
            replace_pattern = mapping.get("replace", "")
            mapping_type = mapping.get("type", "literal")
            description = mapping.get("description", "")
            
            if "frac" in description.lower():
                continue
            
            before = result
            
            if mapping_type == "regex":
                try:
                    result = re.sub(find_pattern, replace_pattern, result)
                except Exception:
                    pass
            else:
                result = result.replace(find_pattern, replace_pattern)
            
            if before != result:
                steps.append({
                    "step": len(steps),
                    "input": before,
                    "output": result,
                    "rule": f"{find_pattern} → {replace_pattern}",
                    "description": description
                })
        
        return {
            "original": test_input,
            "final": result,
            "steps": steps,
            "total_transformations": len(steps) - 1,
            "complex_fraction_iterations": iteration
        }
    
    def reload_mappings(self) -> bool:
        """Reload mappings từ file (hữu ích khi cập nhật config)"""
        try:
            self.mappings = self._load_mappings()
            return True
        except Exception as e:
            print(f"Error reloading mappings: {e}")
            return False


# ========== TESTING ==========
if __name__ == "__main__":
    encoder = PolynomialEncodingService()
    
    print("=== POLYNOMIAL ENCODING SERVICE TEST (ENHANCED) ===\n")
    
    # Test cases including complex fractions
    test_cases = [
        "-5",
        "sqrt(4)",
        "sin(pi/2)",
        "\\frac{1}{2}",
        "\\frac{9}{4}",  # NEW: Test case from user
        "sqrt{16}",
        "cos(0)",
        "ln(e)",
        "-sqrt(25)",
        "2*3",
        "10/5",
        "\\frac{\\sqrt{2}}{3}",  # Complex fraction with sqrt
        "\\frac{-5}{2}",  # Fraction with negative numerator
    ]
    
    print("--- Basic Encoding Tests ---")
    for test in test_cases:
        encoded = encoder.encode_coefficient(test)
        print(f"'{test}' → '{encoded}'")
    
    print("\n--- Detailed Test: \\frac{9}{4} ---")
    test_input = "\\frac{9}{4}"
    result = encoder.test_encoding(test_input)
    print(f"Original: {result['original']}")
    print(f"Final: {result['final']}")
    print(f"Total transformations: {result['total_transformations']}")
    print(f"Complex fraction iterations: {result['complex_fraction_iterations']}")
    print("\nSteps:")
    for step in result['steps']:
        if step['step'] > 0:
            print(f"  Step {step['step']}: {step['input']} → {step['output']}")
            print(f"           Rule: {step['rule']}")
            if 'description' in step:
                print(f"           Description: {step['description']}")
    
    print("\n--- Coefficient List Encoding ---")
    coeffs = ["1", "\\frac{9}{4}", "sqrt(4)"]
    encoded_coeffs = encoder.encode_coefficients(coeffs)
    print(f"Input: {coeffs}")
    print(f"Encoded: {encoded_coeffs}")
    
    print("\n--- Mapping Info ---")
    info = encoder.get_mapping_info()
    print(f"Total mappings: {info['total_mappings']}")
    print(f"Complex fraction support: {info['complex_fraction_support']}")
    print(f"Metadata: {info['metadata']}")
    
    print("\n=== TEST COMPLETED ===")
