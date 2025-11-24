

import re
import math
from typing import Dict, Any, List, Tuple, Optional, Union
import warnings

# Optional dependencies
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    warnings.warn("NumPy not available - numerical integration disabled")

try:
    from scipy import integrate as scipy_integrate
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    warnings.warn("SciPy not available - advanced integration disabled")

try:
    import sympy as sp
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False
    warnings.warn("SymPy not available - symbolic integration disabled")


class LatexCalculator:
    """Core calculator to parse and evaluate LaTeX expressions"""
    
    def __init__(self):
        self.constants = {
            'pi': math.pi,
            'e': math.e,
        }
        
        self.functions = {
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log10,
            'ln': math.log,
            'exp': math.exp,
            'abs': abs,
        }
        
        if HAS_NUMPY:
            self.functions.update({
                'sqrt': np.sqrt,
                'sin': np.sin,
                'cos': np.cos,
                'tan': np.tan,
                'log': np.log10,
                'ln': np.log,
                'exp': np.exp,
            })
    
    def latex_to_python(self, latex_expr: str) -> str:
        """Convert LaTeX expression to Python expression
        
        Examples:
            \\frac{1}{x^2} → (1)/(x**2)
            \\sqrt{x} → sqrt(x)
            x^2 → x**2
        """
        result = latex_expr.strip()
        
        # Remove LaTeX formatting
        result = result.replace(r'\left', '').replace(r'\right', '')
        result = result.replace(' ', '')
        
        # Remove integral notation (will be handled separately)
        result = re.sub(r'\\int\s*(_\{[^}]*\}\s*)?\s*(\^\{[^}]*\}\s*)?', '', result)
        
        # Remove differential (dx, dy, dz, dt, du, dv)
        result = re.sub(r'd[a-z]$', '', result)
        result = re.sub(r'd[a-z]\s', '', result)
        
        # Convert fractions: \frac{a}{b} → (a)/(b)
        for _ in range(10):
            pattern = r'\\frac\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
            match = re.search(pattern, result)
            if not match:
                break
            num = match.group(1)
            den = match.group(2)
            replacement = f"({num})/({den})"
            result = result[:match.start()] + replacement + result[match.end():]
        
        # Convert functions
        result = result.replace(r'\sqrt{', 'sqrt(')
        result = result.replace(r'\sin', 'sin')
        result = result.replace(r'\cos', 'cos')
        result = result.replace(r'\tan', 'tan')
        result = result.replace(r'\ln', 'ln')
        result = result.replace(r'\log', 'log')
        result = result.replace(r'\exp', 'exp')
        
        # Convert exponents: x^2 → x**2
        result = re.sub(r'\^(\d+)', r'**\1', result)
        result = re.sub(r'\^\{([^}]+)\}', r'**(\1)', result)
        
        # Convert braces to parentheses
        result = result.replace('{', '(')
        result = result.replace('}', ')')
        
        return result
    
    def evaluate(self, python_expr: str, variables: Dict[str, float]) -> float:
        """Evaluate Python expression with given variables
        
        Args:
            python_expr: Python expression string
            variables: Dict of variable names to values
            
        Returns:
            Evaluated result as float
        """
        # Build safe evaluation context
        eval_context = {
            **self.constants,
            **self.functions,
            **variables
        }
        
        try:
            result = eval(python_expr, {"__builtins__": {}}, eval_context)
            return float(result)
        except Exception as e:
            raise ValueError(f"Evaluation failed: {e}")
    
    def evaluate_latex(self, latex_expr: str, variables: Dict[str, float]) -> float:
        """Evaluate LaTeX expression directly
        
        Args:
            latex_expr: LaTeX expression
            variables: Dict of variable values
            
        Returns:
            Evaluated result
        """
        python_expr = self.latex_to_python(latex_expr)
        return self.evaluate(python_expr, variables)


class IntegralCalculator:
    """Calculator for definite and indefinite integrals"""
    
    def __init__(self):
        self.latex_calc = LatexCalculator()
    
    def _parse_integral_bounds(self, latex_expr: str) -> Tuple[Optional[str], Optional[str], str, str]:
        """Parse integral expression to extract bounds, function, and variable
        
        Returns:
            (lower_bound, upper_bound, function, variable)
        """
        # Pattern: \int_{a}^{b} f(x) dx
        pattern = r'\\int\s*_\{([^}]*)\}\s*\^\{([^}]*)\}\s*(.*?)\s*d([a-z])'
        match = re.search(pattern, latex_expr)
        
        if match:
            lower = match.group(1).strip()
            upper = match.group(2).strip()
            function = match.group(3).strip()
            variable = match.group(4)
            return lower, upper, function, variable
        
        # Pattern without bounds: \int f(x) dx
        pattern2 = r'\\int\s*(.*?)\s*d([a-z])'
        match2 = re.search(pattern2, latex_expr)
        
        if match2:
            function = match2.group(1).strip()
            variable = match2.group(2)
            return None, None, function, variable
        
        raise ValueError("Cannot parse integral expression")
    
    def calculate_definite_numerical(
        self, 
        latex_expr: str,
        method: str = 'quad'
    ) -> Dict[str, Any]:
        """Calculate definite integral numerically using scipy
        
        Args:
            latex_expr: LaTeX integral expression with bounds
            method: 'quad' (adaptive), 'trapz' (trapezoidal), 'simps' (Simpson's)
            
        Returns:
            Dict with result, error, and metadata
        """
        if not HAS_SCIPY and method == 'quad':
            raise ImportError("SciPy required for numerical integration")
        
        # Parse expression
        lower_str, upper_str, func_latex, var = self._parse_integral_bounds(latex_expr)
        
        if lower_str is None or upper_str is None:
            raise ValueError("Definite integral requires bounds")
        
        # Convert bounds to numbers
        try:
            lower = self.latex_calc.evaluate_latex(lower_str, {})
            upper = self.latex_calc.evaluate_latex(upper_str, {})
        except:
            lower = float(lower_str)
            upper = float(upper_str)
        
        # Convert function to Python
        func_python = self.latex_calc.latex_to_python(func_latex)
        
        # Create integrand function
        def integrand(x):
            return self.latex_calc.evaluate(func_python, {var: x})
        
        # Perform integration
        if method == 'quad':
            result, error = scipy_integrate.quad(integrand, lower, upper)
            return {
                'success': True,
                'result': result,
                'error': error,
                'method': 'scipy.quad',
                'bounds': (lower, upper),
                'variable': var,
                'function': func_latex
            }
        
        elif method == 'trapz' and HAS_NUMPY:
            x_vals = np.linspace(lower, upper, 1000)
            y_vals = np.array([integrand(x) for x in x_vals])
            result = np.trapz(y_vals, x_vals)
            return {
                'success': True,
                'result': result,
                'error': None,
                'method': 'numpy.trapz',
                'bounds': (lower, upper),
                'variable': var,
                'function': func_latex
            }
        
        elif method == 'simps' and HAS_SCIPY:
            x_vals = np.linspace(lower, upper, 1001)  # Simpson needs odd number
            y_vals = np.array([integrand(x) for x in x_vals])
            result = scipy_integrate.simpson(y_vals, x_vals)
            return {
                'success': True,
                'result': result,
                'error': None,
                'method': 'scipy.simpson',
                'bounds': (lower, upper),
                'variable': var,
                'function': func_latex
            }
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def calculate_indefinite_symbolic(self, latex_expr: str) -> Dict[str, Any]:
        """Calculate indefinite integral symbolically using SymPy
        
        Args:
            latex_expr: LaTeX integral expression without bounds
            
        Returns:
            Dict with symbolic result and LaTeX output
        """
        if not HAS_SYMPY:
            raise ImportError("SymPy required for symbolic integration")
        
        # Parse expression
        _, _, func_latex, var = self._parse_integral_bounds(latex_expr)
        
        # Convert to SymPy
        x = sp.Symbol(var)
        
        # Convert LaTeX to SymPy expression
        try:
            # Try using sympify with LaTeX parsing
            func_python = self.latex_calc.latex_to_python(func_latex)
            expr = sp.sympify(func_python, locals={var: x})
        except:
            raise ValueError("Cannot convert to SymPy expression")
        
        # Integrate
        result = sp.integrate(expr, x)
        
        return {
            'success': True,
            'result': result,
            'result_latex': sp.latex(result),
            'result_str': str(result),
            'variable': var,
            'function': func_latex,
            'method': 'sympy.integrate'
        }
    
    def calculate_definite_symbolic(self, latex_expr: str) -> Dict[str, Any]:
        """Calculate definite integral symbolically using SymPy
        
        Args:
            latex_expr: LaTeX integral expression with bounds
            
        Returns:
            Dict with symbolic result
        """
        if not HAS_SYMPY:
            raise ImportError("SymPy required for symbolic integration")
        
        # Parse expression
        lower_str, upper_str, func_latex, var = self._parse_integral_bounds(latex_expr)
        
        if lower_str is None or upper_str is None:
            raise ValueError("Definite integral requires bounds")
        
        # Convert to SymPy
        x = sp.Symbol(var)
        
        # Convert function
        func_python = self.latex_calc.latex_to_python(func_latex)
        expr = sp.sympify(func_python, locals={var: x})
        
        # Convert bounds
        lower = sp.sympify(lower_str)
        upper = sp.sympify(upper_str)
        
        # Integrate
        result = sp.integrate(expr, (x, lower, upper))
        
        # Try to evaluate numerically
        try:
            numerical_result = float(result.evalf())
        except:
            numerical_result = None
        
        return {
            'success': True,
            'result': result,
            'result_latex': sp.latex(result),
            'result_str': str(result),
            'numerical_value': numerical_result,
            'bounds': (lower_str, upper_str),
            'variable': var,
            'function': func_latex,
            'method': 'sympy.integrate'
        }
    
    def calculate_double_integral(
        self,
        latex_expr: str,
        method: str = 'numerical'
    ) -> Dict[str, Any]:
        """Calculate double integral (nested integral)
        
        Args:
            latex_expr: LaTeX expression with double integral
            method: 'numerical' or 'symbolic'
            
        Returns:
            Dict with result
        """
        # Pattern: \int_{a}^{b} \int_{c}^{d} f(x,y) dy dx
        pattern = r'\\int\s*_\{([^}]*)\}\s*\^\{([^}]*)\}\s*\\int\s*_\{([^}]*)\}\s*\^\{([^}]*)\}\s*(.*?)\s*d([a-z])\s*d([a-z])'
        match = re.search(pattern, latex_expr)
        
        if not match:
            raise ValueError("Cannot parse double integral")
        
        outer_lower = match.group(1).strip()
        outer_upper = match.group(2).strip()
        inner_lower = match.group(3).strip()
        inner_upper = match.group(4).strip()
        function = match.group(5).strip()
        inner_var = match.group(6)
        outer_var = match.group(7)
        
        if method == 'numerical' and HAS_SCIPY:
            # Convert function to Python
            func_python = self.latex_calc.latex_to_python(function)
            
            # Evaluate bounds
            def get_bound_value(bound_str, outer_val=None):
                try:
                    if outer_val is not None:
                        return self.latex_calc.evaluate(bound_str, {outer_var: outer_val})
                    else:
                        return float(bound_str)
                except:
                    return float(bound_str)
            
            outer_lower_val = get_bound_value(outer_lower)
            outer_upper_val = get_bound_value(outer_upper)
            
            # Create integrand
            def integrand(inner_val, outer_val):
                return self.latex_calc.evaluate(
                    func_python, 
                    {inner_var: inner_val, outer_var: outer_val}
                )
            
            # Perform double integration
            result, error = scipy_integrate.dblquad(
                integrand,
                outer_lower_val,
                outer_upper_val,
                lambda x: get_bound_value(inner_lower, x),
                lambda x: get_bound_value(inner_upper, x)
            )
            
            return {
                'success': True,
                'result': result,
                'error': error,
                'method': 'scipy.dblquad',
                'outer_bounds': (outer_lower, outer_upper),
                'inner_bounds': (inner_lower, inner_upper),
                'variables': (outer_var, inner_var),
                'function': function
            }
        
        elif method == 'symbolic' and HAS_SYMPY:
            # Use SymPy
            x = sp.Symbol(outer_var)
            y = sp.Symbol(inner_var)
            
            func_python = self.latex_calc.latex_to_python(function)
            expr = sp.sympify(func_python, locals={outer_var: x, inner_var: y})
            
            inner_lower_sym = sp.sympify(inner_lower, locals={outer_var: x})
            inner_upper_sym = sp.sympify(inner_upper, locals={outer_var: x})
            outer_lower_sym = sp.sympify(outer_lower)
            outer_upper_sym = sp.sympify(outer_upper)
            
            # Integrate inner then outer
            inner_result = sp.integrate(expr, (y, inner_lower_sym, inner_upper_sym))
            result = sp.integrate(inner_result, (x, outer_lower_sym, outer_upper_sym))
            
            try:
                numerical_value = float(result.evalf())
            except:
                numerical_value = None
            
            return {
                'success': True,
                'result': result,
                'result_latex': sp.latex(result),
                'result_str': str(result),
                'numerical_value': numerical_value,
                'method': 'sympy.integrate',
                'variables': (outer_var, inner_var),
                'function': function
            }
        
        else:
            raise ImportError("Required library not available")


# Main service wrapper
class IntegralCalculatorService:
    """High-level service combining all calculation methods"""
    
    def __init__(self):
        self.latex_calc = LatexCalculator()
        self.integral_calc = IntegralCalculator()
    
    def calculate(
        self,
        latex_expr: str,
        method: str = 'auto',
        **kwargs
    ) -> Dict[str, Any]:
        """Calculate integral with automatic method selection
        
        Args:
            latex_expr: LaTeX expression
            method: 'auto', 'numerical', 'symbolic'
            **kwargs: Additional arguments
            
        Returns:
            Result dictionary
        """
        try:
            # Detect integral type
            integral_count = latex_expr.count(r'\int')
            has_bounds = '_{' in latex_expr and '^{' in latex_expr
            
            if integral_count == 0:
                # Just evaluate expression
                variables = kwargs.get('variables', {})
                result = self.latex_calc.evaluate_latex(latex_expr, variables)
                return {
                    'success': True,
                    'result': result,
                    'type': 'expression',
                    'method': 'direct_evaluation'
                }
            
            elif integral_count == 1:
                if has_bounds:
                    # Definite integral
                    if method == 'symbolic' and HAS_SYMPY:
                        return self.integral_calc.calculate_definite_symbolic(latex_expr)
                    else:
                        return self.integral_calc.calculate_definite_numerical(latex_expr)
                else:
                    # Indefinite integral
                    if HAS_SYMPY:
                        return self.integral_calc.calculate_indefinite_symbolic(latex_expr)
                    else:
                        return {
                            'success': False,
                            'error': 'Indefinite integral requires SymPy'
                        }
            
            elif integral_count >= 2:
                # Multiple integral
                if method == 'symbolic' and HAS_SYMPY:
                    return self.integral_calc.calculate_double_integral(latex_expr, 'symbolic')
                elif HAS_SCIPY:
                    return self.integral_calc.calculate_double_integral(latex_expr, 'numerical')
                else:
                    return {
                        'success': False,
                        'error': 'Multiple integrals require SciPy or SymPy'
                    }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'latex_input': latex_expr
            }
    
    def get_available_methods(self) -> List[str]:
        """Get list of available calculation methods"""
        methods = ['direct_evaluation']
        
        if HAS_SCIPY:
            methods.extend(['numerical_definite', 'numerical_double'])
        
        if HAS_SYMPY:
            methods.extend(['symbolic_definite', 'symbolic_indefinite', 'symbolic_double'])
        
        return methods
    
    def is_fully_available(self) -> bool:
        """Check if all dependencies are available"""
        return HAS_NUMPY and HAS_SCIPY and HAS_SYMPY


# CLI Test
if __name__ == "__main__":
    print("=" * 80)
    print("INTEGRAL CALCULATOR SERVICE - TEST")
    print("=" * 80)
    print()
    
    service = IntegralCalculatorService()
    
    print(f"Available methods: {service.get_available_methods()}")
    print(f"Fully available: {service.is_fully_available()}")
    print()
    
    test_cases = [
        (r"x^2", "Expression evaluation", {'variables': {'x': 3}}),
        (r"\int_{0}^{1} x dx", "Definite integral (linear)", {}),
        (r"\int_{0}^{1} x^2 dx", "Definite integral (quadratic)", {}),
        (r"\int x^2 dx", "Indefinite integral", {}),
        (r"\int_{0}^{1} \int_{0}^{x} xy dy dx", "Double integral", {}),
    ]
    
    for latex, desc, opts in test_cases:
        print(f"--- {desc} ---")
        print(f"LaTeX: {latex}")
        
        result = service.calculate(latex, **opts)
        
        if result['success']:
            print(f"✅ Result: {result.get('result')}")
            print(f"   Method: {result.get('method')}")
            if 'numerical_value' in result:
                print(f"   Numerical: {result['numerical_value']}")
        else:
            print(f"❌ Error: {result['error']}")
        
        print()
    
    print("=" * 80)
