"""Equation Encoding Service - REFACTORED to use LatexToKeylogEncoder
Fixed import paths for both direct run and module import
"""
import sys
import os
from typing import List, Dict, Any

# ✅ FIX: Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# ✅ Import LatexToKeylogEncoder (absolute path)
try:
    from utils.latex_to_keylog import LatexToKeylogEncoder
except ImportError:
    print("Warning: Cannot import LatexToKeylogEncoder from utils")
    LatexToKeylogEncoder = None

# ✅ Import PrefixResolver (try both relative and absolute)
EquationPrefixResolver = None
try:
    # Try relative import first (when used as module)
    from .prefix_resolver import EquationPrefixResolver
except ImportError:
    try:
        # Try absolute import (when run as script)
        from services.equation.prefix_resolver import EquationPrefixResolver
    except ImportError:
        print("Warning: Cannot import PrefixResolver")
        EquationPrefixResolver = None


class EquationEncodingService:
    """Service mã hóa equation - REFACTORED với LatexToKeylogEncoder

    ✅ Thay đổi:
    - Sử dụng LatexToKeylogEncoder thay vì MappingManager
    - Hỗ trợ tích phân trong equation
    - Hỗ trợ cận phức tạp (có phân số)
    - Fallback paths tự động
    - ✅ Fixed import paths

    Interface giữ nguyên để backwards compatible
    """

    def __init__(self, mapping_file: str = None, prefixes_file: str = None):
        """Khởi tạo service với encoder mới

        Args:
            mapping_file: Path đến mapping.json (optional)
            prefixes_file: Path đến equation_prefixes.json (optional)
        """
        try:
            # ✅ Sử dụng LatexToKeylogEncoder thay vì MappingManager
            if LatexToKeylogEncoder:
                self.encoder = LatexToKeylogEncoder(
                    mapping_file or "config/equation_mode/mapping.json"
                )
            else:
                raise Exception("LatexToKeylogEncoder not available")

            # Prefix resolver giữ nguyên
            if EquationPrefixResolver:
                self.prefix_resolver = EquationPrefixResolver(
                    prefixes_file or "config/equation_mode/equation_prefixes.json"
                )
            else:
                raise Exception("EquationPrefixResolver not available")

        except Exception as e:
            print(f"Warning: EquationEncodingService init failed: {e}")
            self.encoder = None
            self.prefix_resolver = None

        # Trạng thái hiện tại
        self.current_version = "fx799"
        self.current_variables = 2

    def set_version(self, version: str):
        """Thiết lập phiên bản máy tính"""
        self.current_version = version

    def set_variables_count(self, count: int):
        """Thiết lập số ẩn"""
        if count in [2, 3, 4]:
            self.current_variables = count

    def encode_equation_data(self, danh_sach_he_so: List[str], so_an: int, phien_ban: str) -> Dict[str, Any]:
        """Mã hóa dữ liệu phương trình - Interface giữ nguyên

        Args:
            danh_sach_he_so: List các hệ số (LaTeX string)
            so_an: Số ẩn (2, 3, 4)
            phien_ban: Version máy tính (fx799, fx880, ...)

        Returns:
            Dict với keys: success, encoded_coefficients, total_result, prefix_used, version, variables
        """
        try:
            if not self.encoder or not self.prefix_resolver:
                return {
                    'success': False,
                    'error': 'Missing encoder or prefix resolver',
                    'encoded_coefficients': [],
                    'total_result': ""
                }

            # Cập nhật tham số
            self.set_variables_count(so_an)
            self.set_version(phien_ban)

            # ✅ Mã hóa từng hệ số bằng LatexToKeylogEncoder
            encoded_coefficients = []
            for he_so in danh_sach_he_so:
                if he_so.strip():
                    # ✅ THAY ĐỔI: Dùng encoder.encode() thay vì mapping_manager.encode_string()
                    ket_qua = self.encoder.encode(he_so)
                    encoded_coefficients.append(ket_qua)
                else:
                    encoded_coefficients.append("")

            # Tạo kết quả tổng (logic giữ nguyên)
            total_result = self._create_total_result_string(encoded_coefficients, so_an)

            return {
                'success': True,
                'encoded_coefficients': encoded_coefficients,
                'total_result': total_result,
                'prefix_used': self.prefix_resolver.get_equation_prefix(phien_ban, so_an),
                'version': phien_ban,
                'variables': so_an
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'encoded_coefficients': [],
                'total_result': ""
            }

    def _create_total_result_string(self, encoded_coefficients: List[str], so_an: int) -> str:
        """Tạo chuỗi kết quả tổng - Logic giữ nguyên"""
        try:
            if not self.prefix_resolver:
                return "ERROR_NO_PREFIX_RESOLVER"

            # Lấy prefix
            prefix = self.prefix_resolver.get_equation_prefix(self.current_version, so_an)

            # Số hệ số cần thiết
            required_counts = {2: 6, 3: 12, 4: 20}

            if so_an in required_counts:
                required_count = required_counts[so_an]
                if len(encoded_coefficients) >= required_count:
                    he_so_can_thiet = encoded_coefficients[:required_count]
                    chuoi_he_so = "=".join(he_so_can_thiet)

                    # Format theo số ẩn
                    if so_an == 2:
                        return f"{prefix}{chuoi_he_so}== ="
                    elif so_an == 3:
                        return f"{prefix}{chuoi_he_so}== = ="
                    elif so_an == 4:
                        return f"{prefix}{chuoi_he_so}== = = ="

            # Fallback - nối với dấu =
            chuoi_he_so = "=".join(encoded_coefficients)
            return f"{prefix}{chuoi_he_so}="

        except Exception as e:
            print(f"Lỗi khi tạo chuỗi kết quả tổng: {e}")
            return "ERROR_" + "=".join(encoded_coefficients) + "="

    def validate_input_format(self, danh_sach_he_so: List[str], so_an: int) -> Dict[str, Any]:
        """Validate input trước khi encode"""
        required_count = so_an * (so_an + 1)

        return {
            "valid": len(danh_sach_he_so) >= required_count,
            "required_count": required_count,
            "actual_count": len(danh_sach_he_so),
            "missing_count": max(0, required_count - len(danh_sach_he_so)),
            "message": f"Cần {required_count} hệ số cho hệ {so_an} ẩn, hiện có {len(danh_sach_he_so)}"
        }

    def test_encoding_parity(self, test_input: str) -> Dict[str, Any]:
        """Test mã hóa - để debug"""
        try:
            if not self.encoder or not self.prefix_resolver:
                return {"error": "Components not available"}

            # ✅ THAY ĐỔI: Dùng encoder mới
            encoded = self.encoder.encode(test_input)

            return {
                "input": test_input,
                "encoded": encoded,
                "mapping_rules_count": len(self.encoder.mappings),
                "version": self.current_version,
                "prefix_for_2an": self.prefix_resolver.get_equation_prefix(self.current_version, 2),
                "encoder_type": "LatexToKeylogEncoder"  # ✅ NEW
            }
        except Exception as e:
            return {
                "input": test_input,
                "encoded": "",
                "error": str(e)
            }

    def get_final_keylog(self, encoded_coefficients: List[str], so_an: int = None) -> str:
        """Lấy keylog hoàn chỉnh"""
        variables = so_an or self.current_variables
        return self._create_total_result_string(encoded_coefficients, variables)

    def is_available(self) -> bool:
        """Kiểm tra service có sẵn sàng không"""
        return self.encoder is not None and self.prefix_resolver is not None

    # ✅ NEW METHODS - Thêm features từ LatexToKeylogEncoder

    def encode_single_expression(self, expression: str) -> str:

        if not self.encoder:
            return expression
        return self.encoder.encode(expression)

    def encode_batch(self, expressions: List[str]) -> List[str]:
        """Encode nhiều biểu thức cùng lúc

        ✅ NEW: Batch encoding
        """
        if not self.encoder:
            return expressions
        return self.encoder.encode_batch(expressions)

    def validate_latex(self, expression: str) -> Dict[str, Any]:
        """Validate LaTeX expression

        ✅ NEW: Validation support
        """
        if not self.encoder:
            return {"valid": False, "error": "Encoder not available"}

        valid, error = self.encoder.validate_latex(expression)
        return {
            "valid": valid,
            "error": error,
            "expression": expression
        }


# ========== TESTING ==========
if __name__ == "__main__":
    print("=" * 80)
    print("EQUATION ENCODING SERVICE - REFACTORED TEST")
    print("=" * 80)
    print(f"Current directory: {os.getcwd()}")
    print(f"Script location: {__file__}")
    print()

    service = EquationEncodingService()

    if not service.is_available():
        print("❌ Service not available")
        print("\nDebug info:")
        print(f"  - LatexToKeylogEncoder: {'✓' if LatexToKeylogEncoder else '✗'}")
        print(f"  - EquationPrefixResolver: {'✓' if EquationPrefixResolver else '✗'}")
        print(f"  - encoder: {'✓' if service.encoder else '✗'}")
        print(f"  - prefix_resolver: {'✓' if service.prefix_resolver else '✗'}")
        exit(1)

    print("✅ Service initialized successfully")
    print(f"  - Encoder type: LatexToKeylogEncoder")
    print(f"  - Mapping rules loaded: {len(service.encoder.mappings)}")
    print()

    # Test 1: Encoding đơn giản
    print("--- Test 1: Basic Encoding ---")
    test_cases = [
        "1",
        "-5",
        "\\frac{1}{2}",
        "sqrt(4)",
        "sin(x)",
    ]

    for expr in test_cases:
        result = service.encode_single_expression(expr)
        print(f"{expr:20} → {result}")

    # Test 2: Encoding với tích phân
    print("\n--- Test 2: Integral Encoding (NEW) ---")
    integral_tests = [
        "\\int_{0}^{1} x dx",
        "\\int_{\\frac{1}{2}}^{1} x^2 dx",
        "\\frac{\\int_{0}^{1} x dx}{2}",
    ]

    for expr in integral_tests:
        result = service.encode_single_expression(expr)
        print(f"{expr:40} → {result}")

    # Test 3: Full equation data encoding
    print("\n--- Test 3: Full Equation Encoding ---")
    coefficients = ["\\int_{\\frac{1}{2}}^{1} x^2 dx", "2", "-\\frac{1}{2}", "0", "1", "sqrt(4)"]
    result = service.encode_equation_data(coefficients, 2, "fx799")

    print(f"Input coefficients: {coefficients}")
    print(f"Success: {result['success']}")
    print(f"Encoded: {result['encoded_coefficients']}")
    print(f"Total result: {result['total_result']}")
    print(f"Prefix used: {result['prefix_used']}")

    # Test 4: Validation
    print("\n--- Test 4: Validation (NEW) ---")
    validation_tests = [
        "\\frac{1}{2}",
        "\\frac{1{2}",  # Invalid
        "\\int_{0}^{1} x dx",
    ]

    for expr in validation_tests:
        result = service.validate_latex(expr)
        status = "✓" if result['valid'] else "✗"
        error_msg = f" - {result.get('error')}" if not result['valid'] else ""
        print(f"{status} {expr:30}{error_msg}")

    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
