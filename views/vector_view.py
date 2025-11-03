# Vector View - Giao diện Vector Mode cho ConvertKeylogApp
# Tích hợp với VectorService hoàn chỉnh và fixed values system
# Hỗ trợ 2 kiểu tính: Số thực với Vector và Vector với Vector

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
from services.vector import VectorService, VectorServiceError, VectorValidationError

class VectorView:
    """Giao diện Vector Mode với VectorService integration"""
    
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
        self.current_result = ""
        self.has_result = False
        
        # Initialize VectorService
        try:
            self.vector_service = VectorService()
            self.service_status = "Service Ready"
        except Exception as e:
            self.vector_service = None
            self.service_status = f"Service Error: {str(e)}"
            print(f"Warning: Could not initialize VectorService: {e}")
        
        # Operation mappings (updated with VectorService operations)
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
        
        # Service Status
        self.create_service_status(main_frame)
        
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
        title_label = ttk.Label(header_frame, text="🔢 Vector Calculator & Keylog Generator", 
                               font=("Arial", 14, "bold"))
        title_label.pack()
        
        # Description
        desc_label = ttk.Label(header_frame, 
                              text="Hỗ trợ tính toán vector 2D/3D với số thực hoặc vector khác, tự động sinh keylog TL",
                              font=("Arial", 9))
        desc_label.pack(pady=(5, 0))
        
    def create_service_status(self, parent):
        """Hiển thị trạng thái VectorService"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        status_color = "green" if self.vector_service else "red"
        status_text = f"📊 Service Status: {self.service_status}"
        if self.vector_service:
            service_info = self.vector_service.get_service_info()
            status_text += f" | Fixed Values: {'Loaded' if service_info['fixed_values_loaded'] else 'Default'}"
        
        ttk.Label(status_frame, text=status_text, foreground=status_color, 
                 font=("Arial", 9, "italic")).pack()
        
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
        version_combo.bind("<<ComboboxSelected>>", self.on_version_changed)
        
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
        
        # Encoded Values with Fixed Values Info
        encoded_frame = ttk.Frame(results_frame)
        encoded_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(encoded_frame, text="Giá trị mã hóa + Fixed Values:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.encoded_text = tk.Text(encoded_frame, height=4, width=80, font=("Consolas", 10),
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
        self.status_bar = ttk.Label(self.root, text="Sẵn sàng - Vector Mode v1.0 with VectorService", 
                                   relief=tk.SUNKEN, padding="5")
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
        self.update_service_config()
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
        self.update_service_config()
        self.update_status(f"Đã chuyển sang {dimension}D")
        
    def on_version_changed(self, event=None):
        """Xử lý khi thay đổi phiên bản"""
        self.update_service_config()
        version = self.version_var.get()
        self.update_status(f"Đã chọn phiên bản: {version}")
        
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
    
    def update_service_config(self):
        """Cập nhật cấu hình VectorService"""
        if not self.vector_service:
            return
            
        try:
            calc_type = self.calc_type_var.get()
            dimension = int(self.dimension_var.get())
            version = self.version_var.get()
            
            self.vector_service.set_calculation_type(calc_type)
            self.vector_service.set_dimension(dimension)
            self.vector_service.set_version(version)
            
        except Exception as e:
            print(f"Error updating service config: {e}")
    
    # ========== MAIN PROCESSING ==========
    
    def process_calculation(self):
        """Xử lý tính toán chính với VectorService"""
        try:
            if not self.vector_service:
                messagebox.showerror("Lỗi", "VectorService không sẵn sàng!")
                return
                
            # Validate inputs
            if not self.validate_inputs():
                return
                
            # Update service config
            self.update_service_config()
            
            # Set operation
            operation_name = self.operation_var.get()
            operation_code = self.operations_map[self.calc_type_var.get()][operation_name]
            self.vector_service.set_operation(operation_code)
            
            # Process inputs
            calc_type = self.calc_type_var.get()
            
            if calc_type == "scalar_vector":
                scalar_input = self.scalar_entry.get().strip()
                if not self.vector_service.process_scalar_input(scalar_input):
                    messagebox.showerror("Lỗi", "Không thể xử lý scalar input")
                    return
                    
            vector_a_input = self.vector_a_entry.get().strip()
            if not self.vector_service.process_vector_A(vector_a_input):
                messagebox.showerror("Lỗi", "Không thể xử lý Vector A")
                return
                
            if calc_type == "vector_vector":
                vector_b_input = self.vector_b_entry.get().strip()
                if not self.vector_service.process_vector_B(vector_b_input):
                    messagebox.showerror("Lỗi", "Không thể xử lý Vector B")
                    return
            
            # Process complete workflow
            success, message, result = self.vector_service.process_complete_workflow()
            
            if success:
                # Display results
                self.display_results(result)
                
                # Enable buttons
                self.copy_button.config(state=tk.NORMAL)
                self.export_button.config(state=tk.DISABLED)  # Will enable after Excel integration
                
                self.has_result = True
                self.update_status("Tính toán thành công!")
            else:
                messagebox.showerror("Lỗi", f"Lỗi tính toán: {message}")
                self.update_status("Lỗi tính toán")
                
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
        
    def display_results(self, result):
        """Hiển thị kết quả từ VectorService"""
        # Clear previous results
        self.calc_result_text.config(state=tk.NORMAL)
        self.calc_result_text.delete(1.0, tk.END)
        self.calc_result_text.insert(tk.END, result['calculation_display'])
        self.calc_result_text.config(state=tk.DISABLED)
        
        # Encoded values with fixed values info
        encoded_text = ""
        if result['encoded_scalar']:
            encoded_text += f"Scalar encoded: {result['encoded_scalar']}\n"
        if result['encoded_vector_A']:
            encoded_text += f"Vector A encoded: {' = '.join(result['encoded_vector_A'])}\n"
        if result['encoded_vector_B']:
            encoded_text += f"Vector B encoded: {' = '.join(result['encoded_vector_B'])}\n"
        
        # Fixed value info
        fixed_value_info = result['fixed_value']
        encoded_text += f"Fixed value: {fixed_value_info['fixed_value']} ({fixed_value_info['description']})\n"
            
        self.encoded_text.config(state=tk.NORMAL)
        self.encoded_text.delete(1.0, tk.END)
        self.encoded_text.insert(tk.END, encoded_text.strip())
        self.encoded_text.config(state=tk.DISABLED)
        
        # Final keylog
        self.current_result = result['final_keylog']
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
        
        # Reset service state
        if self.vector_service:
            self.vector_service.reset_state()
        
        self.current_result = ""
        self.has_result = False
        self.copy_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.DISABLED)
        
        self.update_status("Đã xóa tất cả dữ liệu")
        
    def export_single_result(self):
        """Xuất kết quả hiện tại ra Excel (placeholder)"""
        messagebox.showinfo("Thông báo", "Chức năng Export Excel sẽ được bổ sung khi VectorExcelProcessor hoàn thành")
        
    def create_template(self):
        """Tạo template Excel (placeholder)"""
        messagebox.showinfo("Thông báo", "Chức năng tạo Template sẽ được bổ sung")
            
    def import_excel(self):
        """Import file Excel (placeholder)"""
        messagebox.showinfo("Thông báo", "Chức năng Import Excel sẽ được bổ sung")
            
    def process_excel_file(self):
        """Xử lý file Excel batch (placeholder)"""
        messagebox.showinfo("Thông báo", "Chức năng xử lý Excel batch sẽ được bổ sung")
            
    def update_status(self, message):
        """Cập nhật thanh trạng thái"""
        self.status_bar.config(text=message)


# ========== MAIN RUNNER (For testing) ==========
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main window
    app = VectorView(root)
    root.mainloop()