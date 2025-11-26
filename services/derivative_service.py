"""Derivative Service - Validation logic cho Derivative Mode"""
import re


class DerivativeService:
    """Service for validating derivative LaTeX expressions"""

    _DERIVATIVE_LATEX_REGEX = re.compile(
        r"\\frac\{d.*?\}\{d[a-z]\}|\\frac\{d\^\d+.*?\}\{d[a-z]\^\d+\}|f'|f''|f'''|\\'", 
        re.IGNORECASE
    )

    @classmethod
    def validate_derivative_latex(cls, latex: str):
        """
        Validate if LaTeX string is a derivative expression.
        
        Supported formats:
        - Leibniz: \\frac{dy}{dx}, \\frac{d^2y}{dx^2}
        - Lagrange: f'(x), f''(x), f'''(x)
        - Prime: y', y'', y'''
        
        Args:
            latex: LaTeX string to validate
            
        Returns:
            tuple: (is_valid, message)
        """
        if not latex or not isinstance(latex, str):
            return False, "Chuỗi rỗng hoặc không phải string"

        latex = latex.strip()

        if len(latex) < 2:
            return False, "Chuỗi quá ngắn để là đạo hàm"

        # Remove $ delimiters if present
        if latex.startswith("$") and latex.endswith("$"):
            latex = latex[1:-1]

        # Check for derivative keywords
        derivative_keywords = [
            r'\frac{d',      # Leibniz notation
            "f'",            # Lagrange notation (function)
            "y'",            # Lagrange notation (variable)
            r"\'",           # Prime notation
        ]
        
        has_derivative = any(kw in latex for kw in derivative_keywords)
        
        if not has_derivative:
            return False, "Không tìm thấy ký hiệu đạo hàm (\\frac{d}{dx}, f', y') trong chuỗi"

        # Validate format with regex
        if cls._DERIVATIVE_LATEX_REGEX.search(latex):
            return True, "Hợp lệ: nhận diện dạng đạo hàm trong LaTeX"

        return False, "Không nhận diện được đúng cấu trúc đạo hàm LaTeX – cần dạng \\frac{dy}{dx} hoặc f'(x) hoặc y'"


if __name__ == "__main__":
    # Test cases
    service = DerivativeService()
    
    test_cases = [
        (r"\frac{dy}{dx}", True),
        (r"\frac{d^2y}{dx^2}", True),
        (r"f'(x)", True),
        (r"f''(x)", True),
        (r"y'", True),
        (r"y''", True),
        (r"x + 2", False),
        (r"\int x dx", False),
        ("", False),
    ]
    
    print("Testing DerivativeService validation:\n")
    for latex, expected_valid in test_cases:
        is_valid, msg = service.validate_derivative_latex(latex)
        status = "✅" if is_valid == expected_valid else "❌"
        print(f"{status} '{latex}' → {is_valid} ({msg})")
