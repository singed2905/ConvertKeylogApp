"""
Test script kiểm tra mã hóa tích phân cho PolynomialEncodingService
Sử dụng nhiều format tích phân phổ biến & kiểm tra bước chuyển đổi
"""
from services.polynomial.polynomial_encoding_service import PolynomialEncodingService

def print_header(title):
    print("\n" + "="*70)
    print(title.center(70))
    print("="*70)

def test_integral_encoding():
    encoder = PolynomialEncodingService()
    test_cases = [
        ("\\int_{0}^{1} x^2 dx", "LaTeX chuẩn: từ 0 đến 1"),
        ("\\int_{-1}^{2} sin(x) dx", "LaTeX: từ -1 đến 2 (hàm sin)"),
        ("int(x^2,0,1)", "Format đơn giản: int (0->1)"),
        ("int(sin(x),-1,2)", "Format đơn giản: int sin, -1->2"),
        ("\\int_{0}^{pi} cos(x) dx", "LaTeX: từ 0 đến pi (cos)")
    ]

    print_header("TEST MÃ HÓA TÍCH PHÂN - PolynomialEncodingService")
    for input_expr, desc in test_cases:
        result = encoder.test_encoding(input_expr)
        print(f"\nMô tả: {desc}")
        print(f"Input:    {input_expr}")
        print(f"Output:   {result['final']}")
        print(f"Số bước:  {result['total_transformations']}")
        # Hiển thị các bước quan trọng
        for step in result['steps']:
            if step['step'] > 0 and step['input'] != step['output']:
                print(f"  Step {step['step']}: {step['input']} → {step['output']}")
                print(f"    Rule: {step['rule']}")
                print(f"    Info: {step['description']}")
        print("-" * 50)

if __name__ == "__main__":
    test_integral_encoding()
