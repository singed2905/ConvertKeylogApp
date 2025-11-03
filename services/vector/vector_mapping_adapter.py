"""Vector Mapping Adapter - Expression encoding adapter for vector components
Converts mathematical expressions to calculator-compatible keylog format
"""
import re
import json
import os
from typing import Dict, Any, List, Optional


class VectorMappingAdapter:
    """Adapter for encoding vector expressions to calculator format"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Default mappings - can be overridden by config
        self.math_expression_mappings = [
            {
                "find": r"\\sqrt\{([^{}]+)\}",
                "replace": r"s\1)",
                "type": "regex",
                "description": "Square root \\sqrt{x} → s(x)"
            },
            {
                "find": r"sqrt\(([^)]+)\)",
                "replace": r"s\1)",
                "type": "regex",
                "description": "Square root sqrt(x) → s(x)"
            },
            {
                "find": r"\-",
                "replace": "p",
                "type": "regex",
                "description": "Negative sign → p"
            },
            {
                "find": r"\*",
                "replace": "O",
                "type": "regex",
                "description": "Multiplication * → O"
            },
            {
                "find": r"\/",
                "replace": "P",
                "type": "regex",
                "description": "Division / → P"
            },
            {
                "find": r"\\pi",
                "replace": "π",
                "type": "regex",
                "description": "Pi symbol \\pi → π"
            },
            {
                "find": "pi",
                "replace": "π",
                "type": "string",
                "description": "Pi constant pi → π"
            },
            {
                "find": r"\\sin\(",
                "replace": "j(",
                "type": "regex",
                "description": "Sine function \\sin( → j("
            },
            {
                "find": r"sin\(",
                "replace": "j(",
                "type": "regex",
                "description": "Sine function sin( → j("
            },
            {
                "find": r"\\cos\(",
                "replace": "k(",
                "type": "regex",
                "description": "Cosine function \\cos( → k("
            },
            {
                "find": r"cos\(",
                "replace": "k(",
                "type": "regex",
                "description": "Cosine function cos( → k("
            },
            {
                "find": r"\\tan\(",
                "replace": "l(",
                "type": "regex",
                "description": "Tangent function \\tan( → l("
            },
            {
                "find": r"tan\(",
                "replace": "l(",
                "type": "regex",
                "description": "Tangent function tan( → l("
            },
            {
                "find": r"\\ln\(",
                "replace": "h(",
                "type": "regex",
                "description": "Natural log \\ln( → h("
            },
            {
                "find": r"ln\(",
                "replace": "h(",
                "type": "regex",
                "description": "Natural log ln( → h("
            },
            {
                "find": r"\^",
                "replace": "^",
                "type": "regex",
                "description": "Power operator ^ preserved"
            }
        ]
        
        # Math function replacements
        self.math_function_replacements = {
            "operators": {
                "^": {
                    "python_equivalent": "**",
                    "description": "Power operator for evaluation",
                    "encoding": "^",
                    "category": "arithmetic"
                },
                "*": {
                    "python_equivalent": "*",
                    "description": "Multiplication operator",
                    "encoding": "O",
                    "category": "arithmetic"
                },
                "/": {
                    "python_equivalent": "/",
                    "description": "Division operator",
                    "encoding": "P",
                    "category": "arithmetic"
                },
                "+": {
                    "python_equivalent": "+",
                    "description": "Addition operator",
                    "encoding": "+",
                    "category": "arithmetic"
                },
                "-": {
                    "python_equivalent": "-",
                    "description": "Subtraction operator",
                    "encoding": "p",
                    "category": "arithmetic"
                }
            },
            "functions": {
                "sqrt": {
                    "python_equivalent": "math.sqrt",
                    "description": "Square root function",
                    "encoding": "s",
                    "category": "algebraic"
                },
                "sin": {
                    "python_equivalent": "math.sin",
                    "description": "Sine trigonometric function",
                    "encoding": "j",
                    "category": "trigonometric"
                },
                "cos": {
                    "python_equivalent": "math.cos",
                    "description": "Cosine trigonometric function",
                    "encoding": "k",
                    "category": "trigonometric"
                },
                "tan": {
                    "python_equivalent": "math.tan",
                    "description": "Tangent trigonometric function",
                    "encoding": "l",
                    "category": "trigonometric"
                },
                "ln": {
                    "python_equivalent": "math.log",
                    "description": "Natural logarithm function",
                    "encoding": "h",
                    "category": "logarithmic"
                },
                "log": {
                    "python_equivalent": "math.log10",
                    "description": "Base-10 logarithm function",
                    "encoding": "log",
                    "category": "logarithmic"
                },
                "abs": {
                    "python_equivalent": "abs",
                    "description": "Absolute value function",
                    "encoding": "abs",
                    "category": "algebraic"
                }
            },
            "constants": {
                "pi": {
                    "python_equivalent": "math.pi",
                    "description": "Pi mathematical constant",
                    "encoding": "π",
                    "value": 3.141592653589793
                },
                "e": {
                    "python_equivalent": "math.e",
                    "description": "Euler's number mathematical constant",
                    "encoding": "e",
                    "value": 2.718281828459045
                }
            }
        }
        
        # Vector-specific operations
        self.vector_specific_operations = {
            "dot_product_symbol": {
                "input": ["•", ".", "*"],
                "encoding": "DOT",
                "description": "Dot product operation symbol"
            },
            "cross_product_symbol": {
                "input": ["×", "x", "cross"],
                "encoding": "CROSS",
                "description": "Cross product operation symbol"
            },
            "magnitude_symbol": {
                "input": ["|", "mag", "length"],
                "encoding": "MAG",
                "description": "Vector magnitude/length"
            }
        }
        
        # Load config if available
        self._load_config()
    
    def _load_config(self):
        """Load configuration from config files"""
        try:
            vector_config = self.config.get('vector_mode', {})
            
            # Load mappings if available
            if 'math_expression_mappings' in vector_config:
                self.math_expression_mappings = vector_config['math_expression_mappings']
                print("Vector mappings loaded from config")
            
            if 'math_function_replacements' in vector_config:
                self.math_function_replacements = vector_config['math_function_replacements']
                print("Vector function replacements loaded from config")
            
            if 'vector_specific_operations' in vector_config:
                self.vector_specific_operations = vector_config['vector_specific_operations']
                print("Vector specific operations loaded from config")
                
        except Exception as e:
            print(f"Warning: Could not load vector mapping config: {e}")
    
    # ========== MAIN ENCODING METHODS ==========
    def encode_scalar(self, value_str: str) -> str:
        """Encode scalar expression to calculator format"""
        if not value_str or not value_str.strip():
            return "0"
        
        encoded = value_str.strip()
        
        # Apply math expression mappings
        encoded = self.apply_math_expression_mappings(encoded)
        
        # Apply function replacements for encoding
        encoded = self.apply_function_replacements_for_encoding(encoded)
        
        # Handle special cases
        encoded = self.handle_special_cases(encoded)
        
        return encoded
    
    def encode_vector(self, components: List[str]) -> List[str]:
        """Encode vector components"""
        return [self.encode_scalar(comp) for comp in components]
    
    def apply_math_expression_mappings(self, expression: str) -> str:
        """Apply math expression mappings from config"""
        result = expression
        
        for mapping in self.math_expression_mappings:
            find_pattern = mapping["find"]
            replace_pattern = mapping["replace"]
            mapping_type = mapping["type"]
            
            try:
                if mapping_type == "regex":
                    result = re.sub(find_pattern, replace_pattern, result)
                elif mapping_type == "string":
                    result = result.replace(find_pattern, replace_pattern)
            except Exception as e:
                print(f"Warning: Error applying mapping {mapping['description']}: {e}")
                continue
        
        return result
    
    def apply_function_replacements_for_encoding(self, expression: str) -> str:
        """Apply function replacements for encoding (not evaluation)"""
        result = expression
        
        # Replace functions with their encoding
        functions = self.math_function_replacements["functions"]
        for func_name, func_info in functions.items():
            encoding = func_info["encoding"]
            # Replace function name with encoding
            result = re.sub(r'\b' + re.escape(func_name) + r'\(', encoding + '(', result)
        
        # Replace constants with their encoding
        constants = self.math_function_replacements["constants"]
        for const_name, const_info in constants.items():
            encoding = const_info["encoding"]
            result = re.sub(r'\b' + re.escape(const_name) + r'\b', encoding, result)
        
        # Replace operators with their encoding
        operators = self.math_function_replacements["operators"]
        for op_symbol, op_info in operators.items():
            encoding = op_info["encoding"]
            if op_symbol in ["+", "-", "*", "/", "^"]:
                # Handle special operator replacements
                if op_symbol == "-" and self.is_negative_sign(result, op_symbol):
                    result = result.replace(op_symbol, encoding)
                elif op_symbol in ["*", "/"]:
                    result = result.replace(op_symbol, encoding)
                # Note: + and ^ are preserved as-is based on encoding config
        
        return result
    
    def handle_special_cases(self, expression: str) -> str:
        """Handle special encoding cases"""
        result = expression
        
        # Handle negative numbers (only at start or after operators)
        result = re.sub(r'^-', 'p', result)  # Negative at start
        result = re.sub(r'([+\-*/^(,])-', r'\1p', result)  # Negative after operators
        
        # Preserve decimal points
        # (Already preserved - no special handling needed)
        
        # Handle parentheses (preserved as-is)
        # (Already preserved - no special handling needed)
        
        return result
    
    def is_negative_sign(self, expression: str, minus_pos: str) -> bool:
        """Check if minus sign is a negative sign (not subtraction)"""
        # Simple heuristic: if minus is at start or after (, +, -, *, /, ^, comma
        minus_index = expression.find(minus_pos)
        if minus_index == 0:
            return True
        if minus_index > 0:
            prev_char = expression[minus_index - 1]
            return prev_char in ['(', '+', '-', '*', '/', '^', ',', ' ']
        return False
    
    # ========== UTILITY METHODS ==========
    def get_encoding_info(self, expression: str) -> Dict[str, Any]:
        """Get detailed encoding information for debugging"""
        steps = []
        current = expression
        
        # Step 1: Original
        steps.append({"step": "original", "value": current})
        
        # Step 2: Math expression mappings
        after_mappings = self.apply_math_expression_mappings(current)
        if after_mappings != current:
            steps.append({"step": "math_mappings", "value": after_mappings})
            current = after_mappings
        
        # Step 3: Function replacements
        after_functions = self.apply_function_replacements_for_encoding(current)
        if after_functions != current:
            steps.append({"step": "function_replacements", "value": after_functions})
            current = after_functions
        
        # Step 4: Special cases
        after_special = self.handle_special_cases(current)
        if after_special != current:
            steps.append({"step": "special_cases", "value": after_special})
            current = after_special
        
        # Final result
        steps.append({"step": "final", "value": current})
        
        return {
            "original": expression,
            "final": current,
            "steps": steps,
            "mappings_applied": len(steps) - 2  # Exclude original and final
        }
    
    def validate_encoding(self, original: str, encoded: str) -> Dict[str, Any]:
        """Validate encoding result"""
        validation = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check for common issues
        if not encoded:
            validation["errors"].append("Encoded result is empty")
            validation["valid"] = False
        
        if encoded == original:
            validation["warnings"].append("No encoding changes applied")
        
        # Check for unhandled mathematical functions
        unhandled_functions = re.findall(r'\b(asin|acos|atan|sinh|cosh|tanh)\(', encoded)
        if unhandled_functions:
            validation["warnings"].append(f"Unhandled functions: {unhandled_functions}")
        
        return validation
    
    def get_supported_functions(self) -> List[str]:
        """Get list of supported mathematical functions"""
        functions = list(self.math_function_replacements["functions"].keys())
        constants = list(self.math_function_replacements["constants"].keys())
        return functions + constants
    
    def get_encoding_examples(self) -> List[Dict[str, str]]:
        """Get examples of encoding transformations"""
        examples = [
            {"input": "sqrt(2)", "output": self.encode_scalar("sqrt(2)"), "description": "Square root"},
            {"input": "sin(pi/2)", "output": self.encode_scalar("sin(pi/2)"), "description": "Sine with pi"},
            {"input": "-3.14", "output": self.encode_scalar("-3.14"), "description": "Negative number"},
            {"input": "2*cos(pi/4)", "output": self.encode_scalar("2*cos(pi/4)"), "description": "Multiplication with cosine"},
            {"input": "ln(e)", "output": self.encode_scalar("ln(e)"), "description": "Natural log of e"},
            {"input": "tan(pi/6)", "output": self.encode_scalar("tan(pi/6)"), "description": "Tangent function"}
        ]
        return examples


# ========== TESTING ==========
if __name__ == "__main__":
    # Test the adapter
    adapter = VectorMappingAdapter()
    
    print("=== Vector Mapping Adapter Test ===")
    
    # Test examples
    test_expressions = [
        "sqrt(2)",
        "sin(pi/2)",
        "-3.14",
        "2*cos(pi/4)", 
        "ln(e)",
        "tan(pi/6)",
        "1/2",
        "2^3"
    ]
    
    print("\n--- Encoding Examples ---")
    for expr in test_expressions:
        encoded = adapter.encode_scalar(expr)
        print(f"{expr:15} → {encoded}")
    
    print("\n--- Detailed Encoding Info ---")
    test_expr = "2*sin(pi/4)"
    info = adapter.get_encoding_info(test_expr)
    print(f"Expression: {test_expr}")
    print(f"Final: {info['final']}")
    print("Steps:")
    for step in info['steps']:
        print(f"  {step['step']:20} : {step['value']}")
    
    print("\n--- Vector Encoding ---")
    vector_components = ["1", "sqrt(2)", "-pi/2"]
    encoded_vector = adapter.encode_vector(vector_components)
    print(f"Original: {vector_components}")
    print(f"Encoded:  {encoded_vector}")
    
    print("\n--- Supported Functions ---")
    functions = adapter.get_supported_functions()
    print(f"Supported: {', '.join(functions)}")