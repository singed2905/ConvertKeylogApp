
from services.polynomial.polynomial_service import PolynomialService
from services.polynomial.polynomial_encoding_service import PolynomialEncodingService


def print_separator(title=""):
    print("\n" + "="*70)
    if title:
        print(f"  {title}")
        print("="*70)


def test_basic_encoding():
    """Test basic encoding với PolynomialEncodingService"""
    print_separator("TEST 1: BASIC COEFFICIENT ENCODING")
    
    encoder = PolynomialEncodingService()
    
    test_cases = [
        ("-5", "Dấu âm"),
        ("sqrt(4)", "Căn bậc hai"),
        ("sin(pi/2)", "Hàm sin"),
        ("cos(0)", "Hàm cos"),
        ("ln(e)", "Logarit tự nhiên"),
        ("2*3", "Phép nhân"),
        ("10/5", "Phép chia"),
        ("-sqrt(25)", "Kết hợp âm và sqrt")
    ]
    
    print("\nCác test case cơ bản:")
    print("-" * 70)
    for input_val, description in test_cases:
        encoded = encoder.encode_coefficient(input_val)
        print(f"{description:30} | '{input_val:15}' → '{encoded}'")


def test_detailed_encoding():
    """Test chi tiết với step-by-step transformation"""
    print_separator("TEST 2: DETAILED STEP-BY-STEP ENCODING")
    
    encoder = PolynomialEncodingService()
    
    test_input = "-sqrt(25)"
    print(f"\nInput: '{test_input}'")
    print("-" * 70)
    
    result = encoder.test_encoding(test_input)
    
    print(f"Original: {result['original']}")
    print(f"Final:    {result['final']}")
    print(f"\nTotal transformations: {result['total_transformations']}")
    print("\nTransformation steps:")
    
    for step in result['steps']:
        if step['step'] > 0:
            print(f"\n  Step {step['step']}:")
            print(f"    Input:  {step['input']}")
            print(f"    Output: {step['output']}")
            print(f"    Rule:   {step['rule']}")
            print(f"    Info:   {step['description']}")


def test_polynomial_service_integration():
    """Test tích hợp với PolynomialService hoàn chỉnh"""
    print_separator("TEST 3: FULL POLYNOMIAL SERVICE INTEGRATION")
    
    service = PolynomialService()
    
    # Test case: x² - 5x + 6 = 0
    print("\nTest case: x² - 5x + 6 = 0")
    print("-" * 70)
    
    coefficients = ["1", "-5", "6"]
    
    service.set_degree(2)
    service.set_version("fx799")
    
    print(f"Input coefficients: {coefficients}")
    
    # Process workflow
    success, msg, roots_display, keylog = service.process_complete_workflow(coefficients)
    
    if success:
        print(f"\n✅ Processing successful!")
        print(f"\nRoots:")
        print(roots_display)
        
        print(f"\nEncoded coefficients: {service.get_last_encoded_coefficients()}")
        print(f"\nFinal Keylog: {keylog}")
    else:
        print(f"\n❌ Error: {msg}")


def test_with_expressions():
    """Test với biểu thức toán học phức tạp"""
    print_separator("TEST 4: COMPLEX MATHEMATICAL EXPRESSIONS")
    
    service = PolynomialService()
    
    # Test case: x² - sqrt(4)x + sin(pi/2) = 0
    print("\nTest case: x² - sqrt(4)x + sin(pi/2) = 0")
    print("-" * 70)
    
    coefficients = ["1", "-sqrt(4)", "sin(pi/2)"]
    
    service.set_degree(2)
    service.set_version("fx799")
    
    print(f"Input coefficients (biểu thức): {coefficients}")
    
    # Test encoding rieng biệt
    print("\nEncoding của từng hệ số:")
    for i, coeff in enumerate(coefficients):
        test_result = service.test_coefficient_encoding(coeff)
        print(f"  Coeff {i}: '{coeff}' → '{test_result['final']}'")
    
    # Process full workflow
    success, msg, roots_display, keylog = service.process_complete_workflow(coefficients)
    
    if success:
        print(f"\n✅ Processing successful!")
        print(f"\nRoots:")
        print(roots_display)
        print(f"\nFinal Keylog: {keylog}")
    else:
        print(f"\n❌ Error: {msg}")


def test_multiple_versions():
    """Test với nhiều phiên bản máy tính"""
    print_separator("TEST 5: MULTIPLE CALCULATOR VERSIONS")
    
    service = PolynomialService()
    
    coefficients = ["1", "-5", "6"]
    versions = ["fx799", "fx880"]
    
    print(f"\nInput: x² - 5x + 6 = 0")
    print(f"Coefficients: {coefficients}")
    print("-" * 70)
    
    service.set_degree(2)
    
    for version in versions:
        service.set_version(version)
        success, msg, _, keylog = service.process_complete_workflow(coefficients)
        
        if success:
            encoded = service.get_last_encoded_coefficients()
            print(f"\n{version:10} | Encoded: {encoded} | Keylog: {keylog}")
        else:
            print(f"\n{version:10} | Error: {msg}")


def test_encoding_info():
    """Hiển thị thông tin về encoding rules"""
    print_separator("TEST 6: ENCODING RULES INFORMATION")
    
    encoder = PolynomialEncodingService()
    info = encoder.get_mapping_info()
    
    print(f"\nSource file: {info['source_file']}")
    print(f"Total mapping rules: {info['total_mappings']}")
    print(f"Metadata: {info['metadata']}")
    
    print("\nMapping Rules:")
    print("-" * 70)
    
    for idx, mapping in enumerate(info['mappings'][:10], 1):  # Hiển thị 10 rules đầu
        print(f"\n{idx}. {mapping['description']}")
        print(f"   Find:    '{mapping['find']}'")
        print(f"   Replace: '{mapping['replace']}'")
        print(f"   Type:    {mapping['type']}")


def main():
    """Chạy tất cả các test"""
    print("\n" + "#"*70)
    print("#" + " "*68 + "#")
    print("#" + "  POLYNOMIAL ENCODING SERVICE - TEST SUITE".center(68) + "#")
    print("#" + "  Sử dụng polynomial_mapping.json".center(68) + "#")
    print("#" + " "*68 + "#")
    print("#"*70)
    
    try:
        # Run all tests
        test_basic_encoding()
        test_detailed_encoding()
        test_polynomial_service_integration()
        test_with_expressions()
        test_multiple_versions()
        test_encoding_info()
        
        print_separator("ALL TESTS COMPLETED SUCCESSFULLY")
        print("\n✅ Tất cả các test đã chạy thành công!")
        print("\nPolynomial Encoding Service sẵn sàng sử dụng với polynomial_mapping.json")
        
    except Exception as e:
        print_separator("ERROR")
        print(f"\n❌ Lỗi khi chạy test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
