"""Equation Encoding Service - Port từ TL với format chính xác"""
from typing import List, Dict, Any

try:
    from .mapping_manager import MappingManager
    from .prefix_resolver import EquationPrefixResolver
except ImportError:
    print("Warning: Cannot import MappingManager or PrefixResolver")
    MappingManager = None
    EquationPrefixResolver = None


class EquationEncodingService:
    """Service mã hóa equation theo chuẩn TL - Port từ TL views/equation/"""
    
    def __init__(self, mapping_file: str = None, prefixes_file: str = None):
        # Khởi tạo các component
        try:
            self.mapping_manager = MappingManager(mapping_file) if MappingManager and mapping_file else (MappingManager() if MappingManager else None)
            self.prefix_resolver = EquationPrefixResolver(prefixes_file) if EquationPrefixResolver and prefixes_file else (EquationPrefixResolver() if EquationPrefixResolver else None)
            
            if not self.mapping_manager or not self.prefix_resolver:
                raise Exception("Missing required components")
                
        except Exception as e:
            print(f"Warning: EquationEncodingService init failed: {e}")
            self.mapping_manager = None
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
        """Mã hóa dữ liệu phương trình - API giống TL"""
        try:
            if not self.mapping_manager or not self.prefix_resolver:
                return {
                    'success': False,
                    'error': 'Missing MappingManager or PrefixResolver',
                    'encoded_coefficients': [],
                    'total_result': ""
                }
            
            # Cập nhật tham số
            self.set_variables_count(so_an)
            self.set_version(phien_ban)
            
            # Mã hóa từng hệ số
            encoded_coefficients = []
            for he_so in danh_sach_he_so:
                if he_so.strip():
                    # Sử dụng MappingManager để encode giống TL
                    ket_qua = self.mapping_manager.encode_string(he_so)
                    encoded_coefficients.append(ket_qua)
                else:
                    encoded_coefficients.append("")
            
            # Tạo kết quả tổng theo format TL
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
        """Tạo chuỗi kết quả tổng theo format TL CHÍNH XÁC"""
        try:
            if not self.prefix_resolver:
                return "ERROR_NO_PREFIX_RESOLVER"
                
            # Lấy prefix từ TL
            prefix = self.prefix_resolver.get_equation_prefix(self.current_version, so_an)
            
            # Số hệ số cần thiết theo TL
            required_counts = {2: 6, 3: 12, 4: 20}

            if so_an in required_counts:
                required_count = required_counts[so_an]
                if len(encoded_coefficients) >= required_count:
                    he_so_can_thiet = encoded_coefficients[:required_count]
                    chuoi_he_so = "=".join(he_so_can_thiet)

                    # ĐIỀU CHỈNH ĐỊNH DẠNG THEO SỐ ẨN - GIỐNG TL
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
        required_count = so_an * (so_an + 1)  # n phương trình, mỗi cái có n+1 hệ số
        
        return {
            "valid": len(danh_sach_he_so) >= required_count,
            "required_count": required_count,
            "actual_count": len(danh_sach_he_so),
            "missing_count": max(0, required_count - len(danh_sach_he_so)),
            "message": f"Cần {required_count} hệ số cho hệ {so_an} ẩn, hiện có {len(danh_sach_he_so)}"
        }
    
    def test_encoding_parity(self, test_input: str) -> Dict[str, Any]:
        """Test mã hóa so với TL - để debug"""
        try:
            if not self.mapping_manager or not self.prefix_resolver:
                return {"error": "Components not available"}
                
            encoded = self.mapping_manager.encode_string(test_input)
            
            return {
                "input": test_input,
                "encoded": encoded,
                "mapping_rules_count": len(self.mapping_manager.mappings),
                "version": self.current_version,
                "prefix_for_2an": self.prefix_resolver.get_equation_prefix(self.current_version, 2)
            }
        except Exception as e:
            return {
                "input": test_input,
                "encoded": "",
                "error": str(e)
            }
    
    def get_final_keylog(self, encoded_coefficients: List[str], so_an: int = None) -> str:
        """Lấy keylog hoàn chỉnh theo format TL"""
        variables = so_an or self.current_variables
        return self._create_total_result_string(encoded_coefficients, variables)
    
    def is_available(self) -> bool:
        """Kiểm tra service có sẵn sàng không"""
        return self.mapping_manager is not None and self.prefix_resolver is not None