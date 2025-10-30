"""Equation Service - Core Logic với TL-compatible encoding"""
import numpy as np
import math
import re
from typing import List, Dict, Tuple, Optional
from .equation_encoding_service import EquationEncodingService

class EquationService:
    """Service xử lý giải hệ phương trình - HYBRID: Numpy solver + TL encoding"""
    
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
        
        # TL Encoding Service
        try:
            self.encoding_service = EquationEncodingService()
            self.tl_encoding_available = True
        except Exception as e:
            print(f"Warning: TL encoding service failed: {e}")
            self.encoding_service = None
            self.tl_encoding_available = False
        
    def set_variables_count(self, count: int):
        """Thiết lập số ẩn"""
        if count in [2, 3, 4]:
            self.current_variables = count
            if self.encoding_service:
                self.encoding_service.set_variables_count(count)
            self._reset_matrices()
    
    def set_version(self, version: str):
        """Thiết lập phiên bản máy tính"""
        self.current_version = version
        if self.encoding_service:
            self.encoding_service.set_version(version)
    
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
        """Giải hệ phương trình sử dụng numpy - GIỮU NUMPY"""
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
    
    def encode_coefficients_tl_format(self) -> List[str]:
        """Mã hóa coefficients theo format TL - THAY THẾ METHOD CŨ"""
        if self.A_matrix is None or self.b_vector is None:
            return []
        
        if not self.tl_encoding_available:
            print("Warning: TL encoding not available, using fallback")
            return self._encode_coefficients_fallback()
        
        try:
            # Chuẩn bị danh sách hệ số theo format TL
            n = self.current_variables
            danh_sach_he_so = []
            
            # Flatten ma trận A và vector b thành danh sách string
            for i in range(n):
                for j in range(n):
                    coeff = self.A_matrix[i, j]
                    danh_sach_he_so.append(str(coeff))
                # Thêm hằng số
                const = self.b_vector[i]
                danh_sach_he_so.append(str(const))
            
            # Sử dụng TL encoding service
            encoding_result = self.encoding_service.encode_equation_data(
                danh_sach_he_so, n, self.current_version
            )
            
            if encoding_result['success']:
                self.encoded_coefficients = encoding_result['encoded_coefficients']
                return self.encoded_coefficients
            else:
                print(f"TL encoding failed: {encoding_result.get('error', 'Unknown error')}")
                return self._encode_coefficients_fallback()
            
        except Exception as e:
            print(f"Lỗi TL encoding: {e}")
            return self._encode_coefficients_fallback()
    
    def _encode_coefficients_fallback(self) -> List[str]:
        """Fallback encoding nếu TL encoding không hoạt động"""
        if self.A_matrix is None or self.b_vector is None:
            return []
        
        encoded = []
        n = self.current_variables
        
        # Simple number-to-string encoding
        for i in range(n):
            for j in range(n):
                coeff = self.A_matrix[i, j]
                encoded.append(str(coeff).replace('-', 'p').replace('.', '_'))
            # Hằng số
            const = self.b_vector[i]
            encoded.append(str(const).replace('-', 'p').replace('.', '_'))
        
        self.encoded_coefficients = encoded
        return encoded
    
    def generate_final_result_tl_format(self) -> str:
        """Sinh kết quả cuối cùng theo format TL - THAY THẾ METHOD CŨ"""
        if not self.encoded_coefficients:
            # Tự động encode nếu chưa có
            self.encode_coefficients_tl_format()
        
        if not self.encoded_coefficients:
            return "Chưa có kết quả"
        
        try:
            # Sử dụng TL encoding service để tạo kết quả cuối
            if self.tl_encoding_available:
                final_result = self.encoding_service.get_final_keylog(
                    self.encoded_coefficients, 
                    self.current_variables
                )
                return final_result
            else:
                # Fallback format
                return "FALLBACK_" + "_".join(self.encoded_coefficients)
            
        except Exception as e:
            print(f"Lỗi generate final result: {e}")
            return "Lỗi sinh kết quả"
    
    def get_solutions_text(self) -> str:
        """Lấy text hiển thị nghiệm - GIỮU NGUYÊN"""
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
        """Xử lý hoàn chỉnh: parse -> solve -> encode TL -> generate TL"""
        try:
            # Bước 1: Parse input
            parse_success = self.parse_equation_input(equation_inputs)
            if not parse_success:
                return False, "Lỗi parse dữ liệu đầu vào", "", ""
            
            # Bước 2: Giải hệ với numpy (giữ ưu điểm)
            solve_success = self.solve_system()
            if not solve_success:
                solutions_text = self.get_solutions_text()
                return False, "Lỗi giải hệ phương trình", solutions_text, ""
            
            # Bước 3: Mã hóa coefficients theo TL
            self.encode_coefficients_tl_format()
            
            # Bước 4: Sinh kết quả cuối cùng theo TL format
            solutions_text = self.get_solutions_text()
            final_result = self.generate_final_result_tl_format()
            
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
            info += f"Det(A): {np.linalg.det(self.A_matrix):.6f}\n"
            info += f"TL Encoding: {'Available' if self.tl_encoding_available else 'Failed'}"
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
    
    def test_tl_compatibility(self, test_coefficients: List[str]) -> Dict[str, Any]:
        """Test tương thích với TL - để so sánh"""
        if not self.tl_encoding_available:
            return {"error": "TL encoding service not available"}
        
        try:
            # Test encoding
            encoding_result = self.encoding_service.encode_equation_data(
                test_coefficients, 
                self.current_variables, 
                self.current_version
            )
            
            return {
                "success": encoding_result['success'],
                "input_coefficients": test_coefficients,
                "encoded_coefficients": encoding_result.get('encoded_coefficients', []),
                "final_keylog": encoding_result.get('total_result', ""),
                "prefix_used": encoding_result.get('prefix_used', ""),
                "version": self.current_version,
                "variables": self.current_variables
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
    
    # Backward compatibility - alias các method cũ
    def encode_coefficients(self) -> List[str]:
        """Alias cho encode_coefficients_tl_format"""
        return self.encode_coefficients_tl_format()
    
    def generate_final_result(self) -> str:
        """Alias cho generate_final_result_tl_format"""
        return self.generate_final_result_tl_format()