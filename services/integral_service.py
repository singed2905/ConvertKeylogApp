"""Integral Service - Validation logic cho Integral Mode"""
import re


class IntegralService:

    _INTEGRAL_LATEX_REGEX = re.compile(
        r"\\int\s*(_\{[^\}]+\})?\s*(\^\{[^\}]+\})?\s*[^\\]+(\\,|[dxdtdu])?", re.IGNORECASE
    )

    @classmethod
    def validate_integral_latex(cls, latex: str):
        if not latex or not isinstance(latex, str):
            return False, "Chuỗi rỗng hoặc không phải string"

        latex = latex.strip()

        if len(latex) < 5:
            return False, "Chuỗi quá ngắn để là tích phân"

        if latex.startswith("$") and latex.endswith("$"):
            latex = latex[1:-1]

        if "\\int" not in latex:
            return False, "Không tìm thấy từ khóa tích phân (\\int) trong chuỗi"

        if cls._INTEGRAL_LATEX_REGEX.match(latex):
            return True, "Hợp lệ: nhận diện dạng tích phân trong LaTeX"

        return False, "Không nhận diện được đúng cấu trúc tích phân LaTeX – cần dạng \\int, cận (tuỳ), hàm, vi phân (dx,dt,...)"
