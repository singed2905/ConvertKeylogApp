"""Equation View Components - Configuration Manager"""

class EquationConfigManager:
    """Quản lý cấu hình cho Equation Mode"""
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def get_available_versions(self):
        """Lấy danh sách phiên bản từ config hoặc sử dụng mặc định"""
        try:
            if self.config and 'common' in self.config and 'versions' in self.config['common']:
                versions_data = self.config['common']['versions']
                if 'versions' in versions_data:
                    return versions_data['versions']
        except Exception as e:
            print(f"Warning: Không thể load versions từ config: {e}")
        
        # Fallback nếu không có config
        return ["fx799", "fx800", "fx801", "fx802", "fx803"]
    
    def get_equation_prefixes(self):
        """Lấy prefixes cho equation từ config"""
        try:
            if self.config and 'equation' in self.config and 'prefixes' in self.config['equation']:
                prefixes_data = self.config['equation']['prefixes']
                if 'versions' in prefixes_data:
                    return prefixes_data['versions']
        except Exception as e:
            print(f"Warning: Không thể load equation prefixes từ config: {e}")
        
        return None
    
    def get_equation_mappings(self):
        """Lấy ánh xạ mã hóa cho equation"""
        try:
            if self.config and 'equation' in self.config and 'mappings' in self.config['equation']:
                return self.config['equation']['mappings']
        except Exception as e:
            print(f"Warning: Không thể load equation mappings: {e}")
        
        # Fallback mappings
        return {
            "coefficient_encoding": {
                "method": "decimal_to_keylog",
                "precision": 3
            },
            "solution_encoding": {
                "method": "solution_to_sequence",
                "format": "compressed"
            }
        }
    
    def get_equation_templates(self):
        """Lấy mẫu Excel template cho equation"""
        try:
            if self.config and 'equation' in self.config and 'excel_templates' in self.config['equation']:
                return self.config['equation']['excel_templates']
        except Exception as e:
            print(f"Warning: Không thể load equation templates: {e}")
        
        # Fallback templates
        return {
            "2_variables": {
                "headers": ["a11", "a12", "c1", "a21", "a22", "c2", "keylog"],
                "sample_data": [[1, 2, 3, 4, 5, 6, ""]]
            },
            "3_variables": {
                "headers": ["a11", "a12", "a13", "c1", "a21", "a22", "a23", "c2", "a31", "a32", "a33", "c3", "keylog"],
                "sample_data": [[1, 0, 1, 4, 2, 1, 0, 3, 0, 1, 2, 5, ""]]
            },
            "4_variables": {
                "headers": ["a11", "a12", "a13", "a14", "c1", "a21", "a22", "a23", "a24", "c2", 
                          "a31", "a32", "a33", "a34", "c3", "a41", "a42", "a43", "a44", "c4", "keylog"],
                "sample_data": [[1, 0, 0, 1, 2, 0, 1, 0, 1, 3, 0, 0, 1, 0, 4, 1, 1, 1, 1, 5, ""]]
            }
        }
    
    def get_solver_config(self):
        """Lấy cấu hình cho solver"""
        try:
            if self.config and 'equation' in self.config and 'solver' in self.config['equation']:
                return self.config['equation']['solver']
        except Exception as e:
            print(f"Warning: Không thể load solver config: {e}")
        
        # Fallback solver config
        return {
            "method": "gaussian_elimination",
            "tolerance": 1e-10,
            "max_iterations": 1000,
            "pivot_strategy": "partial"
        }
    
    def get_display_config(self):
        """Lấy cấu hình hiển thị"""
        try:
            if self.config and 'equation' in self.config and 'display' in self.config['equation']:
                return self.config['equation']['display']
        except Exception as e:
            print(f"Warning: Không thể load display config: {e}")
        
        # Fallback display config
        return {
            "precision": 6,
            "scientific_notation": False,
            "show_steps": False,
            "color_coding": True
        }
    
    def get_validation_rules(self):
        """Lấy quy tắc validation"""
        try:
            if self.config and 'equation' in self.config and 'validation' in self.config['equation']:
                return self.config['equation']['validation']
        except Exception as e:
            print(f"Warning: Không thể load validation rules: {e}")
        
        # Fallback validation rules
        return {
            "required_fields": True,
            "numeric_only": False,  # Allow expressions
            "max_coefficient_value": 1000000,
            "min_coefficient_value": -1000000,
            "allow_zero_determinant": True
        }