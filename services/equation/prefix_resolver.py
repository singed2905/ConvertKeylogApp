"""Equation Prefix Resolver - Port từ TL controllers/equation_controller.py"""
import json
import os
from typing import Dict, Any, List


class EquationPrefixResolver:
    """Resolver lấy prefix cho equation theo version và số ẩn - Port từ TL"""
    
    def __init__(self, prefixes_file: str = "config/equation_mode/equation_prefixes.json"):
        self.prefixes_file = prefixes_file
        self.prefixes_data = self._load_equation_prefixes()
    
    def _load_equation_prefixes(self) -> Dict[str, Any]:
        """Load tiền tố phương trình từ JSON với cấu trúc TL"""
        try:
            if not os.path.exists(self.prefixes_file):
                print(f"Warning: Prefixes file not found: {self.prefixes_file}")
                return self._get_default_equation_prefixes()

            with open(self.prefixes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate cấu trúc file
            if "versions" not in data or "global_defaults" not in data:
                print(f"File {self.prefixes_file} không có cấu trúc mong đợi, sử dụng mặc định")
                return self._get_default_equation_prefixes()

            return data

        except Exception as e:
            print(f"Lỗi khi đọc file equation_prefixes.json: {e}")
            return self._get_default_equation_prefixes()
    
    def _get_default_equation_prefixes(self) -> Dict[str, Any]:
        """Trả về cấu hình mặc định từ TL"""
        return {
            "global_defaults": {
                "2": "w912",
                "3": "w913",
                "4": "w914"
            },
            "versions": {
                "fx799": {
                    "base_prefix": "w",
                    "equation": {
                        "2": "w912",
                        "3": "w913",
                        "4": "w914"
                    }
                },
                "fx880": {
                    "base_prefix": "wR$$||",
                    "equation": {
                        "2": "wR$$|||",
                        "3": "wR$$||R|",
                        "4": "wR$$||RR|"
                    }
                },
                "fx801": {
                    "base_prefix": "yl",
                    "equation": {
                        "2": "yl912",
                        "3": "yl913",
                        "4": "yl914"
                    }
                },
                "fx802": {
                    "base_prefix": "zm",
                    "equation": {
                        "2": "zm912",
                        "3": "zm913",
                        "4": "zm914"
                    }
                },
                "fx803": {
                    "base_prefix": "an",
                    "equation": {
                        "2": "an912",
                        "3": "an913",
                        "4": "an914"
                    }
                }
            },
            "metadata": {
                "version": "2.0",
                "description": "Fallback prefixes từ TL"
            }
        }
    
    def get_equation_prefix(self, version: str, so_an: int) -> str:
        """Lấy tiền tố cho phiên bản máy và số ẩn - Logic y hệt TL"""
        try:
            so_an_str = str(so_an)

            # Lấy cấu hình phiên bản
            versions_config = self.prefixes_data.get("versions", {})
            global_defaults = self.prefixes_data.get("global_defaults", {})

            # Ưu tiên 1: Prefix chi tiết theo phiên bản và số ẩn
            if version in versions_config:
                version_config = versions_config[version]

                # Kiểm tra có equation config chi tiết không
                if "equation" in version_config and so_an_str in version_config["equation"]:
                    return version_config["equation"][so_an_str]

                # Ưu tiên 2: Tự sinh từ base_prefix + số ẩn
                base_prefix = version_config.get("base_prefix")
                if base_prefix and so_an_str in global_defaults:
                    # Lấy 3 số cuối từ global default (912, 913, 914)
                    global_suffix = global_defaults[so_an_str][-3:]
                    return f"{base_prefix}{global_suffix}"

            # Ưu tiên 3: Fallback về global defaults
            if so_an_str in global_defaults:
                return global_defaults[so_an_str]

            # Ưu tiên 4: Fallback cuối cùng (tương thích ngược)
            legacy_prefixes = self.prefixes_data.get("prefixes", {})
            if so_an_str in legacy_prefixes:
                return legacy_prefixes[so_an_str]

            # Mặc định cuối cùng
            return "w912" if so_an == 2 else f"w91{so_an + 1}"

        except Exception as e:
            print(f"Lỗi khi lấy equation prefix: {e}")
            return f"w91{so_an + 1}"
    
    def get_version_info(self, version: str) -> Dict[str, Any]:
        """Lấy thông tin chi tiết về phiên bản"""
        try:
            versions_config = self.prefixes_data.get("versions", {})

            if version in versions_config:
                version_config = versions_config[version]
                return {
                    "version": version,
                    "base_prefix": version_config.get("base_prefix", ""),
                    "equation_prefixes": version_config.get("equation", {}),
                    "description": version_config.get("description", f"Phiên bản {version}")
                }
            else:
                return {
                    "version": version,
                    "base_prefix": "",
                    "equation_prefixes": {},
                    "description": f"Phiên bản {version} (chưa cấu hình)"
                }

        except Exception as e:
            print(f"Lỗi khi lấy thông tin phiên bản: {e}")
            return {
                "version": version,
                "base_prefix": "",
                "equation_prefixes": {},
                "description": "Lỗi cấu hình"
            }
    
    def get_all_supported_versions(self) -> List[str]:
        """Lấy danh sách tất cả phiên bản được hỗ trợ"""
        try:
            versions_config = self.prefixes_data.get("versions", {})
            return list(versions_config.keys())
        except Exception as e:
            print(f"Lỗi khi lấy danh sách phiên bản: {e}")
            return ["fx799", "fx880", "fx801", "fx802", "fx803"]
    
    def debug_prefix_info(self, version: str) -> Dict[str, Any]:
        """Debug thông tin prefix cho tất cả số ẩn - Giống TL"""
        result = {
            "current_version": version,
            "prefixes": {},
            "version_config": self.get_version_info(version)
        }

        for so_an in [2, 3, 4]:
            result["prefixes"][f"{so_an}_an"] = self.get_equation_prefix(version, so_an)

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
            self.prefixes_data = self._load_equation_prefixes()
            return True
        except Exception as e:
            print(f"Lỗi khi reload equation prefixes: {e}")
            return False