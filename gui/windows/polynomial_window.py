"""Polynomial window - tương tự PolynomialView của TL."""

import tkinter as tk
from tkinter import messagebox, ttk
import json
import os


class PolynomialWindow:
    """Polynomial Mode window implementation - giống TL PolynomialView."""
    
    def __init__(self, window):
        self.window = window
        
        # Khởi tạo cửa sổ giống TL
        self.window.title("Polynomial Equation Mode")
        self.window.geometry("800x650")
        self.window.configure(bg="#F0F4F8")

        # Biến giống TL
        self._initialize_variables()
        
        # Tạo giao diện giống TL
        self._create_header()
        self._setup_ui()
        self._setup_bindings()

    def _initialize_variables(self):
        """Khởi tạo biến - giống TL"""
        self.degree_var = tk.StringVar(value="2")
        self.variable_var = tk.StringVar(value="x")
        self.operation_var = tk.StringVar(value="Giải nghiệm")
        
        # Trạng thái
        self.polynomial_entered = False
        self.coefficients_entered = False

    def _create_header(self):
        """Tạo header giống TL"""
        COLORS = {"primary": "#9C27B0", "accent": "#E91E63", "text": "#FFFFFF"}
        
        # Header frame
        header_frame = tk.Frame(self.window, bg=COLORS["primary"], height=70)
        header_frame.pack(fill="x", padx=10, pady=5)
        header_frame.pack_propagate(False)
        
        # Logo và title
        title_frame = tk.Frame(header_frame, bg=COLORS["primary"])
        title_frame.pack(side="left", fill="y", padx=15, pady=10)
        
        tk.Label(title_frame, text="📊", font=("Arial", 18),
                bg=COLORS["primary"], fg=COLORS["text"]).pack(side="left")
        tk.Label(title_frame, text="Polynomial Mode", font=("Arial", 16, "bold"),
                bg=COLORS["primary"], fg=COLORS["text"]).pack(side="left", padx=(5, 0))
        
        # Controls giống TL
        controls_frame = tk.Frame(header_frame, bg=COLORS["primary"])
        controls_frame.pack(side="right", fill="y", padx=15, pady=10)
        
        tk.Label(controls_frame, text="Bậc:", bg=COLORS["primary"], 
                fg=COLORS["text"], font=("Arial", 9)).pack(side="left")
        tk.OptionMenu(controls_frame, self.degree_var, "1", "2", "3", "4", "5", "6").pack(side="left", padx=5)
        
        tk.Label(controls_frame, text="Biến:", bg=COLORS["primary"],
                fg=COLORS["text"], font=("Arial", 9)).pack(side="left", padx=(10, 0))
        tk.OptionMenu(controls_frame, self.variable_var, "x", "y", "t").pack(side="left", padx=5)

    def _setup_ui(self):
        """Setup giao diện chính - giống TL"""
        self.main_frame = tk.Frame(self.window, bg="#F0F4F8")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Input methods giống TL
        input_frame = tk.LabelFrame(self.main_frame, text="Nhập đa thức", bg="#FFFFFF")
        input_frame.pack(fill="x", padx=5, pady=5)
        
        # Method 1: Nhập biểu thức giống TL
        expr_frame = tk.Frame(input_frame, bg="#FFFFFF")
        expr_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(expr_frame, text="Biểu thức:", bg="#FFFFFF", font=("Arial", 10)).pack(side="left")
        self.polynomial_entry = tk.Entry(expr_frame, width=40, font=("Arial", 10))
        self.polynomial_entry.pack(side="left", padx=(10, 0), fill="x", expand=True)
        
        tk.Label(input_frame, text="Ví dụ: x^2 + 2*x - 1, 3*x^3 - 4*x^2 + x - 5", 
                bg="#FFFFFF", font=("Arial", 8), fg="#666").pack(padx=10, pady=(0, 5))
        
        # Method 2: Nhập hệ số giống TL
        coeff_frame = tk.LabelFrame(self.main_frame, text="Nhập hệ số (từ bậc cao xuống thấp)", bg="#FFFFFF")
        coeff_frame.pack(fill="x", padx=5, pady=5)
        
        # Coefficient entries
        self.coeff_entries = {}
        coeff_grid = tk.Frame(coeff_frame, bg="#FFFFFF")
        coeff_grid.pack(padx=10, pady=10)
        
        for i, coeff in enumerate(["a6", "a5", "a4", "a3", "a2", "a1", "a0"]):
            col = i % 4
            row = i // 4
            
            tk.Label(coeff_grid, text=f"{coeff}:", bg="#FFFFFF", font=("Arial", 9)).grid(
                row=row*2, column=col, padx=5, pady=2, sticky="w")
            
            entry = tk.Entry(coeff_grid, width=12, font=("Arial", 9))
            entry.grid(row=row*2+1, column=col, padx=5, pady=2)
            self.coeff_entries[coeff] = entry
        
        # Operations giống TL
        op_frame = tk.LabelFrame(self.main_frame, text="Chọn thao tác", bg="#FFFFFF")
        op_frame.pack(fill="x", padx=5, pady=5)
        
        operations = ["Giải nghiệm", "Đạo hàm", "Tích phân", "Tính giá trị", "Phân tích"]
        
        op_grid = tk.Frame(op_frame, bg="#FFFFFF")
        op_grid.pack(padx=10, pady=10)
        
        for i, op in enumerate(operations):
            tk.Radiobutton(op_grid, text=op, variable=self.operation_var, value=op,
                          bg="#FFFFFF", font=("Arial", 9)).grid(row=0, column=i, padx=10, sticky="w")
        
        # Kết quả giống TL
        result_frame = tk.LabelFrame(self.main_frame, text="📄 Kết quả", bg="#FFFFFF")
        result_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.result_text = tk.Text(result_frame, bg="#F8F9FA", font=("Consolas", 10), wrap=tk.WORD)
        self.result_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Action buttons giống TL
        action_frame = tk.Frame(result_frame, bg="#FFFFFF")
        action_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        tk.Button(action_frame, text="🚀 Xử lý", command=self._process_polynomial,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(action_frame, text="💾 Lưu kết quả", command=self._save_result,
                 bg="#2196F3", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        tk.Button(action_frame, text="🗑️ Xóa", command=self._clear_all,
                 bg="#F44336", fg="white", font=("Arial", 10)).pack(side="left", padx=5)

    def _setup_bindings(self):
        """Setup event bindings - giống TL"""
        self.degree_var.trace_add("write", self._on_degree_changed)
        self.variable_var.trace_add("write", self._on_variable_changed)
        self.operation_var.trace_add("write", self._on_operation_changed)

    # Placeholder methods - giống TL structure  
    def _on_degree_changed(self, *args): pass
    def _on_variable_changed(self, *args): pass
    def _on_operation_changed(self, *args): pass
    def _process_polynomial(self): messagebox.showinfo("Xử lý", "Xử lý đa thức sẽ được implement")
    def _save_result(self): messagebox.showinfo("Lưu", "Lưu kết quả sẽ được implement")
    def _clear_all(self):
        self.polynomial_entry.delete(0, tk.END)
        for entry in self.coeff_entries.values():
            entry.delete(0, tk.END)
        self.result_text.delete(1.0, tk.END)
        messagebox.showinfo("Xóa", "Tất cả dữ liệu đã bị xóa")