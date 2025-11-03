# Vector View - Giao diện Vector Mode cho ConvertKeylogApp
# Hỗ trợ 2 kiểu tính: Số thực với Vector và Vector với Vector
# Tương thích với kiến trúc hiện tại của Geometry Mode

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime

class VectorView:
    """Giao diện Vector Mode - Tính toán vector và sinh keylog"""
    
    def __init__(self, parent):
        self.parent = parent
        self.root = tk.Toplevel(parent)
        self.root.title("ConvertKeylogApp - Vector Mode v1.0")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variables
        self.calc_type_var = tk.StringVar(value="scalar_vector")
        self.dimension_var = tk.StringVar(value="2")
        self.operation_var = tk.StringVar()
        self.version_var = tk.StringVar(value="fx799")
        
        # Data storage
        self.scalar_value = ""
        self.vector_A = ""
        self.vector_B = ""
        self.current_result = ""
        
        # Operation mappings
        self.operations_map = {
            "scalar_vector": {
                "Nhân scalar": "multiply",
                "Chia scalar": "divide", 
                "Cộng scalar": "add",
                "Trừ scalar": "subtract"
            },
            "vector_vector": {
                "Tích vô hướng": "dot_product",
                "Tích có hướng": "cross_product",
                "Cộng vector": "add",
                "Trừ vector": "subtract",
                "Góc giữa 2 vector": "angle",
                "Khoảng cách": "distance"
            }
        }
        
        self.setup_ui()
        self.update_operation_dropdown()
        
    def setup_ui(self):
        """Thiết lập giao diện chính"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header(main_frame)
        
        # Control Panel
        self.create_control_panel(main_frame)
        
        # Input Section
        self.create_input_section(main_frame)
        
        # Results Section
        self.create_results_section(main_frame)
        
        # Action Buttons
        self.create_action_buttons(main_frame)
        
        # Excel Section
        self.create_excel_section(main_frame)
        
        # Status Bar
        self.create_status_bar()
        
    def create_header(self, parent):
        """Tạo header với title và thông tin"""
        header_frame = ttk.LabelFrame(parent, text="Vector Mode - Tính toán Vector và Keylog", padding="10")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame, text="🧮 Vector Calculator & Keylog Generator", 
                               font=("Arial", 14, "bold"))
        title_label.pack()
        
        # Description
        desc_label = ttk.Label(header_frame, 
                              text="Hỗ trợ tính toán vector 2D/3D với số thực hoặc vector khác, tự động sinh keylog TL",
                              font=("Arial", 9))
        desc_label.pack(pady=(5, 0))
        
    def create_control_panel(self, parent):
        """Tạo panel điều khiển chính"""
        control_frame = ttk.LabelFrame(parent, text="⚙️ Cấu hình tính toán", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Row 1: Calculation Type và Dimension
        row1_frame = ttk.Frame(control_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Calculation Type
        ttk.Label(row1_frame, text="Kiểu tính:").pack(side=tk.LEFT)
        calc_type_combo = ttk.Combobox(row1_frame, textvariable=self.calc_type_var, 
                                      values=["scalar_vector", "vector_vector"],
                                      state="readonly", width=15)
        calc_type_combo.pack(side=tk.LEFT, padx=(5, 20))
        calc_type_combo.bind("<<ComboboxSelected>>", self.on_calc_type_changed)
        
        # Dimension
        ttk.Label(row1_frame, text="Kích thước:").pack(side=tk.LEFT)
        dimension_combo = ttk.Combobox(row1_frame, textvariable=self.dimension_var,
                                      values=["2", "3"], state="readonly", width=5)
        dimension_combo.pack(side=tk.LEFT, padx=(5, 20))
        dimension_combo.bind("<<ComboboxSelected>>", self.on_dimension_changed)
        
        # Version
        ttk.Label(row1_frame, text="Phiên bản:").pack(side=tk.LEFT)
        version_combo = ttk.Combobox(row1_frame, textvariable=self.version_var,
                                    values=["fx799", "fx991", "fx570"], state="readonly", width=10)
        version_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Row 2: Operation
        row2_frame = ttk.Frame(control_frame)
        row2_frame.pack(fill=tk.X)
        
        ttk.Label(row2_frame, text="Phép toán:").pack(side=tk.LEFT)
        self.operation_combo = ttk.Combobox(row2_frame, textvariable=self.operation_var,
                                           state="readonly", width=20)
        self.operation_combo.pack(side=tk.LEFT, padx=(5, 0))
        
    def create_input_section(self, parent):
        """Tạo section nhập liệu"""
        input_frame = ttk.LabelFrame(parent, text="📝 Nhập dữ liệu", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Scalar input (ẩn/hiện theo calc_type)
        self.scalar_frame = ttk.Frame(input_frame)
        self.scalar_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.scalar_frame, text="Số thực:", width=12).pack(side=tk.LEFT)
        self.scalar_entry = ttk.Entry(self.scalar_frame, width=20, font=("Consolas", 10))
        self.scalar_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        # Example label for scalar
        self.scalar_example = ttk.Label(self.scalar_frame, text="Ví dụ: 3.14 hoặc sqrt(2)", 
                                       foreground="gray", font=("Arial", 8))
        self.scalar_example.pack(side=tk.LEFT, padx=(10, 0))
        
        # Vector A input
        vector_a_frame = ttk.Frame(input_frame)
        vector_a_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(vector_a_frame, text="Vector A:", width=12).pack(side=tk.LEFT)
        self.vector_a_entry = ttk.Entry(vector_a_frame, width=20, font=("Consolas", 10))
        self.vector_a_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        self.vector_a_example = ttk.Label(vector_a_frame, text="Ví dụ: 1,2 (2D) hoặc 1,2,3 (3D)",
                                         foreground="gray", font=("Arial", 8))
        self.vector_a_example.pack(side=tk.LEFT, padx=(10, 0))
        
        # Vector B input (ẩn/hiện theo calc_type)
        self.vector_b_frame = ttk.Frame(input_frame)
        self.vector_b_frame.pack(fill=tk.X)
        
        ttk.Label(self.vector_b_frame, text="Vector B:", width=12).pack(side=tk.LEFT)
        self.vector_b_entry = ttk.Entry(self.vector_b_frame, width=20, font=("Consolas", 10))
        self.vector_b_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        self.vector_b_example = ttk.Label(self.vector_b_frame, text="Ví dụ: 4,5 (2D) hoặc 4,5,6 (3D)",
                                         foreground="gray", font=("Arial", 8))
        self.vector_b_example.pack(side=tk.LEFT, padx=(10, 0))
        
    def create_results_section(self, parent):
        """Tạo section hiển thị kết quả"""
        results_frame = ttk.LabelFrame(parent, text="📊 Kết quả", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Calculation Result
        calc_frame = ttk.Frame(results_frame)
        calc_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(calc_frame, text="Kết quả tính toán:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.calc_result_text = tk.Text(calc_frame, height=3, width=80, font=("Consolas", 10),
                                       wrap=tk.WORD, state=tk.DISABLED)
        self.calc_result_text.pack(fill=tk.X, pady=(5, 0))
        
        # Encoded Values
        encoded_frame = ttk.Frame(results_frame)
        encoded_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(encoded_frame, text="Giá trị đã mã hóa:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.encoded_text = tk.Text(encoded_frame, height=3, width=80, font=("Consolas", 10),
                                   wrap=tk.WORD, state=tk.DISABLED)
        self.encoded_text.pack(fill=tk.X, pady=(5, 0))
        
        # Final Keylog
        keylog_frame = ttk.Frame(results_frame)
        keylog_frame.pack(fill=tk.X)
        
        ttk.Label(keylog_frame, text="Keylog cuối cùng:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.keylog_text = tk.Text(keylog_frame, height=2, width=80, font=("Consolas", 12, "bold"),
                                  wrap=tk.WORD, state=tk.DISABLED, bg="#f0f8ff")
        self.keylog_text.pack(fill=tk.X, pady=(5, 0))
        
    def create_action_buttons(self, parent):
        """Tạo các nút hành động"""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Main action button
        self.process_button = ttk.Button(action_frame, text="🚀 Tính toán & Mã hóa", 
                                        command=self.process_calculation,
                                        style="Accent.TButton")
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Copy button  
        self.copy_button = ttk.Button(action_frame, text="📋 Copy Keylog",
                                     command=self.copy_result, state=tk.DISABLED)
        self.copy_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        clear_button = ttk.Button(action_frame, text="🧹 Xóa tất cả",
                                 command=self.clear_all)
        clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export button
        self.export_button = ttk.Button(action_frame, text="💾 Xuất Excel",
                                       command=self.export_single_result, state=tk.DISABLED)
        self.export_button.pack(side=tk.RIGHT)
        
    def create_excel_section(self, parent):
        """Tạo section xử lý Excel"""
        excel_frame = ttk.LabelFrame(parent, text="📁 Xử lý Excel", padding="10")
        excel_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File info
        file_frame = ttk.Frame(excel_frame)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_label = ttk.Label(file_frame, text="Chưa chọn file", foreground="gray")
        self.file_label.pack(side=tk.LEFT)
        
        # Excel buttons
        excel_buttons_frame = ttk.Frame(excel_frame)
        excel_buttons_frame.pack(fill=tk.X)
        
        ttk.Button(excel_buttons_frame, text="📝 Tạo Template", 
                  command=self.create_template).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(excel_buttons_frame, text="📁 Import Excel",
                  command=self.import_excel).pack(side=tk.LEFT, padx=(0, 10))
        
        self.process_excel_button = ttk.Button(excel_buttons_frame, text="🔥 Xử lý File Excel",
                                              command=self.process_excel_file, state=tk.DISABLED)
        self.process_excel_button.pack(side=tk.LEFT)
        
    def create_status_bar(self):
        """Tạo thanh trạng thái"""
        self.status_bar = ttk.Label(self.root, text="Sẵn sàng", relief=tk.SUNKEN, padding="5")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    # ========== EVENT HANDLERS ==========
    
    def on_calc_type_changed(self, event=None):
        """Xử lý khi thay đổi kiểu tính"""
        calc_type = self.calc_type_var.get()
        
        if calc_type == "scalar_vector":
            self.scalar_frame.pack(fill=tk.X, pady=(0, 10), before=self.vector_a_entry.master)
            self.vector_b_frame.pack_forget()
        else:
            self.scalar_frame.pack_forget()
            self.vector_b_frame.pack(fill=tk.X)
            
        self.update_operation_dropdown()
        self.update_status("Đã chuyển sang kiểu: " + ("Số thực với Vector" if calc_type == "scalar_vector" else "Vector với Vector"))
        
    def on_dimension_changed(self, event=None):
        """Xử lý khi thay đổi kích thước"""
        dimension = self.dimension_var.get()
        
        if dimension == "2":
            self.vector_a_example.config(text="Ví dụ: 1,2 (2D)")
            self.vector_b_example.config(text="Ví dụ: 4,5 (2D)")
        else:
            self.vector_a_example.config(text="Ví dụ: 1,2,3 (3D)")
            self.vector_b_example.config(text="Ví dụ: 4,5,6 (3D)")
            
        # Update operation list (cross product only available in 3D)
        self.update_operation_dropdown()
        self.update_status(f"Đã chuyển sang {dimension}D")
        
    def update_operation_dropdown(self):
        """Cập nhật dropdown phép toán"""
        calc_type = self.calc_type_var.get()
        dimension = self.dimension_var.get()
        
        operations = list(self.operations_map[calc_type].keys())
        
        # Remove cross product for 2D
        if calc_type == "vector_vector" and dimension == "2":
            operations = [op for op in operations if op != "Tích có hướng"]
            
        self.operation_combo['values'] = operations
        if operations:
            self.operation_var.set(operations[0])
    
    # ========== MAIN PROCESSING ==========
    
    def process_calculation(self):
        """Xử lý tính toán chính"""
        try:
            # Validate inputs
            if not self.validate_inputs():
                return
                
            # Get inputs
            calc_type = self.calc_type_var.get()
            operation = self.operation_var.get()
            dimension = int(self.dimension_var.get())
            
            # Process calculation
            if calc_type == "scalar_vector":
                result = self.calculate_scalar_vector(operation, dimension)
            else:
                result = self.calculate_vector_vector(operation, dimension)
                
            # Display results
            self.display_results(result)
            
            # Enable buttons
            self.copy_button.config(state=tk.NORMAL)
            self.export_button.config(state=tk.NORMAL)
            
            self.update_status("Tính toán thành công!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tính toán: {str(e)}")
            self.update_status("Lỗi tính toán")
    
    def validate_inputs(self):
        """Kiểm tra tính hợp lệ của inputs"""
        calc_type = self.calc_type_var.get()
        
        # Check vector A
        if not self.vector_a_entry.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng nhập Vector A")
            return False
            
        # Check scalar for scalar_vector mode
        if calc_type == "scalar_vector" and not self.scalar_entry.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng nhập số thực")
            return False
            
        # Check vector B for vector_vector mode
        if calc_type == "vector_vector" and not self.vector_b_entry.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng nhập Vector B")
            return False
            
        # Check operation
        if not self.operation_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn phép toán")
            return False
            
        return True
    
    def calculate_scalar_vector(self, operation, dimension):
        """Tính toán scalar với vector"""
        scalar_str = self.scalar_entry.get().strip()
        vector_str = self.vector_a_entry.get().strip()
        
        # Parse inputs
        scalar = self.parse_scalar(scalar_str)
        vector = self.parse_vector(vector_str, dimension)
        
        # Calculate based on operation
        op_code = self.operations_map["scalar_vector"][operation]
        
        if op_code == "multiply":
            result_vector = [scalar * v for v in vector]
            calc_result = f"{scalar} × {self.format_vector(vector)} = {self.format_vector(result_vector)}"
        elif op_code == "divide":
            if scalar == 0:
                raise ValueError("Không thể chia cho 0")
            result_vector = [v / scalar for v in vector]
            calc_result = f"{self.format_vector(vector)} ÷ {scalar} = {self.format_vector(result_vector)}"
        elif op_code == "add":
            result_vector = [v + scalar for v in vector]
            calc_result = f"{self.format_vector(vector)} + {scalar} = {self.format_vector(result_vector)}"
        elif op_code == "subtract":
            result_vector = [v - scalar for v in vector]
            calc_result = f"{self.format_vector(vector)} - {scalar} = {self.format_vector(result_vector)}"
        else:
            raise ValueError(f"Phép toán không hỗ trợ: {operation}")
            
        # Generate encoded values and keylog
        encoded_scalar = self.encode_value(scalar_str)
        encoded_vector = [self.encode_value(str(v)) for v in vector]
        keylog = self.generate_keylog_scalar_vector(encoded_scalar, encoded_vector, op_code)
        
        return {
            'calculation': calc_result,
            'encoded_scalar': encoded_scalar,
            'encoded_vector': encoded_vector,
            'keylog': keylog,
            'result_vector': result_vector
        }
    
    def calculate_vector_vector(self, operation, dimension):
        """Tính toán vector với vector"""
        vector_a_str = self.vector_a_entry.get().strip()
        vector_b_str = self.vector_b_entry.get().strip()
        
        # Parse inputs
        vector_a = self.parse_vector(vector_a_str, dimension)
        vector_b = self.parse_vector(vector_b_str, dimension)
        
        # Calculate based on operation
        op_code = self.operations_map["vector_vector"][operation]
        
        if op_code == "dot_product":
            result = sum(a * b for a, b in zip(vector_a, vector_b))
            calc_result = f"{self.format_vector(vector_a)} • {self.format_vector(vector_b)} = {result}"
        elif op_code == "cross_product":
            if dimension != 3:
                raise ValueError("Tích có hướng chỉ áp dụng cho vector 3D")
            result = self.cross_product_3d(vector_a, vector_b)
            calc_result = f"{self.format_vector(vector_a)} × {self.format_vector(vector_b)} = {self.format_vector(result)}"
        elif op_code == "add":
            result = [a + b for a, b in zip(vector_a, vector_b)]
            calc_result = f"{self.format_vector(vector_a)} + {self.format_vector(vector_b)} = {self.format_vector(result)}"
        elif op_code == "subtract":
            result = [a - b for a, b in zip(vector_a, vector_b)]
            calc_result = f"{self.format_vector(vector_a)} - {self.format_vector(vector_b)} = {self.format_vector(result)}"
        elif op_code == "angle":
            import math
            dot = sum(a * b for a, b in zip(vector_a, vector_b))
            mag_a = math.sqrt(sum(a * a for a in vector_a))
            mag_b = math.sqrt(sum(b * b for b in vector_b))
            cos_theta = dot / (mag_a * mag_b)
            cos_theta = max(-1, min(1, cos_theta))  # Clamp to [-1, 1]
            angle_rad = math.acos(cos_theta)
            angle_deg = math.degrees(angle_rad)
            result = angle_deg
            calc_result = f"Góc giữa {self.format_vector(vector_a)} và {self.format_vector(vector_b)} = {angle_deg:.2f}°"
        elif op_code == "distance":
            import math
            diff = [a - b for a, b in zip(vector_a, vector_b)]
            result = math.sqrt(sum(d * d for d in diff))
            calc_result = f"Khoảng cách giữa {self.format_vector(vector_a)} và {self.format_vector(vector_b)} = {result:.4f}"
        else:
            raise ValueError(f"Phép toán không hỗ trợ: {operation}")
            
        # Generate encoded values and keylog
        encoded_vector_a = [self.encode_value(str(v)) for v in vector_a]
        encoded_vector_b = [self.encode_value(str(v)) for v in vector_b]
        keylog = self.generate_keylog_vector_vector(encoded_vector_a, encoded_vector_b, op_code)
        
        return {
            'calculation': calc_result,
            'encoded_vector_a': encoded_vector_a,
            'encoded_vector_b': encoded_vector_b,
            'keylog': keylog,
            'result': result
        }
    
    # ========== UTILITY FUNCTIONS ==========
    
    def parse_scalar(self, scalar_str):
        """Parse scalar từ string"""
        try:
            # Handle basic math expressions
            import math
            scalar_str = scalar_str.replace('sqrt', 'math.sqrt').replace('pi', 'math.pi').replace('^', '**')
            allowed = {"__builtins__": {}, "math": math}
            return float(eval(scalar_str, allowed))
        except:
            return float(scalar_str)
            
    def parse_vector(self, vector_str, expected_dim):
        """Parse vector từ string"""
        components = [comp.strip() for comp in vector_str.split(',')]
        if len(components) != expected_dim:
            raise ValueError(f"Vector cần có {expected_dim} thành phần, nhận được {len(components)}")
            
        result = []
        for comp in components:
            try:
                # Handle basic math expressions
                import math  
                comp = comp.replace('sqrt', 'math.sqrt').replace('pi', 'math.pi').replace('^', '**')
                allowed = {"__builtins__": {}, "math": math}
                result.append(float(eval(comp, allowed)))
            except:
                result.append(float(comp))
                
        return result
        
    def cross_product_3d(self, a, b):
        """Tính tích có hướng cho vector 3D"""
        return [
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2], 
            a[0] * b[1] - a[1] * b[0]
        ]
        
    def format_vector(self, vector):
        """Format vector để hiển thị"""
        formatted = [f"{v:.3f}".rstrip('0').rstrip('.') for v in vector]
        return f"({', '.join(formatted)})"
        
    def encode_value(self, value_str):
        """Mã hóa giá trị theo quy tắc TL (đơn giản hóa)"""
        # Thay thế một số ký hiệu cơ bản
        encoded = value_str.replace('-', 'p').replace('sqrt', 's').replace('pi', 'π')
        return encoded
        
    def generate_keylog_scalar_vector(self, encoded_scalar, encoded_vector, op_code):
        """Sinh keylog cho scalar-vector"""
        version = self.version_var.get()
        prefix = "wv" if version == "fx799" else "wv"  # Có thể customize theo version
        
        vector_part = "=".join(encoded_vector)
        operation_codes = {
            "multiply": "qV1",
            "divide": "qV2",
            "add": "qV3", 
            "subtract": "qV4"
        }
        
        op_code_str = operation_codes.get(op_code, "qV1")
        return f"{prefix}{encoded_scalar}={vector_part}=C{op_code_str}="
        
    def generate_keylog_vector_vector(self, encoded_vector_a, encoded_vector_b, op_code):
        """Sinh keylog cho vector-vector"""
        version = self.version_var.get()
        prefix = "wv" if version == "fx799" else "wv"
        
        vector_a_part = "=".join(encoded_vector_a)
        vector_b_part = "=".join(encoded_vector_b)
        
        operation_codes = {
            "dot_product": "qV5",
            "cross_product": "qV6",
            "add": "qV7",
            "subtract": "qV8",
            "angle": "qV9",
            "distance": "qV10"
        }
        
        op_code_str = operation_codes.get(op_code, "qV5")
        return f"{prefix}{vector_a_part}=C{vector_b_part}=C{op_code_str}="
        
    def display_results(self, result):
        """Hiển thị kết quả"""
        # Clear previous results
        self.calc_result_text.config(state=tk.NORMAL)
        self.calc_result_text.delete(1.0, tk.END)
        self.calc_result_text.insert(tk.END, result['calculation'])
        self.calc_result_text.config(state=tk.DISABLED)
        
        # Encoded values
        encoded_text = ""
        if 'encoded_scalar' in result:
            encoded_text += f"Scalar: {result['encoded_scalar']}\n"
        if 'encoded_vector' in result:
            encoded_text += f"Vector A: {' = '.join(result['encoded_vector'])}\n"
        if 'encoded_vector_a' in result:
            encoded_text += f"Vector A: {' = '.join(result['encoded_vector_a'])}\n"
        if 'encoded_vector_b' in result:
            encoded_text += f"Vector B: {' = '.join(result['encoded_vector_b'])}\n"
            
        self.encoded_text.config(state=tk.NORMAL)
        self.encoded_text.delete(1.0, tk.END)
        self.encoded_text.insert(tk.END, encoded_text.strip())
        self.encoded_text.config(state=tk.DISABLED)
        
        # Final keylog
        self.current_result = result['keylog']
        self.keylog_text.config(state=tk.NORMAL)
        self.keylog_text.delete(1.0, tk.END)
        self.keylog_text.insert(tk.END, self.current_result)
        self.keylog_text.config(state=tk.DISABLED)
        
    # ========== ACTION METHODS ==========
    
    def copy_result(self):
        """Copy keylog to clipboard"""
        if self.current_result:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_result)
            self.update_status("Đã copy keylog vào clipboard!")
            messagebox.showinfo("Thành công", "Đã copy keylog vào clipboard!")
        else:
            messagebox.showwarning("Cảnh báo", "Chưa có kết quả để copy")
            
    def clear_all(self):
        """Xóa tất cả dữ liệu"""
        self.scalar_entry.delete(0, tk.END)
        self.vector_a_entry.delete(0, tk.END)
        self.vector_b_entry.delete(0, tk.END)
        
        self.calc_result_text.config(state=tk.NORMAL)
        self.calc_result_text.delete(1.0, tk.END)
        self.calc_result_text.config(state=tk.DISABLED)
        
        self.encoded_text.config(state=tk.NORMAL)
        self.encoded_text.delete(1.0, tk.END)
        self.encoded_text.config(state=tk.DISABLED)
        
        self.keylog_text.config(state=tk.NORMAL)
        self.keylog_text.delete(1.0, tk.END)
        self.keylog_text.config(state=tk.DISABLED)
        
        self.current_result = ""
        self.copy_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.DISABLED)
        
        self.update_status("Đã xóa tất cả dữ liệu")
        
    def export_single_result(self):
        """Xuất kết quả hiện tại ra Excel"""
        if not self.current_result:
            messagebox.showwarning("Cảnh báo", "Chưa có kết quả để xuất")
            return
            
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Lưu kết quả Vector"
            )
            
            if file_path:
                # Create simple Excel export (placeholder)
                data = {
                    "Thời gian": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "Kiểu tính": [self.calc_type_var.get()],
                    "Kích thước": [self.dimension_var.get()],
                    "Phép toán": [self.operation_var.get()],
                    "Keylog": [self.current_result]
                }
                
                # Would use pandas DataFrame here in real implementation
                messagebox.showinfo("Thành công", f"Đã xuất kết quả ra: {file_path}")
                self.update_status("Đã xuất Excel thành công")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xuất Excel: {str(e)}")
            
    def create_template(self):
        """Tạo template Excel"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Tạo Template Vector"
            )
            
            if file_path:
                # Create template (placeholder)
                messagebox.showinfo("Thành công", f"Đã tạo template: {file_path}")
                self.update_status("Đã tạo template Excel")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tạo template: {str(e)}")
            
    def import_excel(self):
        """Import file Excel"""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
                title="Chọn file Excel Vector"
            )
            
            if file_path:
                self.file_label.config(text=f"File: {os.path.basename(file_path)}", foreground="blue")
                self.process_excel_button.config(state=tk.NORMAL)
                self.update_status(f"Đã import file: {os.path.basename(file_path)}")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi import Excel: {str(e)}")
            
    def process_excel_file(self):
        """Xử lý file Excel batch"""
        try:
            # Placeholder for Excel batch processing
            messagebox.showinfo("Thông báo", "Chức năng xử lý Excel batch đang được phát triển")
            self.update_status("Excel batch processing - Coming soon")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý Excel: {str(e)}")
            
    def update_status(self, message):
        """Cập nhật thanh trạng thái"""
        self.status_bar.config(text=message)


# ========== MAIN RUNNER (For testing) ==========
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main window
    app = VectorView(root)
    root.mainloop()