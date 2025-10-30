"""Equation Service - Core Logic for System of Linear Equations"""
import numpy as np
import math
import re
from typing import List, Dict, Tuple, Optional

class EquationService:
    """Service xử lý giải hệ phương trình tuyến tính"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.current_variables = 2
        self.current_version = "fx799"
        
        # Coefficient matrix và constants vector
        self.A_matrix = None
        self.b_vector = None
        
        # Solutions
        self.solutions = None
        self.encoded_coefficients = []
        
    def set_variables_count(self, count: int):
        """Thiết lập số ẩn"""
        if count in [2, 3, 4]:
            self.current_variables = count
            self._reset_matrices()
    
    def set_version(self, version: str):
        """Thiết lập phiên bản máy tính"""
        self.current_version = version
    
    def _reset_matrices(self):
        """Reset matrices khi thay đổi số ẩn"""
        n = self.current_variables
        self.A_matrix = np.zeros((n, n))
        self.b_vector = np.zeros(n)
        self.solutions = None
        self.encoded_coefficients = []
    
    def parse_equation_input(self, equation_inputs: List[str]) -> bool:
        """Parse input từ người dùng và tạo ma trận"""
        try:
            n = self.current_variables
            self.A_matrix = np.zeros((n, n))
            self.b_vector = np.zeros(n)
            
            for i, eq_input in enumerate(equation_inputs):
                if i >= n:  # Chỉ lấy đủ số phương trình cần thiết
                    break
                    
                if not eq_input.strip():
                    continue
                    
                # Parse hệ số từ string
                coeffs = self._parse_coefficients(eq_input)
                
                if len(coeffs) < n + 1:  # Cần n hệ số + 1 hằng số
                    # Điền số 0 cho các hệ số thiếu
                    coeffs.extend([0.0] * (n + 1 - len(coeffs)))
                
                # Gán vào ma trận A và vector b
                for j in range(n):
                    self.A_matrix[i, j] = coeffs[j]
                self.b_vector[i] = coeffs[n]
            
            return True
            
        except Exception as e:
            print(f"Lỗi parse input: {e}")
            return False
    
    def _parse_coefficients(self, input_str: str) -> List[float]:
        """Parse chuỗi input thành danh sách hệ số"""
        coeffs = []
        
        # Tách theo dấu phẩy
        parts = input_str.split(',')
        
        for part in parts:
            part = part.strip()
            if not part:
                coeffs.append(0.0)
                continue
            
            try:
                # Xử lý các biểu thức đơn giản
                value = self._evaluate_expression(part)
                coeffs.append(float(value))
            except:
                try:
                    # Fallback: parse trực tiếp thành float
                    coeffs.append(float(part))
                except:
                    coeffs.append(0.0)
        
        return coeffs
    
    def _evaluate_expression(self, expr: str) -> float:
        """Evaluate biểu thức toán học cơ bản"""
        # Thay thế các hàm toán học
        expr = expr.replace('sqrt', 'math.sqrt')
        expr = expr.replace('sin', 'math.sin')
        expr = expr.replace('cos', 'math.cos')
        expr = expr.replace('tan', 'math.tan')
        expr = expr.replace('log', 'math.log10')
        expr = expr.replace('ln', 'math.log')
        expr = expr.replace('pi', 'math.pi')
        expr = expr.replace('^', '**')
        
        # An toàn eval với hạn chế
        allowed_names = {
            "__builtins__": {},
            "math": math,
        }
        
        try:
            result = eval(expr, allowed_names)
            return result
        except:
            # Nếu không eval được, thử parse thành float
            return float(expr)
    
    def solve_system(self) -> bool:
        """Giải hệ phương trình sử dụng numpy"""
        try:
            if self.A_matrix is None or self.b_vector is None:
                return False
            
            # Kiểm tra det != 0
            det = np.linalg.det(self.A_matrix)
            if abs(det) < 1e-10:
                self.solutions = "Hệ vô nghiệm hoặc vô số nghiệm"
                return False
            
            # Giải hệ bằng Gaussian elimination
            self.solutions = np.linalg.solve(self.A_matrix, self.b_vector)
            return True
            
        except Exception as e:
            print(f"Lỗi giải hệ: {e}")
            self.solutions = f"Lỗi giải hệ: {str(e)}"
            return False
    
    def encode_coefficients(self) -> List[str]:
        """Mã hóa các hệ số thành keylog"""
        if self.A_matrix is None or self.b_vector is None:
            return []
        
        encoded = []
        n = self.current_variables
        
        # Lấy encoding config từ config file
        encoding_map = self._get_encoding_map()
        
        try:
            # Mã hóa từng hệ số của ma trận A và vector b
            for i in range(n):
                for j in range(n):
                    coeff = self.A_matrix[i, j]
                    encoded_coeff = self._encode_single_coefficient(coeff, encoding_map)
                    encoded.append(encoded_coeff)
                
                # Mã hóa hằng số
                const = self.b_vector[i]
                encoded_const = self._encode_single_coefficient(const, encoding_map)
                encoded.append(encoded_const)
            
            self.encoded_coefficients = encoded
            return encoded
            
        except Exception as e:
            print(f"Lỗi mã hóa: {e}")
            return []
    
    def _get_encoding_map(self) -> Dict:
        """Lấy bảng mã hóa từ config"""
        try:
            if (self.config and 'equation' in self.config and 
                'encoding' in self.config['equation']):
                return self.config['equation']['encoding']
        except:
            pass
        
        # Fallback encoding map cơ bản
        return {
            "numbers": {
                "0": "00", "1": "01", "2": "02", "3": "03", "4": "04",
                "5": "05", "6": "06", "7": "07", "8": "08", "9": "09",
                "-": "FF", ".": "FE"
            },
            "prefix": "EQ"
        }
    
    def _encode_single_coefficient(self, coeff: float, encoding_map: Dict) -> str:
        """Mã hóa 1 hệ số thành keylog"""
        try:
            # Chuyển về string và format
            if coeff == int(coeff):
                coeff_str = str(int(coeff))
            else:
                coeff_str = f"{coeff:.3f}".rstrip('0').rstrip('.')
            
            # Mã hóa từng ký tự
            numbers_map = encoding_map.get('numbers', {})
            encoded = ""
            
            for char in coeff_str:
                if char in numbers_map:
                    encoded += numbers_map[char]
                else:
                    encoded += char  # Giữ nguyên nếu không tìm thấy
            
            return encoded
            
        except Exception as e:
            print(f"Lỗi encode coefficient {coeff}: {e}")
            return "00"
    
    def generate_final_result(self) -> str:
        """Sinh kết quả cuối cùng cho máy tính"""
        if not self.encoded_coefficients or self.solutions is None:
            return "Chưa có kết quả"
        
        try:
            # Lấy prefix từ config
            prefix = self._get_version_prefix()
            
            # Tạo chuỗi kết quả
            encoded_str = "".join(self.encoded_coefficients)
            
            # Thêm solutions (nếu là số)
            solution_part = ""
            if isinstance(self.solutions, np.ndarray):
                # Mã hóa solutions
                encoding_map = self._get_encoding_map()
                for sol in self.solutions:
                    encoded_sol = self._encode_single_coefficient(sol, encoding_map)
                    solution_part += encoded_sol
            
            # Kết quả cuối cùng
            final_result = f"{prefix}{encoded_str}SOL{solution_part}"
            return final_result
            
        except Exception as e:
            print(f"Lỗi generate final result: {e}")
            return "Lỗi sinh kết quả"
    
    def _get_version_prefix(self) -> str:
        """Lấy prefix cho phiên bản hiện tại"""
        try:
            if (self.config and 'equation' in self.config and 
                'prefixes' in self.config['equation'] and
                'versions' in self.config['equation']['prefixes']):
                
                version_prefixes = self.config['equation']['prefixes']['versions']
                if self.current_version in version_prefixes:
                    return version_prefixes[self.current_version].get('base_prefix', 'EQ')
        except:
            pass
        
        # Fallback prefixes
        fallback_prefixes = {
            "fx799": "EQ799",
            "fx800": "EQ800", 
            "fx801": "EQ801",
            "fx802": "EQ802",
            "fx803": "EQ803"
        }
        return fallback_prefixes.get(self.current_version, "EQ")
    
    def get_solutions_text(self) -> str:
        """Lấy text hiển thị nghiệm"""
        if self.solutions is None:
            return "Chưa giải hệ phương trình"
        
        if isinstance(self.solutions, str):
            return self.solutions
        
        try:
            # Hiển thị nghiệm
            n = self.current_variables
            variables = ['x', 'y', 'z', 't'][:n]
            
            result_parts = []
            for i, sol in enumerate(self.solutions):
                if i < len(variables):
                    if abs(sol - round(sol)) < 1e-10:
                        result_parts.append(f"{variables[i]} = {int(round(sol))}")
                    else:
                        result_parts.append(f"{variables[i]} = {sol:.4f}")
            
            return "; ".join(result_parts)
            
        except Exception as e:
            return f"Lỗi hiển thị nghiệm: {e}"
    
    def get_encoded_coefficients_display(self) -> List[str]:
        """Lấy encoded coefficients để hiển thị trong grid"""
        return self.encoded_coefficients
    
    def process_complete_workflow(self, equation_inputs: List[str]) -> Tuple[bool, str, str, str]:
        """Xử lý hoàn chỉnh: parse -> solve -> encode -> generate"""
        try:
            # Bước 1: Parse input
            parse_success = self.parse_equation_input(equation_inputs)
            if not parse_success:
                return False, "Lỗi parse dữ liệu đầu vào", "", ""
            
            # Bước 2: Giải hệ
            solve_success = self.solve_system()
            if not solve_success:
                solutions_text = self.get_solutions_text()
                return False, "Lỗi giải hệ phương trình", solutions_text, ""
            
            # Bước 3: Mã hóa coefficients
            self.encode_coefficients()
            
            # Bước 4: Sinh kết quả cuối cùng
            solutions_text = self.get_solutions_text()
            final_result = self.generate_final_result()
            
            return True, "Thành công", solutions_text, final_result
            
        except Exception as e:
            return False, f"Lỗi xử lý: {str(e)}", "", ""
    
    def get_matrix_info(self) -> str:
        """Lấy thông tin ma trận để debug"""
        if self.A_matrix is None or self.b_vector is None:
            return "Chưa có dữ liệu"
        
        try:
            info = f"Ma trận A ({self.current_variables}x{self.current_variables}):\n"
            info += str(self.A_matrix) + "\n\n"
            info += f"Vector b: {self.b_vector}\n"
            info += f"Det(A): {np.linalg.det(self.A_matrix):.6f}"
            return info
        except:
            return "Lỗi hiển thị thông tin ma trận"
    
    def validate_input(self, equation_inputs: List[str]) -> Tuple[bool, str]:
        """Validate dữ liệu đầu vào"""
        n = self.current_variables
        
        # Kiểm tra số phương trình
        if len(equation_inputs) < n:
            return False, f"Cần ít nhất {n} phương trình cho hệ {n} ẩn"
        
        # Kiểm tra mỗi phương trình có dữ liệu
        for i, eq_input in enumerate(equation_inputs[:n]):
            if not eq_input.strip():
                return False, f"Phương trình {i+1} không có dữ liệu"
            
            # Kiểm tra số hệ số
            coeffs = eq_input.split(',')
            if len([c for c in coeffs if c.strip()]) < n + 1:
                return False, f"Phương trình {i+1} cần {n+1} hệ số ({n} hệ số + 1 hằng số)"
        
        return True, "Dữ liệu hợp lệ"