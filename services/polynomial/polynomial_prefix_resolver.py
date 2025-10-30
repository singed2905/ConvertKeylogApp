"""Polynomial Prefix Resolver - Generates keylog prefixes for polynomial equations
Adapted from equation prefix resolver but for polynomial degrees instead of variable count
"""
import json
import os
from typing import Dict, Any, List


class PolynomialPrefixResolver:
    """Resolver lấy prefix cho polynomial theo version và bậc phương trình"""
    
    def __init__(self, prefixes_file: str = "config/polynomial_mode/polynomial_prefixes.json"):
        self.prefixes_file = prefixes_file
        self.prefixes_data = self._load_polynomial_prefixes()
    
    def _load_polynomial_prefixes(self) -> Dict[str, Any]:
        """Load tiền tố polynomial từ JSON"""
        try:
            if not os.path.exists(self.prefixes_file):
                print(f"Warning: Polynomial prefixes file not found: {self.prefixes_file}")
                return self._get_default_polynomial_prefixes()

            with open(self.prefixes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate cấu trúc file
            if "versions" not in data or "global_defaults" not in data:
                print(f"File {self.prefixes_file} không có cấu trúc mong đợi, sử dụng mặc định")
                return self._get_default_polynomial_prefixes()

            return data

        except Exception as e:
            print(f"Lỗi khi đọc file polynomial_prefixes.json: {e}")
            return self._get_default_polynomial_prefixes()
    
    def _get_default_polynomial_prefixes(self) -> Dict[str, Any]:
        """Trả về cấu hình prefix mặc định cho polynomial"""
        return {
            "global_defaults": {
                "2": "P2=",
                "3": "P3=",
                "4": "P4="
            },
            "versions": {
                "fx799": {
                    "base_prefix": "P",
                    "polynomial": {
                        "2": "P2=",
                        "3": "P3=",
                        "4": "P4="
                    },
                    "suffix_patterns": {
                        "2": "==",
                        "3": "===",
                        "4": "===="
                    },
                    "description": "Casio fx-799VN standard polynomial prefixes"
                },
                "fx991": {
                    "base_prefix": "EQN",
                    "polynomial": {
                        "2": "EQN2=",
                        "3": "EQN3=",
                        "4": "EQN4="
                    },
                    "suffix_patterns": {
                        "2": "=0",
                        "3": "==0",
                        "4": "===0"
                    },
                    "description": "Casio fx-991 equation solver format"
                },
                "fx570": {
                    "base_prefix": "POL",
                    "polynomial": {
                        "2": "POL2=",
                        "3": "POL3=",
                        "4": "POL4="
                    },
                    "suffix_patterns": {
                        "2": "=ROOT",
                        "3": "==ROOT",
                        "4": "===ROOT"
                    },
                    "description": "Casio fx-570 polynomial mode"
                },
                "fx580": {
                    "base_prefix": "POLY",
                    "polynomial": {
                        "2": "POLY2=",
                        "3": "POLY3=",
                        "4": "POLY4="
                    },
                    "suffix_patterns": {
                        "2": "=SOLVE",
                        "3": "==SOLVE",
                        "4": "===SOLVE"
                    },
                    "description": "Casio fx-580 extended polynomial format"
                },
                "fx115": {
                    "base_prefix": "Q",
                    "polynomial": {
                        "2": "QUAD=",
                        "3": "CUB3=",
                        "4": "QUAT="
                    },
                    "suffix_patterns": {
                        "2": "=",
                        "3": "==",
                        "4": "==="
                    },
                    "description": "Casio fx-115 compact format"
                }
            },
            "metadata": {
                "version": "2.1",
                "description": "Default polynomial prefixes for various calculator versions",
                "last_updated": "2025-10-30"
            }
        }
    
    def get_polynomial_prefix(self, version: str, degree: int) -> str:
        """Lấy tiền tố cho phiên bản máy và bậc phương trình"""
        try:
            degree_str = str(degree)

            # Lấy cấu hình phiên bản
            versions_config = self.prefixes_data.get("versions", {})
            global_defaults = self.prefixes_data.get("global_defaults", {})

            # Ưu tiên 1: Prefix chi tiết theo phiên bản và bậc
            if version in versions_config:
                version_config = versions_config[version]

                # Kiểm tra có polynomial config chi tiết không
                if "polynomial" in version_config and degree_str in version_config["polynomial"]:
                    return version_config["polynomial"][degree_str]

                # Ưu tiên 2: Tự sinh từ base_prefix + bậc
                base_prefix = version_config.get("base_prefix")
                if base_prefix:
                    return f"{base_prefix}{degree}="

            # Ưu tiên 3: Fallback về global defaults
            if degree_str in global_defaults:
                return global_defaults[degree_str]

            # Mặc định cuối cùng
            return f"P{degree}="

        except Exception as e:
            print(f"Lỗi khi lấy polynomial prefix: {e}")
            return f"P{degree}="
    
    def get_polynomial_suffix(self, version: str, degree: int) -> str:
        """Lấy hậu tố cho phiên bản máy và bậc phương trình"""
        try:
            degree_str = str(degree)
            versions_config = self.prefixes_data.get("versions", {})
            
            if version in versions_config:
                version_config = versions_config[version]
                suffix_patterns = version_config.get("suffix_patterns", {})
                
                if degree_str in suffix_patterns:
                    return suffix_patterns[degree_str]
            
            # Default suffix pattern
            return "=" * degree
            
        except Exception as e:
            print(f"Lỗi khi lấy polynomial suffix: {e}")
            return "=" * degree
    
    def get_complete_keylog_format(self, version: str, degree: int, coefficients: List[str]) -> str:
        """Tạo keylog hoàn chỉnh với prefix + coefficients + suffix"""
        try:
            prefix = self.get_polynomial_prefix(version, degree)
            suffix = self.get_polynomial_suffix(version, degree)
            
            # Join coefficients với separator "="
            coeffs_part = "=".join(coefficients)
            
            return f"{prefix}{coeffs_part}{suffix}"
            
        except Exception as e:
            print(f"Lỗi khi tạo complete keylog format: {e}")
            return f"P{degree}=" + "=".join(coefficients) + "=" * degree
    
    def get_version_info(self, version: str) -> Dict[str, Any]:
        """Lấy thông tin chi tiết về phiên bản"""
        try:
            versions_config = self.prefixes_data.get("versions", {})

            if version in versions_config:
                version_config = versions_config[version]
                return {
                    "version": version,
                    "base_prefix": version_config.get("base_prefix", ""),
                    "polynomial_prefixes": version_config.get("polynomial", {}),
                    "suffix_patterns": version_config.get("suffix_patterns", {}),
                    "description": version_config.get("description", f"Phiên bản {version}")
                }
            else:
                return {
                    "version": version,
                    "base_prefix": "",
                    "polynomial_prefixes": {},
                    "suffix_patterns": {},
                    "description": f"Phiên bản {version} (chưa cấu hình)"
                }

        except Exception as e:
            print(f"Lỗi khi lấy thông tin phiên bản: {e}")
            return {
                "version": version,
                "base_prefix": "",
                "polynomial_prefixes": {},
                "suffix_patterns": {},
                "description": "Lỗi cấu hình"
            }
    
    def get_all_supported_versions(self) -> List[str]:
        """Lấy danh sách tất cả phiên bản được hỗ trợ"""
        try:
            versions_config = self.prefixes_data.get("versions", {})
            return list(versions_config.keys())
        except Exception as e:
            print(f"Lỗi khi lấy danh sách phiên bản: {e}")
            return ["fx799", "fx991", "fx570", "fx580", "fx115"]
    
    def debug_prefix_info(self, version: str) -> Dict[str, Any]:
        """Debug thông tin prefix cho tất cả bậc polynomial"""
        result = {
            "current_version": version,
            "prefixes": {},
            "suffixes": {},
            "version_config": self.get_version_info(version)
        }

        for degree in [2, 3, 4]:
            result["prefixes"][f"degree_{degree}"] = self.get_polynomial_prefix(version, degree)
            result["suffixes"][f"degree_{degree}"] = self.get_polynomial_suffix(version, degree)

        return result
    
    def validate_version_support(self, version: str) -> Dict[str, Any]:
        """Kiểm tra phiên bản có được hỗ trợ không"""
        supported_versions = self.get_all_supported_versions()

        return {
            "is_supported": version in supported_versions,
            "version": version,
            "supported_versions": supported_versions,
            "message": f"Phiên bản {version} {'được hỗ trợ' if version in supported_versions else 'chưa được hỗ trợ'}"
        }
    
    def reload_prefixes(self):
        """Reload lại cấu hình prefix (hữu ích khi cập nhật file config)"""
        try:
            self.prefixes_data = self._load_polynomial_prefixes()
            return True
        except Exception as e:
            print(f"Lỗi khi reload polynomial prefixes: {e}")
            return False


# ========== TESTING ==========
if __name__ == "__main__":
    resolver = PolynomialPrefixResolver()
    
    print("=== POLYNOMIAL PREFIX RESOLVER TEST ===")
    
    # Test các phiên bản với các bậc
    test_versions = ["fx799", "fx991", "fx570", "fx580", "fx115"]
    test_degrees = [2, 3, 4]
    
    for version in test_versions:
        print(f"\n--- Version: {version} ---")
        
        for degree in test_degrees:
            prefix = resolver.get_polynomial_prefix(version, degree)
            suffix = resolver.get_polynomial_suffix(version, degree)
            
            # Test với coefficients mẫu
            if degree == 2:
                coeffs = ["1", "-5", "6"]
            elif degree == 3:
                coeffs = ["1", "-6", "11", "-6"]
            else:  # degree == 4
                coeffs = ["1", "0", "-5", "0", "4"]
            
            complete_keylog = resolver.get_complete_keylog_format(version, degree, coeffs)
            
            print(f"  Degree {degree}: {prefix} ... {suffix}")
            print(f"  Complete: {complete_keylog}")
    
    # Test debug info
    print(f"\n--- Debug Info for fx799 ---")
    debug_info = resolver.debug_prefix_info("fx799")
    print(f"Prefixes: {debug_info['prefixes']}")
    print(f"Suffixes: {debug_info['suffixes']}")
    
    # Test validation
    print(f"\n--- Version Support Validation ---")
    for test_version in ["fx799", "fx999", "unknown"]:
        validation = resolver.validate_version_support(test_version)
        print(f"{test_version}: {validation['message']}")
    
    print("\n=== POLYNOMIAL PREFIX RESOLVER TEST COMPLETED ===")