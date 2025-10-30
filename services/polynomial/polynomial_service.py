"""Polynomial Service - Enhanced service orchestrating polynomial solving and encoding
Integrates enhanced solver with repeated roots detection, encoder, config management for complete workflow
"""
from typing import List, Tuple, Dict, Any, Optional
from .polynomial_solver import PolynomialSolver, PolynomialValidationError, PolynomialSolvingError
from .polynomial_prefix_resolver import PolynomialPrefixResolver


class PolynomialService:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize components
        self.solver = PolynomialSolver()
        self.prefix_resolver = PolynomialPrefixResolver()
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
        self.last_roots_display = ""
        self.last_compact_display = ""
    
    def _load_config(self):
        """Load configuration for polynomial service"""
        try:
            poly_config = self.config.get('polynomial', {})
            
            # Solver settings
            solver_config = poly_config.get('solver', {})
            method = solver_config.get('method', 'numpy')
            precision = solver_config.get('precision', 6)
            duplicate_threshold = solver_config.get('duplicate_threshold', 1e-8)
            
            self.solver.set_method(method)
            self.solver.set_precision(precision)
            self.solver.set_duplicate_threshold(duplicate_threshold)
            
            print(f"Polynomial config loaded: method={method}, precision={precision}, dup_threshold={duplicate_threshold}")
            
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
    
    def set_duplicate_threshold(self, threshold: float):
        """Set threshold for detecting repeated roots"""
        self.solver.set_duplicate_threshold(threshold)
    
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
            
            # Step 2: Solve polynomial with enhanced solver
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
            self.last_roots_display = roots_display
            self.last_compact_display = self.solver.get_compact_display(roots)
            
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
        """Generate final keylog string using PolynomialPrefixResolver"""
        try:
            # Use prefix resolver for proper keylog formatting
            final_keylog = self.prefix_resolver.get_complete_keylog_format(
                self.version, self.degree, encoded_coeffs
            )
            
            return final_keylog
            
        except Exception as e:
            print(f"Keylog generation error: {e}")
            # Fallback to simple format
            return f"P{self.degree}=" + "=".join(encoded_coeffs) + "=" * self.degree
    
    # ========== DEPRECATED - Now handled by prefix_resolver ==========
    def _get_polynomial_prefix(self) -> str:
        """DEPRECATED: Use prefix_resolver instead"""
        return self.prefix_resolver.get_polynomial_prefix(self.version, self.degree)
    
    def _get_polynomial_suffix(self) -> str:
        """DEPRECATED: Use prefix_resolver instead"""
        return self.prefix_resolver.get_polynomial_suffix(self.version, self.degree)
    
    # ========== GETTERS FOR UI ==========
    def get_last_roots(self) -> List[complex]:
        """Get last computed roots"""
        return self.last_roots.copy()
    
    def get_last_roots_display(self) -> str:
        """Get last roots display with repeated root analysis"""
        return self.last_roots_display
    
    def get_last_compact_display(self) -> str:
        """Get compact one-line display for UI constraints"""
        return self.last_compact_display
    
    def get_last_encoded_coefficients(self) -> List[str]:
        """Get last encoded coefficients for display"""
        return self.last_encoded_coefficients.copy()
    
    def get_last_final_keylog(self) -> str:
        """Get last generated keylog"""
        return self.last_final_keylog
    
    def get_real_roots_only(self) -> List[float]:
        """Get only real roots from last solution"""
        return self.solver.get_real_roots_only(self.last_roots)
    
    def get_root_multiplicities(self) -> Dict[str, int]:
        """Get multiplicity information for last computed roots"""
        if not self.last_roots:
            return {}
        return self.solver.get_root_multiplicities(self.last_roots)
    
    def get_polynomial_info(self) -> Dict[str, Any]:
        """Get detailed polynomial information including prefix info"""
        if not self.last_coefficients_numeric:
            base_info = {}
        else:
            base_info = self.solver.get_polynomial_info(self.last_coefficients_numeric, self.degree)
        
        # Add service info
        base_info.update({
            "version": self.version,
            "solver_method": self.solver.method,
            "solver_precision": self.solver.precision,
            "duplicate_threshold": self.solver.duplicate_threshold,
            "has_results": bool(self.last_roots)
        })
        
        # Add repeated roots analysis
        if self.last_roots:
            multiplicities = self.get_root_multiplicities()
            has_repeated = any(mult > 1 for mult in multiplicities.values())
            base_info.update({
                "has_repeated_roots": has_repeated,
                "root_multiplicities": multiplicities,
                "compact_display": self.last_compact_display
            })
        
        # Add prefix info
        try:
            prefix_info = self.prefix_resolver.get_version_info(self.version)
            base_info.update({
                "keylog_prefix": self.prefix_resolver.get_polynomial_prefix(self.version, self.degree),
                "keylog_suffix": self.prefix_resolver.get_polynomial_suffix(self.version, self.degree),
                "prefix_system": prefix_info.get('description', 'Unknown')
            })
        except Exception as e:
            print(f"Warning: Could not get prefix info: {e}")
        
        return base_info
    
    # ========== UTILITY METHODS ==========
    def reset_state(self):
        """Reset service state"""
        self.last_coefficients_raw = []
        self.last_coefficients_numeric = []
        self.last_roots = []
        self.last_encoded_coefficients = []
        self.last_final_keylog = ""
        self.last_roots_display = ""
        self.last_compact_display = ""
    
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
    
    def get_keylog_preview(self, coefficient_inputs: List[str]) -> str:
        """Get preview of what keylog would look like (without solving)"""
        try:
            encoded_coeffs = self._encode_coefficients(coefficient_inputs)
            return self.prefix_resolver.get_complete_keylog_format(
                self.version, self.degree, encoded_coeffs
            )
        except Exception as e:
            return f"Preview error: {str(e)}"
    
    def get_enhanced_roots_analysis(self) -> Dict[str, Any]:
        """Get detailed analysis of roots including repeated root detection"""
        if not self.last_roots:
            return {"has_results": False}
        
        multiplicities = self.get_root_multiplicities()
        real_roots = self.get_real_roots_only()
        
        analysis = {
            "has_results": True,
            "total_roots": len(self.last_roots),
            "real_roots_count": len(real_roots),
            "complex_roots_count": len(self.last_roots) - len(real_roots),
            "has_repeated_roots": any(mult > 1 for mult in multiplicities.values()),
            "root_multiplicities": multiplicities,
            "compact_display": self.last_compact_display,
            "full_display": self.last_roots_display
        }
        
        # Add discriminant info for degree 2
        if self.degree == 2 and self.last_coefficients_numeric:
            poly_info = self.solver.get_polynomial_info(self.last_coefficients_numeric, 2)
            if 'discriminant' in poly_info:
                analysis['discriminant'] = poly_info['discriminant']
                analysis['discriminant_analysis'] = poly_info.get('root_type', 'unknown')
        
        return analysis
    
    # ========== ERROR HANDLING ==========
    def get_last_error(self) -> Optional[str]:
        """Get last error message if any"""
        # TODO: Implement error tracking
        return None
    
    def is_service_ready(self) -> bool:
        """Check if service is ready for processing"""
        return (self.solver is not None and 
                self.prefix_resolver is not None and 
                self.degree in [2, 3, 4])


class PolynomialServiceError(Exception):
    """Custom exception for polynomial service errors"""
    pass

