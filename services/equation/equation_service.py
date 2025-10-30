"""Equation Service - Core Logic với TL-compatible encoding (no-eval for encoding)
Updated behavior: always output keylog and distinguish between no solution vs infinite solutions using matrix rank.
"""
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
    - Behavior v2.2: Luôn sinh keylog, phân biệt vô nghiệm vs vô số nghiệm bằng rank analysis
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
        self.solutions_text = "Chưa giải hệ phương trình"
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
        self.solutions_text = "Chưa giải hệ phương trình"
        self.encoded_coefficients = []
        self.coeff_text_list = []
    
    # -------------------- VALIDATION (Compatibility with UI) --------------------
    def validate_input(self, equation_inputs: List[str]) -> Tuple[bool, str]:
        """Validate dữ liệu đầu vào: tương thích với equation_view.py"""
        n = self.current_variables
        if len(equation_inputs) < n:
            return False, f"Cần ít nhất {n} phương trình cho hệ {n} ẩn"
        for i, eq_input in enumerate(equation_inputs[:n]):
            if not eq_input.strip():
                return False, f"Phương trình {i+1} không có dữ liệu"
            parts = [p.strip() for p in eq_input.split(',')]
            non_empty = [p for p in parts if p]
            if len(non_empty) < n + 1:
                # Cho phép thiếu → encode vẫn chạy được nếu điền 0 bổ sung ở parse
                pass
        return True, "Dữ liệu hợp lệ"
    
    # -------------------- PARSE INPUTS --------------------
    def parse_equation_input(self, equation_inputs: List[str]) -> bool:
        """Parse input: tạo ma trận số cho giải nghiệm và list chuỗi cho mã hóa.
        - Không eval khi build chuỗi mã hóa
        - Có eval khi build ma trận số để giải nghiệm
        - Bổ sung '0' nếu thiếu để đủ n+1 mục mỗi phương trình
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
    
    # -------------------- ENHANCED SOLVER --------------------
    def solve_system(self) -> bool:
        """Giải hệ với phân biệt vô nghiệm vs vô số nghiệm bằng rank analysis.
        Behavior mới: không raise/propagate lỗi; chỉ set solutions_text phù hợp.
        """
        try:
            if self.A_matrix is None or self.b_vector is None:
                self.solutions = None
                self.solutions_text = "Dữ liệu không hợp lệ"
                return False
                
            # Phân tích rank để phân biệt vô nghiệm vs vô số nghiệm
            rank_A = np.linalg.matrix_rank(self.A_matrix)
            augmented = np.column_stack((self.A_matrix, self.b_vector))
            rank_augmented = np.linalg.matrix_rank(augmented)
            n = self.current_variables
            
            # Kiểm tra determinant cho quick check
            det = np.linalg.det(self.A_matrix)
            
            if abs(det) > 1e-10:
                # Hệ có nghiệm duy nhất
                try:
                    self.solutions = np.linalg.solve(self.A_matrix, self.b_vector)
                    self.solutions_text = self._format_solutions_text(self.solutions)
                    return True
                except Exception as solve_error:
                    print(f"Lỗi solve dù det != 0: {solve_error}")
                    self.solutions = None
                    self.solutions_text = "Lỗi giải hệ"
                    return False
            else:
                # Hệ suy biến (det ~ 0), dùng rank analysis
                if rank_A == rank_augmented:
                    if rank_A < n:
                        # Vô số nghiệm
                        self.solutions = None
                        self.solutions_text = "Hệ có vô số nghiệm"
                        return False
                    else:
                        # Lý thuyết rank_A == n == rank_augmented, nhưng det ~ 0 
                        # (trường hợp hiếm, có thể do numerical error)
                        self.solutions = None
                        self.solutions_text = "Hệ gần suy biến (vô số nghiệm hoặc nghiệm không ổn định)"
                        return False
                else:
                    # rank_A < rank_augmented: vô nghiệm
                    self.solutions = None
                    self.solutions_text = "Hệ vô nghiệm (mâu thuẫn)"
                    return False
                    
        except Exception as e:
            print(f"Lỗi giải hệ: {e}")
            self.solutions = None
            self.solutions_text = "Lỗi giải hệ phương trình"
            return False
    
    def _format_solutions_text(self, sols) -> str:
        try:
            variables = ['x', 'y', 'z', 't'][: self.current_variables]
            parts = []
            for i, sol in enumerate(sols):
                if abs(sol - round(sol)) < 1e-10:
                    parts.append(f"{variables[i]} = {int(round(sol))}")
                else:
                    parts.append(f"{variables[i]} = {sol:.4f}")
            return "; ".join(parts)
        except Exception as e:
            return f"Lỗi hiển thị nghiệm: {str(e)}"
    
    # -------------------- ENCODING --------------------
    def encode_coefficients_tl_format(self) -> List[str]:
        """Mã hóa theo TL: dùng CHUỖI GỐC self.coeff_text_list (không eval). Luôn cố gắng encode."""
        if not self.tl_encoding_available:
            print("Warning: TL encoding not available")
            return []
        try:
            n = self.current_variables
            expected = n * (n + 1)
            coeffs_text = self.coeff_text_list[:expected]
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
        """Sinh keylog tổng. Luôn cố gắng trả về keylog nếu có encoded_coefficients."""
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
        """Trả về text nghiệm đã phân loại hoặc fallback"""
        return self.solutions_text or "Chưa có kết quả"
    
    def get_enhanced_solutions_text(self) -> str:
        """Trả về text nghiệm chi tiết với thông tin rank (cho debug/advanced UI)"""
        if self.A_matrix is None or self.b_vector is None:
            return "Chưa parse dữ liệu"
        try:
            rank_A = np.linalg.matrix_rank(self.A_matrix)
            augmented = np.column_stack((self.A_matrix, self.b_vector))
            rank_augmented = np.linalg.matrix_rank(augmented)
            det = np.linalg.det(self.A_matrix)
            
            base_info = f"rank(A)={rank_A}, rank([A|b])={rank_augmented}, det≈{det:.2e}"
            
            if self.solutions is not None:
                return f"{self.solutions_text} | {base_info}"
            else:
                return f"{self.solutions_text} | {base_info}"
        except Exception as e:
            return f"{self.solutions_text} | Lỗi rank analysis: {str(e)}"
    
    def get_encoded_coefficients_display(self) -> List[str]:
        return self.encoded_coefficients
    
    # -------------------- WORKFLOW --------------------
    def process_complete_workflow(self, equation_inputs: List[str]) -> Tuple[bool, str, str, str]:
        """Behavior v2.2: Không chặn khi solve fail. Luôn encode và sinh keylog.
        Returns: (success_for_ui, status_msg, solutions_text_display, final_keylog)
        success_for_ui luôn True nếu encode/keylog đã sinh (dù solve fail), để UI không popup lỗi.
        """
        try:
            # Validate nhẹ để đảm bảo có dữ liệu
            is_valid, msg = self.validate_input(equation_inputs)
            if not is_valid:
                return False, msg, "Dữ liệu không hợp lệ", ""
            
            # Parse luôn (bổ sung 0 nếu thiếu)
            if not self.parse_equation_input(equation_inputs):
                # Dù parse fail hiếm gặp, vẫn trả về thông điệp chuẩn và không sinh keylog
                return False, "Lỗi parse dữ liệu đầu vào", "Dữ liệu không hợp lệ", ""
            
            # Solve (nhưng không chặn)
            self.solve_system()  # ignore boolean; solutions_text đã set nội bộ
            
            # Encode luôn
            self.encode_coefficients_tl_format()
            final_result = self.generate_final_result_tl_format()
            
            # success_for_ui: true nếu có final_result hợp lệ
            success_for_ui = bool(final_result and final_result.strip() and final_result != "Chưa có kết quả")
            status_msg = "Thành công" if success_for_ui else "Không thể sinh keylog"
            
            return success_for_ui, status_msg, self.get_solutions_text(), final_result
        except Exception as e:
            return False, f"Lỗi xử lý: {str(e)}", "Lỗi xử lý hệ thống", ""
    
    def process_complete_workflow_detailed(self, equation_inputs: List[str]) -> Tuple[bool, str, str, str, str]:
        """Workflow với thông tin rank chi tiết cho advanced UI hoặc debugging.
        Returns: (success_for_ui, status_msg, solutions_text_display, enhanced_solutions_text, final_keylog)
        """
        success, status, solutions, keylog = self.process_complete_workflow(equation_inputs)
        enhanced_solutions = self.get_enhanced_solutions_text()
        return success, status, solutions, enhanced_solutions, keylog
    
    # Backward compatibility
    def encode_coefficients(self) -> List[str]:
        return self.encode_coefficients_tl_format()
    def generate_final_result(self) -> str:
        return self.generate_final_result_tl_format()
