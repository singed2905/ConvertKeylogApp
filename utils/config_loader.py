import json
import os
from typing import Dict, Any, Optional

class ConfigLoader:
    """Utility class để load config theo mode từ cấu trúc mới"""
    
    def __init__(self, base_path: str = "config"):
        self.base_path = base_path
        self._cache = {}
    
    def load_common_config(self, config_name: str) -> Dict[str, Any]:
        """Load config từ thư mục common"""
        return self._load_json(f"common/{config_name}.json")
    
    def load_geometry_config(self, config_name: str) -> Dict[str, Any]:
        """Load config từ thư mục geometry_mode"""
        return self._load_json(f"geometry_mode/{config_name}.json")
    
    def load_equation_config(self, config_name: str) -> Dict[str, Any]:
        """Load config từ thư mục equation_mode"""
        return self._load_json(f"equation_mode/{config_name}.json")
    
    def load_polynomial_config(self, config_name: str) -> Dict[str, Any]:
        """Load config từ thư mục polynomial_mode"""
        return self._load_json(f"polynomial_mode/{config_name}.json")
    
    def load_version_config(self, version: str) -> Dict[str, Any]:
        """Load config cho version cụ thể"""
        return self._load_json(f"version_configs/{version}_config.json")
    
    def get_mode_config(self, mode: str) -> Dict[str, Any]:
        """Load tất cả config cần thiết cho một mode"""
        config = {
            'common': {
                'modes': self.load_common_config('modes'),
                'versions': self.load_common_config('versions'),
                'version_mapping': self.load_common_config('version_mapping')
            }
        }
        
        if mode == "Geometry Mode":
            config['geometry'] = {
                'excel_mapping': self.load_geometry_config('geometry_excel_mapping'),
                'operations': self.load_geometry_config('geometry_operations')
            }
        elif mode == "Equation Mode":
            config['equation'] = {
                'prefixes': self.load_equation_config('equation_prefixes'),
                'excel_mapping': self.load_equation_config('equation_excel_mapping')
            }
        elif mode == "Polynomial Equation Mode":
            config['polynomial'] = {
                'mapping': self.load_polynomial_config('polynomial_mapping'),
                'math_replacements': self.load_polynomial_config('math_replacements')
            }
        
        return config
    
    def _load_json(self, relative_path: str) -> Dict[str, Any]:
        """Load file JSON với cache"""
        if relative_path in self._cache:
            return self._cache[relative_path]
        
        full_path = os.path.join(self.base_path, relative_path)
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._cache[relative_path] = data
                return data
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {full_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file {full_path}: {e}")
    
    def clear_cache(self):
        """Xóa cache để reload config"""
        self._cache.clear()
    
    def get_available_modes(self) -> list:
        """Lấy danh sách modes có sẵn"""
        modes_config = self.load_common_config('modes')
        return modes_config.get('modes', [])
    
    def get_available_versions(self) -> list:
        """Lấy danh sách versions có sẵn"""
        versions_config = self.load_common_config('versions')
        return versions_config.get('versions', [])
    
    def get_default_version(self) -> str:
        """Lấy version mặc định"""
        versions_config = self.load_common_config('versions')
        return versions_config.get('default_version', 'fx799')

# Singleton instance
config_loader = ConfigLoader()
