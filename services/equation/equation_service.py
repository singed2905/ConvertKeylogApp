"""Equation Service - Core Logic với TL-compatible encoding (no-eval for encoding)"""
import numpy as np
import math
from typing import List, Dict, Tuple, Optional, Any

try:
    from .equation_encoding_service import EquationEncodingService
    from .mapping_manager import MappingManager
except ImportError:
    print("Warning: Cannot import EquationEncodingService/MappingManager")
    EquationEncodingService = None
    MappingManager = None

class EquationService:
    """Service xử lý giải hệ phương trình - HYBRID: Numpy solver + TL encoding.
    - Giải nghiệm: dùng hệ số đã EVAL (float)
    - Mã hóa keylog: dùng CHUỖI GỐC (giữ nguyên biểu thức), không eval
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.current_variables = 2
        self.current_version = "fx799"
        
        # Dữ liệu cho giải nghiệm (float) và mã hóa (string)
        self.A_matrix = None            # float matrix cho giải nghiệm
        self.b_vector = None            # float vector cho giải nghiệm
        self.coeff_text_list: List[str] = []  # chuỗi thô cho mã hóa keylog (theo thứ tự TL)
        
        # Solutions
        self.solutions = None
        self.encoded_coefficients = []
        
        # Services
        try:
            self.encoding_service = EquationEncodingService() if EquationEncodingService else None
            self.mapper = MappingManager() if MappingManager else None
            self.tl_encoding_available = self.encoding_service is not None and self.mapper is not None
        except Exception as e:
            print(f"Warning: init services failed: {e}")
            self.encoding_service = None
            self.mapper = None
            self.tl_encoding_available = False
        
    def set_variables_count(self, count: int):
        if count in [2, 3, 4]:
            self.current_variables = count
            if self.encoding_service:
                self.encoding_service.set_variables_count(count)
            self._reset_state()
    
    def set_version(self, version: str):
        self.current_version = version
        if self.encoding_service:
            self.encoding_service.set_version(version)
    
    def _reset_state(self):
        n = self.current_variables
        self.A_matrix = np.zeros((n, n))
        self.b_vector = np.zeros(n)
        self.solutions = None
        self.encoded_coefficients = []
        self.coeff_text_list = []
    
    # -------------------- PARSE INPUTS --------------------
    def parse_equation_input(self, equation_inputs: List[str]) -> bool:
        """Parse input: tạo ma trận số cho giải nghiệm và list chuỗi cho mã hóa.
        - Không eval khi build chuỗi mã hóa
        - Có eval khi build ma trận số để giải nghiệm
        """
        try:
            n = self.current_variables
            self.A_matrix = np.zeros((n, n))
            self.b_vector = np.zeros(n)
            
            # Reset chuỗi thô (theo thứ tự TL: hàng 1..n, mỗi hàng n hệ số + 1 hằng)
            self.coeff_text_list = []
            
            for i, eq_input in enumerate(equation_inputs[:n]):
                parts = [p.strip() for p in eq_input.split(',')]
                
                # Bổ sung 0 nếu thiếu để đủ n+1 mục
                if len(parts) < n + 1:
                    parts.extend(["0"] * (n + 1 - len(parts)))
                
                # 1) Lưu nguyên chuỗi cho mã hóa
                # Thứ tự: a_i1, a_i2, ..., a_in, c_i
                self.coeff_text_list.extend(parts[:n+1])
                
                # 2) Evaluate để giải nghiệm
                for j in range(n):
                    self.A_matrix[i, j] = self._safe_eval_number(parts[j])
                self.b_vector[i] = self._safe_eval_number(parts[n])
            
            return True
        except Exception as e:
            print(f"Lỗi parse input: {e}")
            return False
    
    def _safe_eval_number(self, expr: str) -> float:
        """Eval biểu thức thành số cho giải nghiệm. Hỗ trợ sqrt, sin, cos, tan, log10, ln, pi, ^"""
        try:
            expr2 = (
                expr.replace('sqrt', 'math.sqrt')
                    .replace('sin', 'math.sin')
                    .replace('cos', 'math.cos')
                    .replace('tan', 'math.tan')
                    .replace('log', 'math.log10')
                    .replace('ln', 'math.log')
                    .replace('pi', 'math.pi')
                    .replace('^', '**')
            )
            allowed = {"__builtins__": {}, "math": math}
            return float(eval(expr2, allowed))
        except Exception:
            try:
                return float(expr)
            except Exception:
                return 0.0
    
    # -------------------- SOLVER --------------------
    def solve_system(self) -> bool:
        try:
            if self.A_matrix is None or self.b_vector is None:
                return False
            det = np.linalg.det(self.A_matrix)
            if abs(det) < 1e-10:
                self.solutions = "Hệ vô nghiệm hoặc vô số nghiệm"
                return False
            self.solutions = np.linalg.solve(self.A_matrix, self.b_vector)
            return True
        except Exception as e:
            print(f"Lỗi giải hệ: {e}")
            self.solutions = f"Lỗi giải hệ: {str(e)}"
            return False
    
    # -------------------- ENCODING --------------------
    def encode_coefficients_tl_format(self) -> List[str]:
        """Mã hóa theo TL: dùng CHUỖI GỐC self.coeff_text_list (không eval)."""
        if not self.tl_encoding_available:
            print("Warning: TL encoding not available")
            return []
        try:
            n = self.current_variables
            # Đảm bảo độ dài đúng n*(n+1)
            expected = n * (n + 1)
            coeffs_text = self.coeff_text_list[:expected]
            # Gọi service TL để encode
            result = self.encoding_service.encode_equation_data(coeffs_text, n, self.current_version)
            if result.get('success'):
                self.encoded_coefficients = result.get('encoded_coefficients', [])
                return self.encoded_coefficients
            else:
                print(f"TL encoding failed: {result.get('error')}")
                return []
        except Exception as e:
            print(f"Lỗi TL encoding: {e}")
            return []
    
    def generate_final_result_tl_format(self) -> str:
        if not self.encoded_coefficients:
            self.encode_coefficients_tl_format()
        if not self.encoded_coefficients:
            return "Chưa có kết quả"
        try:
            return self.encoding_service.get_final_keylog(self.encoded_coefficients, self.current_variables) if self.tl_encoding_available else ""
        except Exception as e:
            print(f"Lỗi generate final result: {e}")
            return "Lỗi sinh kết quả"
    
    # -------------------- TEXT UTILS --------------------
    def get_solutions_text(self) -> str:
        if self.solutions is None:
            return "Chưa giải hệ phương trình"
        if isinstance(self.solutions, str):
            return self.solutions
        try:
            variables = ['x', 'y', 'z', 't'][: self.current_variables]
            parts = []
            for i, sol in enumerate(self.solutions):
                if abs(sol - round(sol)) < 1e-10:
                    parts.append(f"{variables[i]} = {int(round(sol))}")
                else:
                    parts.append(f"{variables[i]} = {sol:.4f}")
            return "; ".join(parts)
        except Exception as e:
            return f"Lỗi hiển thị nghiệm: {e}"
    
    def get_encoded_coefficients_display(self) -> List[str]:
        return self.encoded_coefficients
    
    # -------------------- WORKFLOW --------------------
    def process_complete_workflow(self, equation_inputs: List[str]) -> Tuple[bool, str, str, str]:
        try:
            if not self.parse_equation_input(equation_inputs):
                return False, "Lỗi parse dữ liệu đầu vào", "", ""
            if not self.solve_system():
                return False, "Lỗi giải hệ phương trình", self.get_solutions_text(), ""
            self.encode_coefficients_tl_format()
            final_result = self.generate_final_result_tl_format()
            return True, "Thành công", self.get_solutions_text(), final_result
        except Exception as e:
            return False, f"Lỗi xử lý: {str(e)}", "", ""
    
    # Backward compatibility
    def encode_coefficients(self) -> List[str]:
        return self.encode_coefficients_tl_format()
    def generate_final_result(self) -> str:
        return self.generate_final_result_tl_format()