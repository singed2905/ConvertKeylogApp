"""Polynomial Service - Main service orchestrating polynomial solving and encoding
Integrates solver, encoder, config management for complete workflow
"""
from typing import List, Tuple, Dict, Any, Optional
from .polynomial_solver import PolynomialSolver, PolynomialValidationError, PolynomialSolvingError


class PolynomialService:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize components
        self.solver = PolynomialSolver()
        self.degree = 2  # Default degree
        self.version = "fx799"  # Default calculator version
        
        # Load config settings
        self._load_config()
        
        # State tracking
        self.last_coefficients_raw = []
        self.last_coefficients_numeric = []
        self.last_roots = []
        self.last_encoded_coefficients = []
        self.last_final_keylog = ""
    
    def _load_config(self):
        """Load configuration for polynomial service"""
        try:
            poly_config = self.config.get('polynomial', {})
            
            # Solver settings
            solver_config = poly_config.get('solver', {})
            method = solver_config.get('method', 'numpy')
            precision = solver_config.get('precision', 6)
            
            self.solver.set_method(method)
            self.solver.set_precision(precision)
            
            print(f"Polynomial config loaded: method={method}, precision={precision}")
            
        except Exception as e:
            print(f"Warning: Could not load polynomial config: {e}")
            # Use defaults already set
    
    # ========== CONFIGURATION SETTERS ==========
    def set_degree(self, degree: int):
        """Set polynomial degree (2, 3, or 4)"""
        if degree not in [2, 3, 4]:
            raise ValueError("Degree must be 2, 3, or 4")
        self.degree = degree
    
    def set_version(self, version: str):
        """Set calculator version for encoding"""
        self.version = version
    
    def set_solver_method(self, method: str):
        """Set solver method: 'numpy' or 'analytical'"""
        self.solver.set_method(method)
    
    def set_precision(self, precision: int):
        """Set decimal precision for results"""
        self.solver.set_precision(precision)
    
    # ========== INPUT VALIDATION ==========
    def validate_input(self, coefficient_inputs: List[str]) -> Tuple[bool, str]:
        """Validate polynomial coefficient inputs"""
        try:
            expected_count = self.degree + 1
            
            if len(coefficient_inputs) != expected_count:
                return False, f"Need exactly {expected_count} coefficients for degree {self.degree} polynomial"
            
            # Check if all inputs are empty
            if all(not coeff.strip() for coeff in coefficient_inputs):
                return False, "All coefficient fields are empty"
            
            # Try parsing to check validity
            coeffs, parse_ok = self.solver.parse_coefficients(coefficient_inputs)
            if not parse_ok:
                return False, "Cannot parse one or more coefficient expressions"
            
            # Validate polynomial structure
            valid, msg = self.solver.validate_polynomial(coeffs, self.degree)
            if not valid:
                return False, msg
            
            return True, "Valid input"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    # ========== MAIN PROCESSING WORKFLOW ==========
    def process_complete_workflow(self, coefficient_inputs: List[str]) -> Tuple[bool, str, str, str]:
        """
        Complete workflow: validate -> solve -> encode -> format
        Returns: (success, status_msg, roots_display, final_keylog)
        """
        try:
            # Step 1: Validate
            valid, validation_msg = self.validate_input(coefficient_inputs)
            if not valid:
                return False, validation_msg, "", ""
            
            # Step 2: Solve polynomial
            success, solve_msg, roots, roots_display = self.solver.solve_polynomial(
                coefficient_inputs, self.degree
            )
            if not success:
                return False, solve_msg, "", ""
            
            # Step 3: Store results
            self.last_coefficients_raw = coefficient_inputs.copy()
            coeffs, _ = self.solver.parse_coefficients(coefficient_inputs)
            self.last_coefficients_numeric = coeffs
            self.last_roots = roots
            
            # Step 4: Encode coefficients and generate keylog 
            encoded_coeffs = self._encode_coefficients(coefficient_inputs)
            final_keylog = self._generate_final_keylog(encoded_coeffs)
            
            self.last_encoded_coefficients = encoded_coeffs
            self.last_final_keylog = final_keylog
            
            return True, "Processing completed successfully", roots_display, final_keylog
            
        except Exception as e:
            return False, f"Processing error: {str(e)}", "", ""
    
    # ========== ENCODING METHODS ==========
    def _encode_coefficients(self, raw_coefficients: List[str]) -> List[str]:
        """Encode coefficient expressions to calculator keylog format"""
        try:
            # For MVP: simple placeholder encoding
            # TODO: Implement proper PolynomialEncodingService integration
            encoded = []
            
            for coeff in raw_coefficients:
                if not coeff or not coeff.strip():
                    encoded.append("0")
                else:
                    # Simple encoding - replace common expressions
                    encoded_coeff = self._simple_encode_expression(coeff.strip())
                    encoded.append(encoded_coeff)
            
            return encoded
            
        except Exception as e:
            print(f"Encoding error: {e}")
            # Fallback: return raw coefficients
            return raw_coefficients.copy()
    
    def _simple_encode_expression(self, expr: str) -> str:
        """Simple expression encoding for MVP"""
        # Basic replacements for common expressions
        replacements = {
            'sqrt': '√',
            'pi': 'π',
            '^': '',  # Remove power operator for now
            'sin': 'sin',
            'cos': 'cos',
            'log': 'log',
            'ln': 'ln'
        }
        
        result = expr
        for old, new in replacements.items():
            result = result.replace(old, new)
        
        return result
    
    def _generate_final_keylog(self, encoded_coeffs: List[str]) -> str:
        """Generate final keylog string for calculator input"""
        try:
            # Get prefix for polynomial based on degree and version
            prefix = self._get_polynomial_prefix()
            
            # Join encoded coefficients
            coeffs_part = "=".join(encoded_coeffs)
            
            # Add suffix based on degree
            suffix = self._get_polynomial_suffix()
            
            # Combine parts
            final_keylog = f"{prefix}{coeffs_part}{suffix}"
            
            return final_keylog
            
        except Exception as e:
            print(f"Keylog generation error: {e}")
            return "KEYLOG_ERROR"
    
    def _get_polynomial_prefix(self) -> str:
        """Get prefix for polynomial keylog based on version and degree"""
        # TODO: Load from config based on version and degree
        prefix_map = {
            ("fx799", 2): "POLY2=",
            ("fx799", 3): "POLY3=", 
            ("fx799", 4): "POLY4=",
            ("fx991", 2): "EQN2=",
            ("fx991", 3): "EQN3=",
            ("fx991", 4): "EQN4=",
        }
        
        return prefix_map.get((self.version, self.degree), f"POLY{self.degree}=")
    
    def _get_polynomial_suffix(self) -> str:
        """Get suffix for polynomial keylog based on degree"""
        suffix_map = {
            2: "==",
            3: "===", 
            4: "===="
        }
        return suffix_map.get(self.degree, "==")
    
    # ========== GETTERS FOR UI ==========
    def get_last_roots(self) -> List[complex]:
        """Get last computed roots"""
        return self.last_roots.copy()
    
    def get_last_encoded_coefficients(self) -> List[str]:
        """Get last encoded coefficients for display"""
        return self.last_encoded_coefficients.copy()
    
    def get_last_final_keylog(self) -> str:
        """Get last generated keylog"""
        return self.last_final_keylog
    
    def get_real_roots_only(self) -> List[float]:
        """Get only real roots from last solution"""
        return self.solver.get_real_roots_only(self.last_roots)
    
    def get_polynomial_info(self) -> Dict[str, Any]:
        """Get detailed polynomial information"""
        if not self.last_coefficients_numeric:
            return {}
        
        info = self.solver.get_polynomial_info(self.last_coefficients_numeric, self.degree)
        info.update({
            "version": self.version,
            "solver_method": self.solver.method,
            "solver_precision": self.solver.precision,
            "has_results": bool(self.last_roots)
        })
        
        return info
    
    # ========== UTILITY METHODS ==========
    def reset_state(self):
        """Reset service state"""
        self.last_coefficients_raw = []
        self.last_coefficients_numeric = []
        self.last_roots = []
        self.last_encoded_coefficients = []
        self.last_final_keylog = ""
    
    def get_expected_coefficient_count(self) -> int:
        """Get expected number of coefficients for current degree"""
        return self.degree + 1
    
    def get_coefficient_labels(self) -> List[str]:
        """Get labels for coefficient inputs based on degree"""
        labels_map = {
            2: ["a (x²)", "b (x)", "c (constant)"],
            3: ["a (x³)", "b (x²)", "c (x)", "d (constant)"],
            4: ["a (x⁴)", "b (x³)", "c (x²)", "d (x)", "e (constant)"]
        }
        return labels_map.get(self.degree, labels_map[2])
    
    def get_polynomial_form_display(self) -> str:
        """Get polynomial form string for display"""
        forms = {
            2: "ax² + bx + c = 0",
            3: "ax³ + bx² + cx + d = 0", 
            4: "ax⁴ + bx³ + cx² + dx + e = 0"
        }
        return forms.get(self.degree, "Invalid degree")
    
    # ========== ERROR HANDLING ==========
    def get_last_error(self) -> Optional[str]:
        """Get last error message if any"""
        # TODO: Implement error tracking
        return None
    
    def is_service_ready(self) -> bool:
        """Check if service is ready for processing"""
        return self.solver is not None and self.degree in [2, 3, 4]


class PolynomialServiceError(Exception):
    """Custom exception for polynomial service errors"""
    pass


# ========== TESTING ==========
if __name__ == "__main__":
    # Test service with mock config
    config = {
        'polynomial': {
            'solver': {
                'method': 'numpy',
                'precision': 4
            }
        }
    }
    
    service = PolynomialService(config)
    
    # Test quadratic polynomial
    print("=== TEST POLYNOMIAL SERVICE ===")
    service.set_degree(2)
    service.set_version("fx799")
    
    # Test input: x² - 5x + 6 = 0
    success, msg, roots_display, keylog = service.process_complete_workflow(["1", "-5", "6"])
    
    print(f"Success: {success}")
    print(f"Message: {msg}")
    print(f"Roots Display:\n{roots_display}")
    print(f"Final Keylog: {keylog}")
    print(f"Encoded Coefficients: {service.get_last_encoded_coefficients()}")
    print(f"Polynomial Info: {service.get_polynomial_info()}")
    
    # Test with expressions
    print("\n=== TEST WITH EXPRESSIONS ===")
    success, msg, roots_display, keylog = service.process_complete_workflow(["1", "-sqrt(9)", "2"])
    print(f"Success: {success}")
    print(f"Keylog: {keylog}")
    
    # Test cubic
    print("\n=== TEST CUBIC ===")
    service.set_degree(3)
    success, msg, roots_display, keylog = service.process_complete_workflow(["1", "-6", "11", "-6"])
    print(f"Success: {success}")
    print(f"Roots Display:\n{roots_display}")
    print(f"Keylog: {keylog}")