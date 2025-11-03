"""Vector Service - Complete service for vector calculations and keylog encoding
Integrates vector mathematics, expression parsing, and keylog generation with fixed values
"""
import math
import json
import os
from typing import List, Tuple, Dict, Any, Optional, Union
from .vector_mapping_adapter import VectorMappingAdapter


class VectorService:
    """Complete Vector Service với fixed values system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize components
        self.mapping_adapter = VectorMappingAdapter(config)
        
        # Current state
        self.current_calculation_type = "scalar_vector"  # "scalar_vector" or "vector_vector"
        self.current_dimension = 2  # 2 or 3
        self.current_operation = ""
        self.current_version = "fx799"
        
        # Input data
        self.scalar_value = ""  # Raw input string
        self.vector_A = []  # List of raw component strings
        self.vector_B = []  # List of raw component strings
        
        # Processed data
        self.parsed_scalar = 0.0
        self.parsed_vector_A = []  # List of floats
        self.parsed_vector_B = []  # List of floats
        
        # Results
        self.calculation_result = None
        self.encoded_scalar = ""
        self.encoded_vector_A = []
        self.encoded_vector_B = []
        self.final_keylog = ""
        
        # Fixed values system
        self.operation_fixed_values = {
            "scalar_vector": {
                "multiply": {"fixed_value": "1", "description": "Default multiplier"},
                "divide": {"fixed_value": "1", "description": "Default divisor"},
                "add": {"fixed_value": "0", "description": "Default addend"},
                "subtract": {"fixed_value": "0", "description": "Default subtrahend"}
            },
            "vector_vector": {
                "dot_product": {"fixed_value": "DOT", "description": "Dot product identifier"},
                "cross_product": {"fixed_value": "CROSS", "description": "Cross product identifier"},
                "add": {"fixed_value": "ADD", "description": "Vector addition identifier"},
                "subtract": {"fixed_value": "SUB", "description": "Vector subtraction identifier"},
                "angle": {"fixed_value": "ANG", "description": "Angle calculation identifier"},
                "distance": {"fixed_value": "DIST", "description": "Distance calculation identifier"}
            }
        }
        
        # Operation codes
        self.operation_codes = {
            "scalar_vector": {
                "multiply": "qV1",
                "divide": "qV2",
                "add": "qV3",
                "subtract": "qV4"
            },
            "vector_vector": {
                "dot_product": "qV5",
                "cross_product": "qV6",
                "add": "qV7",
                "subtract": "qV8",
                "angle": "qV9",
                "distance": "qV10"
            }
        }
        
        # Load config if available
        self._load_config()
    
    def _load_config(self):
        """Load configuration from config files"""
        try:
            # Try to load fixed values from config
            vector_config = self.config.get('vector_mode', {})
            if 'operation_fixed_values' in vector_config:
                self.operation_fixed_values = vector_config['operation_fixed_values']
                print("Vector config loaded: Fixed values from config")
        except Exception as e:
            print(f"Warning: Could not load vector config: {e}")
    
    # ========== CONFIGURATION SETTERS ==========
    def set_calculation_type(self, calc_type: str):
        """Set calculation type: 'scalar_vector' or 'vector_vector'"""
        if calc_type in ["scalar_vector", "vector_vector"]:
            self.current_calculation_type = calc_type
        else:
            raise ValueError("Calculation type must be 'scalar_vector' or 'vector_vector'")
    
    def set_dimension(self, dimension: int):
        """Set vector dimension: 2 or 3"""
        if dimension in [2, 3]:
            self.current_dimension = dimension
        else:
            raise ValueError("Dimension must be 2 or 3")
    
    def set_operation(self, operation: str):
        """Set current operation"""
        self.current_operation = operation
    
    def set_version(self, version: str):
        """Set calculator version"""
        self.current_version = version
    
    # ========== INPUT PROCESSING ==========
    def process_scalar_input(self, scalar_str: str):
        """Process scalar input string"""
        self.scalar_value = scalar_str.strip()
        try:
            self.parsed_scalar = self.parse_expression(scalar_str)
            self.encoded_scalar = self.mapping_adapter.encode_scalar(scalar_str)
            return True
        except Exception as e:
            print(f"Error processing scalar input: {e}")
            return False
    
    def process_vector_A(self, vector_str: str):
        """Process vector A input string"""
        try:
            components = [comp.strip() for comp in vector_str.split(',')]
            if len(components) != self.current_dimension:
                raise ValueError(f"Vector A needs {self.current_dimension} components, got {len(components)}")
            
            self.vector_A = components
            self.parsed_vector_A = [self.parse_expression(comp) for comp in components]
            self.encoded_vector_A = [self.mapping_adapter.encode_scalar(comp) for comp in components]
            return True
        except Exception as e:
            print(f"Error processing vector A: {e}")
            return False
    
    def process_vector_B(self, vector_str: str):
        """Process vector B input string"""
        try:
            components = [comp.strip() for comp in vector_str.split(',')]
            if len(components) != self.current_dimension:
                raise ValueError(f"Vector B needs {self.current_dimension} components, got {len(components)}")
            
            self.vector_B = components
            self.parsed_vector_B = [self.parse_expression(comp) for comp in components]
            self.encoded_vector_B = [self.mapping_adapter.encode_scalar(comp) for comp in components]
            return True
        except Exception as e:
            print(f"Error processing vector B: {e}")
            return False
    
    def parse_expression(self, expr: str) -> float:
        """Parse mathematical expression to float"""
        if not expr or not expr.strip():
            return 0.0
        
        expr = str(expr).strip()
        
        # Handle simple numbers first
        try:
            return float(expr)
        except ValueError:
            pass
        
        # Replace mathematical expressions
        replacements = {
            'pi': 'math.pi',
            'e': 'math.e',
            'sqrt': 'math.sqrt',
            'sin': 'math.sin',
            'cos': 'math.cos',
            'tan': 'math.tan',
            'log': 'math.log10',
            'ln': 'math.log',
            '^': '**',
        }
        
        # Apply replacements
        import re
        for old, new in replacements.items():
            if old in ['^']:
                expr = expr.replace(old, new)
            else:
                expr = re.sub(r'\b' + re.escape(old) + r'\b', new, expr)
        
        # Safe evaluation
        try:
            safe_dict = {"__builtins__": {}, "math": math}
            result = eval(expr, safe_dict)
            return float(result)
        except Exception:
            try:
                return float(expr)
            except Exception:
                return 0.0
    
    # ========== CALCULATIONS ==========
    def calculate_scalar_vector_operation(self, operation: str):
        """Perform scalar-vector operation"""
        if operation == "multiply":
            result_vector = [self.parsed_scalar * v for v in self.parsed_vector_A]
            calc_result = f"{self.parsed_scalar} × {self.format_vector(self.parsed_vector_A)} = {self.format_vector(result_vector)}"
        elif operation == "divide":
            if abs(self.parsed_scalar) < 1e-12:
                raise ValueError("Cannot divide by zero")
            result_vector = [v / self.parsed_scalar for v in self.parsed_vector_A]
            calc_result = f"{self.format_vector(self.parsed_vector_A)} ÷ {self.parsed_scalar} = {self.format_vector(result_vector)}"
        elif operation == "add":
            result_vector = [v + self.parsed_scalar for v in self.parsed_vector_A]
            calc_result = f"{self.format_vector(self.parsed_vector_A)} + {self.parsed_scalar} = {self.format_vector(result_vector)}"
        elif operation == "subtract":
            result_vector = [v - self.parsed_scalar for v in self.parsed_vector_A]
            calc_result = f"{self.format_vector(self.parsed_vector_A)} - {self.parsed_scalar} = {self.format_vector(result_vector)}"
        else:
            raise ValueError(f"Unknown scalar-vector operation: {operation}")
        
        self.calculation_result = {
            'type': 'vector',
            'result': result_vector,
            'display': calc_result
        }
        return calc_result
    
    def calculate_vector_vector_operation(self, operation: str):
        """Perform vector-vector operation"""
        if operation == "dot_product":
            result = sum(a * b for a, b in zip(self.parsed_vector_A, self.parsed_vector_B))
            calc_result = f"{self.format_vector(self.parsed_vector_A)} • {self.format_vector(self.parsed_vector_B)} = {result:.4f}"
            result_type = 'scalar'
        elif operation == "cross_product":
            if self.current_dimension != 3:
                raise ValueError("Cross product only available for 3D vectors")
            result = self.cross_product_3d(self.parsed_vector_A, self.parsed_vector_B)
            calc_result = f"{self.format_vector(self.parsed_vector_A)} × {self.format_vector(self.parsed_vector_B)} = {self.format_vector(result)}"
            result_type = 'vector'
        elif operation == "add":
            result = [a + b for a, b in zip(self.parsed_vector_A, self.parsed_vector_B)]
            calc_result = f"{self.format_vector(self.parsed_vector_A)} + {self.format_vector(self.parsed_vector_B)} = {self.format_vector(result)}"
            result_type = 'vector'
        elif operation == "subtract":
            result = [a - b for a, b in zip(self.parsed_vector_A, self.parsed_vector_B)]
            calc_result = f"{self.format_vector(self.parsed_vector_A)} - {self.format_vector(self.parsed_vector_B)} = {self.format_vector(result)}"
            result_type = 'vector'
        elif operation == "angle":
            import math
            dot = sum(a * b for a, b in zip(self.parsed_vector_A, self.parsed_vector_B))
            mag_a = math.sqrt(sum(a * a for a in self.parsed_vector_A))
            mag_b = math.sqrt(sum(b * b for b in self.parsed_vector_B))
            if mag_a * mag_b == 0:
                raise ValueError("Cannot calculate angle with zero vector")
            cos_theta = dot / (mag_a * mag_b)
            cos_theta = max(-1, min(1, cos_theta))  # Clamp to [-1, 1]
            angle_rad = math.acos(cos_theta)
            angle_deg = math.degrees(angle_rad)
            result = angle_deg
            calc_result = f"Angle between {self.format_vector(self.parsed_vector_A)} and {self.format_vector(self.parsed_vector_B)} = {angle_deg:.2f}°"
            result_type = 'scalar'
        elif operation == "distance":
            import math
            diff = [a - b for a, b in zip(self.parsed_vector_A, self.parsed_vector_B)]
            result = math.sqrt(sum(d * d for d in diff))
            calc_result = f"Distance between {self.format_vector(self.parsed_vector_A)} and {self.format_vector(self.parsed_vector_B)} = {result:.4f}"
            result_type = 'scalar'
        else:
            raise ValueError(f"Unknown vector-vector operation: {operation}")
        
        self.calculation_result = {
            'type': result_type,
            'result': result,
            'display': calc_result
        }
        return calc_result
    
    def cross_product_3d(self, a: List[float], b: List[float]) -> List[float]:
        """Calculate cross product for 3D vectors"""
        return [
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]
        ]
    
    def format_vector(self, vector: List[float]) -> str:
        """Format vector for display"""
        formatted = [f"{v:.3f}".rstrip('0').rstrip('.') for v in vector]
        return f"({', '.join(formatted)})"
    
    # ========== KEYLOG GENERATION ==========
    def get_operation_processing_string(self, calc_type: str, operation: str) -> str:
        """Generate processing string with operation code and fixed value"""
        op_code = self.operation_codes[calc_type][operation]
        fixed_value = self.operation_fixed_values[calc_type][operation]["fixed_value"]
        
        if calc_type == "scalar_vector":
            # Include encoded scalar in processing string
            return f"{self.encoded_scalar}{op_code}{fixed_value}"
        else:
            # Just operation code and fixed value
            return f"{op_code}{fixed_value}"
    
    def get_vector_prefix(self, version: str) -> str:
        """Get vector prefix for specified version"""
        # Default prefixes (can be loaded from config)
        prefixes = {
            "fx799": "wv",
            "fx991": "VEC",
            "fx570": "V"
        }
        return prefixes.get(version, "wv")
    
    def generate_final_keylog(self) -> str:
        """Generate final keylog with fixed values system"""
        try:
            calc_type = self.current_calculation_type
            version = self.current_version
            operation = self.current_operation
            
            # Get prefix
            prefix = self.get_vector_prefix(version)
            
            # Encode vector A
            vectorA_encoded = "=".join(self.encoded_vector_A) + "="
            
            # Get processing string with fixed values
            processing_string = self.get_operation_processing_string(calc_type, operation)
            
            if calc_type == "scalar_vector":
                # Format: prefix + vectorA + C + {scalar+operation+fixed} + =
                self.final_keylog = f"{prefix}{vectorA_encoded}C{processing_string}="
            else:
                # Format: prefix + vectorA + C + vectorB + C + {operation+fixed} + =
                vectorB_encoded = "=".join(self.encoded_vector_B) + "="
                self.final_keylog = f"{prefix}{vectorA_encoded}C{vectorB_encoded}C{processing_string}="
            
            return self.final_keylog
            
        except Exception as e:
            print(f"Error generating keylog: {e}")
            return f"ERROR: {str(e)}"
    
    # ========== MAIN WORKFLOW ==========
    def process_complete_workflow(self) -> Tuple[bool, str, Dict[str, Any]]:
        """Complete workflow: validate -> calculate -> encode -> generate keylog"""
        try:
            # Validate inputs
            if not self.validate_inputs():
                return False, "Invalid inputs", {}
            
            # Perform calculation
            if self.current_calculation_type == "scalar_vector":
                calc_display = self.calculate_scalar_vector_operation(self.current_operation)
            else:
                calc_display = self.calculate_vector_vector_operation(self.current_operation)
            
            # Generate keylog
            keylog = self.generate_final_keylog()
            
            # Prepare result
            result = {
                'calculation_display': calc_display,
                'encoded_scalar': self.encoded_scalar,
                'encoded_vector_A': self.encoded_vector_A,
                'encoded_vector_B': self.encoded_vector_B,
                'final_keylog': keylog,
                'calculation_result': self.calculation_result,
                'fixed_value': self.operation_fixed_values[self.current_calculation_type][self.current_operation]
            }
            
            return True, "Success", result
            
        except Exception as e:
            return False, f"Processing error: {str(e)}", {}
    
    def validate_inputs(self) -> bool:
        """Validate current inputs"""
        try:
            # Check operation
            if not self.current_operation:
                return False
            
            # Check vector A
            if not self.vector_A or len(self.vector_A) != self.current_dimension:
                return False
            
            # Check scalar for scalar_vector operations
            if self.current_calculation_type == "scalar_vector" and not self.scalar_value:
                return False
            
            # Check vector B for vector_vector operations
            if (self.current_calculation_type == "vector_vector" and 
                (not self.vector_B or len(self.vector_B) != self.current_dimension)):
                return False
            
            return True
            
        except Exception:
            return False
    
    # ========== UTILITY METHODS ==========
    def reset_state(self):
        """Reset service state"""
        self.scalar_value = ""
        self.vector_A = []
        self.vector_B = []
        self.parsed_scalar = 0.0
        self.parsed_vector_A = []
        self.parsed_vector_B = []
        self.calculation_result = None
        self.encoded_scalar = ""
        self.encoded_vector_A = []
        self.encoded_vector_B = []
        self.final_keylog = ""
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            'calculation_type': self.current_calculation_type,
            'dimension': self.current_dimension,
            'operation': self.current_operation,
            'version': self.current_version,
            'has_result': self.calculation_result is not None,
            'fixed_values_loaded': bool(self.operation_fixed_values)
        }


# ========== CUSTOM EXCEPTIONS ==========
class VectorServiceError(Exception):
    """Custom exception for Vector Service errors"""
    pass


class VectorValidationError(Exception):
    """Custom exception for Vector validation errors"""
    pass


# ========== TESTING ==========
if __name__ == "__main__":
    # Test basic functionality
    service = VectorService()
    
    print("=== Testing Scalar-Vector ===")
    service.set_calculation_type("scalar_vector")
    service.set_dimension(2)
    service.set_operation("multiply")
    service.set_version("fx799")
    
    service.process_scalar_input("3")
    service.process_vector_A("1,2")
    
    success, message, result = service.process_complete_workflow()
    print(f"Success: {success}")
    print(f"Message: {message}")
    if success:
        print(f"Calculation: {result['calculation_display']}")
        print(f"Final Keylog: {result['final_keylog']}")
    
    print("\n=== Testing Vector-Vector ===")
    service.reset_state()
    service.set_calculation_type("vector_vector")
    service.set_dimension(3)
    service.set_operation("dot_product")
    
    service.process_vector_A("1,2,3")
    service.process_vector_B("4,5,6")
    
    success, message, result = service.process_complete_workflow()
    print(f"Success: {success}")
    if success:
        print(f"Calculation: {result['calculation_display']}")
        print(f"Final Keylog: {result['final_keylog']}")
        print(f"Fixed Value: {result['fixed_value']['description']}") 