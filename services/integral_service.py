# integral_service.py - Logic kiểm tra chuỗi LaTeX cho Integral Mode
import re

class IntegralService:
    """
    Cung cấp hàm validate_integral_latex(latex: str) -> bool, dict:
    - Kiểm tra 1 chuỗi có phải là biểu thức tích phân LaTeX không (dạng \\int, lower/upper bound, ...)
    - Không kiểm tra math syntax sâu, chỉ kiểm tra pattern tổng quát và loại bỏ nhập linh tinh.
    """
    # Regex phủ nhiều dạng phổ biến cho tích phân
    _INTEGRAL_LATEX_REGEX = re.compile(
        r"\\int\s*(_\{[^\}]+\})?\s*(\^\{[^\}]+\})?\s*[^\\]+(\\,|[dxdtdu])?", re.IGNORECASE
    )

    @classmethod
    def validate_integral_latex(cls, latex: str):
        """
        Kiểm tra chuỗi latex có phải kiểu tích phân không;
        Trả về:
            - is_valid: bool
            - message: lý do hoặc mô tả
        """
        if not latex or not isinstance(latex, str):
            return False, "Chuỗi rỗng hoặc không phải string"
        latex = latex.strip()
        if len(latex) < 5:
            return False, "Chuỗi quá ngắn để là tích phân"
        # Remove common delimiters
        if latex.startswith("$") and latex.endswith("$"):
            latex = latex[1:-1]
        # Check for \int
        if "\\int" not in latex:
            return False, "Không tìm thấy từ khóa tích phân (\\int) trong chuỗi"
        # Regex match for \int_{...}^{...} ... dx
        if cls._INTEGRAL_LATEX_REGEX.match(latex):
            return True, "Hợp lệ: nhận diện dạng tích phân trong LaTeX"
        return False, "Không nhận diện được đúng cấu trúc tích phân LaTeX – cần dạng \\int, cận (tuỳ), hàm, vi phân (dx,dt,...)"
